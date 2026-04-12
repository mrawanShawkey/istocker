from ml.training.walkforward_training import WalkForwardTraining
from ml.models.lstm_model import LSTMModel


def factory():
    return LSTMModel(
        window=30, 
        epochs=30,
        batch_size=128
    )


if __name__ == "__main__":

    trainer = WalkForwardTraining(
        model_factory=factory,
        model_name="lstm"
    )

    trainer.run()