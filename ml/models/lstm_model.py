"""
lstm_model.py

Enhanced LSTM model wrapper for financial time-series prediction.

Improvements over the previous version:
- Per-symbol sequence building (no cross-stock contamination)
- Single scaling point (scaler lives inside model only)
- Symbol-aware fit() and predict()
- Stable architecture with Huber loss
- Early stopping + LR reduction
- Float32 everywhere for speed/memory efficiency

Expected usage:
    model = LSTMModel(window=30)
    model.fit(X_train, y_train, symbols=train_symbols)
    preds, indices = model.predict(X_test, symbols=test_symbols)
"""

import numpy as np
import pandas as pd

from sklearn.preprocessing import StandardScaler

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.losses import Huber
from tensorflow.keras.optimizers import Adam


class LSTMModel:
    """
    LSTM wrapper compatible with the walk-forward training framework.
    """

    def __init__(
        self,
        window=30,
        lstm_units_1=32,
        lstm_units_2=16,
        dense_units=16,
        dropout_rate=0.2,
        epochs=30,
        batch_size=128,
        learning_rate=0.001,
        clip_target=True,
        target_clip_range=(-1.0, 1.0),
        validation_split=0.1
    ):
        # ---------------------------------------------------------
        # Sequence length
        # ---------------------------------------------------------
        self.window = window

        # ---------------------------------------------------------
        # Network architecture
        # ---------------------------------------------------------
        self.lstm_units_1  = lstm_units_1
        self.lstm_units_2  = lstm_units_2
        self.dense_units   = dense_units
        self.dropout_rate  = dropout_rate

        # ---------------------------------------------------------
        # Training settings
        # ---------------------------------------------------------
        self.epochs           = epochs
        self.batch_size       = batch_size
        self.learning_rate    = learning_rate
        self.validation_split = validation_split

        # ---------------------------------------------------------
        # Target smoothing
        # ---------------------------------------------------------
        self.clip_target        = clip_target
        self.target_clip_range  = target_clip_range

        # ---------------------------------------------------------
        # Fitted objects
        # ---------------------------------------------------------
        self.scaler          = StandardScaler()
        self.model           = None
        self.train_indices   = None

    # -------------------------------------------------------------
    # Target smoothing
    # -------------------------------------------------------------
    def smooth_target(self, y):
        """
        Clip extreme target values to reduce training instability.
        """
        y = np.asarray(y, dtype=np.float32)

        if self.clip_target:
            y = np.clip(
                y,
                self.target_clip_range[0],
                self.target_clip_range[1]
            )

        return y

    # -------------------------------------------------------------
    # Per-symbol sequence builder
    # -------------------------------------------------------------
    def build_sequences(self, X, y=None, symbols=None):
        """
        Build rolling LSTM sequences.

        If symbols is provided, sequences are built PER SYMBOL
        to avoid cross-stock contamination.

        If symbols is None, falls back to global sequential
        sequence building (original behavior).

        Parameters
        ----------
        X       : np.ndarray, shape (n_samples, n_features)
        y       : np.ndarray or None
        symbols : np.ndarray of symbol labels or None

        Returns
        -------
        Without y:
            X_seq       : np.ndarray (n_seq, window, n_features)
            indices     : list of original row indices

        With y:
            X_seq       : np.ndarray (n_seq, window, n_features)
            y_seq       : np.ndarray (n_seq,)
            indices     : list of original row indices
        """

        n_features = X.shape[1]

        # ---------------------------------------------------------
        # Per-symbol mode
        # ---------------------------------------------------------
        if symbols is not None:

            all_X_seq  = []
            all_y_seq  = []
            all_idx    = []

            unique_symbols = np.unique(symbols)

            for sym in unique_symbols:

                mask      = symbols == sym
                X_sym     = X[mask]
                idx_sym   = np.where(mask)[0]
                n         = len(X_sym)
                n_seq     = n - self.window

                if n_seq <= 0:
                    # Not enough history for this stock — skip
                    continue

                if y is not None:
                    y_sym = y[mask]

                for i in range(n_seq):
                    all_X_seq.append(X_sym[i : i + self.window])
                    all_idx.append(idx_sym[i + self.window])

                    if y is not None:
                        all_y_seq.append(y_sym[i + self.window])

            # ---------------------------------------------------------
            # Handle empty result
            # ---------------------------------------------------------
            if len(all_X_seq) == 0:
                empty = np.empty(
                    (0, self.window, n_features), dtype=np.float32
                )
                if y is None:
                    return empty, []
                return empty, np.empty((0,), dtype=np.float32), []

            X_seq = np.array(all_X_seq, dtype=np.float32)

            if y is None:
                return X_seq, all_idx

            y_seq = np.array(all_y_seq, dtype=np.float32)
            return X_seq, y_seq, all_idx

        # ---------------------------------------------------------
        # Global mode (fallback — no symbol info)
        # ---------------------------------------------------------
        n_samples  = X.shape[0]
        n_seq      = n_samples - self.window

        if n_seq <= 0:
            empty = np.empty((0, self.window, n_features), dtype=np.float32)
            if y is None:
                return empty, []
            return empty, np.empty((0,), dtype=np.float32), []

        X_seq = np.empty((n_seq, self.window, n_features), dtype=np.float32)

        for i in range(n_seq):
            X_seq[i] = X[i : i + self.window]

        all_idx = list(range(self.window, n_samples))

        if y is None:
            return X_seq, all_idx

        y_seq = np.asarray(y[self.window:], dtype=np.float32)
        return X_seq, y_seq, all_idx

    # -------------------------------------------------------------
    # Build Keras model
    # -------------------------------------------------------------
    def build_model(self, input_shape):
        """
        Build enhanced LSTM network.
        """
        model = Sequential()

        model.add(Input(shape=input_shape))

        # First LSTM layer — keeps full sequence
        model.add(LSTM(self.lstm_units_1, return_sequences=True))
        model.add(Dropout(self.dropout_rate))

        # Second LSTM — compresses sequence into final representation
        model.add(LSTM(self.lstm_units_2))
        model.add(Dropout(self.dropout_rate))

        # Dense head
        model.add(Dense(self.dense_units, activation="relu"))
        model.add(Dense(1))

        optimizer = Adam(
        learning_rate=self.learning_rate,
        clipnorm=1.0
    )

        model.compile(
            optimizer=optimizer,
            loss=Huber()
        )

        return model

    # -------------------------------------------------------------
    # Fit
    # -------------------------------------------------------------
    def fit(self, X, y, symbols=None):
        """
        Fit LSTM model on training fold.

        Parameters
        ----------
        X       : np.ndarray (n_samples, n_features)
        y       : np.ndarray (n_samples,)
        symbols : np.ndarray of symbol labels (optional but recommended)
                Used for per-symbol sequence building.
        """

        X = np.asarray(X, dtype=np.float32)
        y = self.smooth_target(y)

        # ---------------------------------------------------------
        # Scale features
        # Single scaling point — do NOT scale before calling fit()
        # ---------------------------------------------------------
        X_scaled = self.scaler.fit_transform(X).astype(np.float32)

        # ---------------------------------------------------------
        # Build sequences (per symbol if available)
        # ---------------------------------------------------------
        X_seq, y_seq, self.train_indices = self.build_sequences(
            X_scaled, y, symbols=symbols
        )

        if len(X_seq) == 0:
            raise ValueError(
                f"Not enough samples to build sequences "
                f"with window={self.window}. "
                f"Check that training data has sufficient history."
            )

        print(f"  LSTM sequences built: {X_seq.shape}")

        # ---------------------------------------------------------
        # Build model
        # ---------------------------------------------------------
        self.model = self.build_model(
            input_shape=(X_seq.shape[1], X_seq.shape[2])
        )

        # ---------------------------------------------------------
        # Callbacks
        # ---------------------------------------------------------
        early_stopping = EarlyStopping(
            monitor="val_loss",
            patience=5,
            restore_best_weights=True,
            verbose=0
        )

        reduce_lr = ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=2,
            min_lr=1e-5,
            verbose=0
        )

        # ---------------------------------------------------------
        # Train
        # ---------------------------------------------------------

        n_total = len(X_seq)
        n_val = max(1, int(n_total * self.validation_split))
        n_gap = n_val  # Using same size for validation gap to ensure no leakage
        train_end = n_total - n_gap - n_val
        val_start = n_total - n_val

        if train_end <= 0:
            raise ValueError(
                "Not enough sequences after applying validation gap. "
                f"n_total={n_total}, n_gap={n_gap}, n_val={n_val}"
            )

        X_train_seq = X_seq[:train_end]
        y_train_seq = y_seq[:train_end]

        X_val_seq = X_seq[val_start:]
        y_val_seq = y_seq[val_start:]

        print(
            f"  Train seq: {len(X_train_seq)}, "
            f"Gap seq: {n_gap}, "
            f"Val seq: {len(X_val_seq)}"
)

        self.model.fit(
            X_train_seq,
            y_train_seq,
            validation_data=(X_val_seq, y_val_seq),
            epochs=self.epochs,
            batch_size=self.batch_size,
            callbacks=[early_stopping, reduce_lr],
            verbose=0,
            shuffle=False
        )

    # -------------------------------------------------------------
    # Predict
    # -------------------------------------------------------------
    def predict(self, X, symbols=None):
        """
        Predict on test fold.

        Parameters
        ----------
        X       : np.ndarray (n_samples, n_features)
        symbols : np.ndarray of symbol labels (optional but recommended)

        Returns
        -------
        preds         : np.ndarray of predictions
        pred_indices  : list of original row indices aligned to predictions
                        Use these to slice y_test for metric computation.
        """

        if self.model is None:
            raise ValueError("LSTMModel must be fitted before predict().")

        X        = np.asarray(X, dtype=np.float32)

        # ---------------------------------------------------------
        # Use training scaler — do NOT refit on test data
        # ---------------------------------------------------------
        X_scaled = self.scaler.transform(X).astype(np.float32)

        # ---------------------------------------------------------
        # Build test sequences
        # ---------------------------------------------------------
        X_seq, pred_indices = self.build_sequences(
            X_scaled, y=None, symbols=symbols
        )

        if len(X_seq) == 0:
            return np.array([], dtype=np.float32), []

        # ---------------------------------------------------------
        # Predict
        # ---------------------------------------------------------
        preds = self.model.predict(
            X_seq,
            batch_size=self.batch_size,
            verbose=0
        ).flatten().astype(np.float32)

        return preds, pred_indices