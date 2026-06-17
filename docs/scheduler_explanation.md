# Scheduler Explanation

This document explains `api/jobs/scheduler.py` in beginner-friendly terms. It describes what the scheduler is intended to do today, what it depends on, and what looks risky or incomplete.

## Simple Overview

`api/jobs/scheduler.py` is meant to run a daily market-data pipeline automatically.

At 01:00 every day, APScheduler should call `daily_pipeline()`. That pipeline:

1. Fetches one day of EGX market data from TradingView.
2. Combines the per-stock CSV files into one daily CSV.
3. Inserts the daily prices into the database.
4. Loads the production XGBoost model and runs predictions.
5. Creates recommendation-set containers for Conservative, Moderate, and Aggressive users.
6. Starts recommendation selection logic, although that final part is not implemented yet.

Important: this file defines `schedule()`, but current repository search did not find another file calling it. If nothing calls `schedule()`, the daily job will never start.

## Step-by-Step Flow

### 1. Module import

When Python imports `api/jobs/scheduler.py`, it immediately:

- Adds the current project root to `sys.path`.
- Imports project paths such as `MARKET_DIR`, `XGB_MODEL`, and `XGB_MODEL_META`.
- Imports the Flask app factory and SQLAlchemy database object.
- Imports ORM models and repository helper functions.
- Creates a Flask app with `app = create_app()`.
- Creates a TradingView client with `tv = TvDatafeed()`.
- Sets `combined_file_path` to `data/market_data/daily/EGX30_Full_Dataset_Ready.csv`.

### 2. Scheduler startup

The `schedule()` function creates an APScheduler `BackgroundScheduler`.

It registers this job:

```python
scheduler.add_job(func=daily_pipeline, trigger='cron', hour=1, minute=0)
```

Then it starts the scheduler thread with:

```python
scheduler.start()
```

This means the scheduler runs in the same Python process. It is not a separate worker service.

### 3. Cron trigger

The trigger is a cron trigger:

- `hour=1`
- `minute=0`

So the job is intended to run every day at 01:00.

No timezone is configured in this file. APScheduler will use its default/local timezone. That should be made explicit before production use.

### 4. Job execution

At the scheduled time, APScheduler calls `daily_pipeline()`.

`daily_pipeline()` opens a Flask application context:

```python
with app.app_context():
```

This is required because the job is not running inside a normal Flask request. Without the app context, database access through Flask-SQLAlchemy can fail.

Then it runs these steps in order:

1. `daily_market_update()`
2. `daily_predictions(daily_data)`
3. `daily_recommendation_sets(latest_date)`
4. `daily_recommendations(latest_date)`

If any step raises an exception, `daily_pipeline()` catches it and prints an error message.

## Jobs Registered By The Scheduler

Only one APScheduler job is registered.

| Job function | Trigger | When it runs | Purpose |
| --- | --- | --- | --- |
| `daily_pipeline` | `cron` | Every day at 01:00 local/default scheduler time | Run the full market update, prediction, and recommendation pipeline |

There are no interval triggers and no date triggers in this file.

## What Each Function Does

### `daily_market_update()`

Purpose:

- Fetch daily EGX market data from TradingView.
- Combine per-ticker CSV files into one daily CSV.
- Delete the individual raw files after combining.
- Insert daily stock prices into the database.

Depends on:

- TradingView access through `tvDatafeed`.
- `data/market_data/daily` directory.
- `preprocessing.market_processing.fetch_market_data`.
- Flask application context.
- SQLAlchemy database session.
- `stocks` table already populated.
- Expected CSV columns such as `date`, `symbol` or `ticker`, `open`, `high`, `low`, `close`, and `volume`.

Side effects:

- Creates CSV files.
- Deletes raw per-ticker CSV files.
- Inserts `StockPrice` rows.
- Commits or rolls back the database session.

### `daily_predictions(daily_data)`

Purpose:

- Load the production XGBoost model.
- Load model metadata.
- Read the combined daily CSV.
- Build the model feature matrix.
- Run predictions.
- Attempt to save predictions.
- Delete the combined daily CSV.

Depends on:

- `XGB_MODEL`: `data/ml_data/metadata/walkforward_results/xgboost_production.pkl`
- `XGB_MODEL_META`: `data/ml_data/metadata/walkforward_results/xgboost_production_meta.json`
- The metadata file containing `features` and `medians`.
- The daily CSV containing all required feature columns.
- Database session if predictions are saved.

Side effects:

- Reads model files.
- Reads and deletes the combined daily CSV.
- Attempts database writes.

### `daily_recommendation_sets(latest_date)`

Purpose:

- Create recommendation-set containers for:
  - `Conservative`
  - `Moderate`
  - `Aggressive`

Depends on:

- `RecommendationSet` model.
- Database session.
- A usable date value.

Side effects:

- Inserts `RecommendationSet` rows.
- Commits or rolls back the database session.

### `daily_recommendations(latest_date)`

Purpose:

- Intended to choose stocks to recommend using predicted returns and risk level.

Current state:

- Reads predicted returns.
- Reads all stocks.
- Reads latest recommendation sets.
- Defines a risk-category-to-risk-level map.
- Does not yet create `Recommendation` rows because the selection loop is commented out.

Depends on:

- Predictions existing for the target date.
- Stocks existing in the database.
- Recommendation sets existing.

### `daily_pipeline()`

Purpose:

- Orchestrate the whole daily workflow inside a Flask app context.

Depends on:

- All dependencies of the child functions.
- `app = create_app()` having succeeded at import time.

Side effects:

- Runs the full pipeline.
- Catches exceptions and prints an error.

### `schedule()`

Purpose:

- Create and start the in-process APScheduler.
- Register `daily_pipeline()` as the daily cron job.

Depends on:

- `apscheduler` package being installed.
- The process staying alive.
- Some application startup code calling `schedule()`.

Side effects:

- Starts a background scheduler thread.

## External Services And Requirements

This scheduler expects:

- A database configured through Flask-SQLAlchemy.
- `DATABASE_URL` environment variable, or fallback SQLite database `sqlite:///./database.db`.
- `SECRET_KEY` environment variable for Flask JWT config, although scheduler work does not directly use JWT.
- TradingView access through `tvDatafeed`.
- Model artifacts on disk:
  - `xgboost_production.pkl`
  - `xgboost_production_meta.json`
- Market-data directories on disk, especially:
  - `data/market_data/daily`
- Flask app setup from `api.app.create_app`.
- APScheduler for background scheduling.

Redis and Celery are not used by this file. If the project later uses Celery, this scheduler would need a different architecture.

## Dependency Check

The file imports:

```python
from apscheduler.schedulers.background import BackgroundScheduler
```

But `environment.yml` currently lists:

```yaml
- flask-scheduler==0.0.51
```

It does not obviously list `apscheduler` directly. `flask-scheduler` may or may not install the needed APScheduler package transitively. For reliability, `apscheduler` should be listed explicitly if this file is used.

## What Is Missing Or Risky

### Scheduler may not start

Repository search found `schedule()` defined in `api/jobs/scheduler.py`, but did not find a place where it is called.

If nothing calls:

```python
schedule()
```

then no jobs will run.

### Jobs may duplicate on reload or multiple workers

`BackgroundScheduler` runs inside the current process.

If Flask debug reload starts two processes, or a production server runs multiple workers, each process that calls `schedule()` may run its own copy of the daily job. That can duplicate downloads, database inserts, predictions, and recommendation sets.

### Timezone is not explicit

The cron trigger runs at 01:00 in APScheduler's default/local timezone. The file does not say whether that should be Africa/Cairo, UTC, or something else.

### `latest_date` is probably wrong

The file has:

```python
latest_date = get_latest_date
```

That assigns the function object, not the result of calling the function.

Later it passes `latest_date` into recommendation functions. That means those functions may receive a function object instead of an actual date.

It probably should be called at the correct point in the pipeline, but that is a logic fix and was not changed here.

### `RecommendationSet.date` does not exist

`daily_recommendation_sets()` queries:

```python
RecommendationSet.date == latest_date
```

But the current `RecommendationSet` model has `created_at`, not `date`.

That query may fail.

### Prediction rows are not built correctly yet

`daily_predictions()` does:

```python
raw_preds = model.predict(X)
db.session.add_all(raw_preds)
```

Model predictions are usually raw numbers or a NumPy array, not SQLAlchemy `Prediction` objects. SQLAlchemy normally expects ORM model instances.

This probably needs code that maps each prediction to a stock/date and creates `Prediction(...)` rows.

### Ticker lookup may use the wrong key

`daily_market_update()` strips `EGX:` from symbols into `ticker_symbol`, but then inserts with:

```python
stock_id = stock_map[row['symbol']]
```

If `row['symbol']` is `EGX:COMI` and the database stores `COMI`, this can raise `KeyError`.

### Exceptions are mostly printed, not logged

The file uses `print()` instead of the Python `logging` module. That makes production monitoring harder.

Some messages also miss f-string formatting, for example:

```python
print('Error: {e}')
```

This prints `{e}` literally instead of the actual error.

### Database session cleanup is limited

The code commits or rolls back in several places, but it does not explicitly close or remove the session at the end of the job. Flask-SQLAlchemy usually handles request teardown for web requests, but scheduler jobs are outside request handling.

### Recommendation generation is incomplete

`daily_recommendations()` does not insert final recommendations yet.

### Tests were not found

Repository search did not find tests for these scheduled functions.

## Common Scheduler Issues Checklist

| Issue | Current status |
| --- | --- |
| Is the scheduler actually started anywhere? | Not found in repository search. |
| Are jobs duplicated on app reload? | Possible if `schedule()` is called during Flask reload or in multiple workers. |
| Are timezone settings clear? | No. The cron timezone is implicit. |
| Are environment variables documented? | Partly. `DATABASE_URL` and `SECRET_KEY` are in `api/config.py`, but scheduler-specific docs were missing before this document. |
| Are database sessions safely opened/closed? | App context is used, commits/rollbacks exist, but explicit scheduler-session cleanup is not present. |
| Is logging enough? | No. It uses `print()` and some error messages do not interpolate exceptions. |
| Are exceptions inside jobs handled? | Some are caught. The outer pipeline catches all exceptions, which may hide failed jobs from APScheduler. |
| Does it work with multiple workers? | Risky. Each worker can run its own scheduler. |
| Are dependencies included? | `flask-scheduler` is listed, but direct `apscheduler` is not obvious. |
| Are there tests for scheduled jobs? | Not found. |

## How To Run Or Test Locally

### 1. Check syntax

```bash
python3 -m py_compile api/jobs/scheduler.py
```

### 2. Check that APScheduler imports

```bash
python3 -c "from apscheduler.schedulers.background import BackgroundScheduler; print('apscheduler ok')"
```

### 3. Run the pipeline manually

Use this only when you are ready for real side effects: it can call TradingView, create/delete CSV files, and write to the database.

```bash
python3 -c "from api.jobs.scheduler import daily_pipeline; daily_pipeline()"
```

### 4. Start the scheduler manually

This starts the background scheduler in the current Python process. The process must stay alive.

```bash
python3 -c "from api.jobs.scheduler import schedule; schedule(); import time; time.sleep(120)"
```

This command only waits two minutes, so it will not execute the daily job unless the current time reaches 01:00 during that window. It is mainly useful to check that scheduler startup does not crash.

### 5. Test individual functions

For safer testing, mock or monkeypatch external calls:

- Mock `Extract.fetch_tv_data`.
- Mock `Extract.fetch_with_retries`.
- Use a temporary daily CSV.
- Use a test database.
- Mock `joblib.load` and model predictions.

## Suggested Fixes To Consider Later

These are recommended, but not applied in this documentation-only change:

1. Call `schedule()` from a clear startup location, or move scheduled work to a dedicated worker process.
2. Configure an explicit timezone, probably `Africa/Cairo` or UTC.
3. Add a stable job id and `replace_existing=True`.
4. Prevent duplicate jobs in multi-worker deployments.
5. Replace `print()` with structured logging.
6. Fix `latest_date = get_latest_date` so the code passes an actual date.
7. Fix `RecommendationSet.date` usage or add the intended model column.
8. Convert model outputs into real `Prediction` ORM objects before calling `db.session.add_all`.
9. Use the stripped `ticker_symbol` for `stock_map` lookup.
10. Add tests for each function with mocked TradingView, file system, model, and database behavior.
