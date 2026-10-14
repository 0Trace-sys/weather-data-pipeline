
# Weather Data Pipeline

This is my first project as I begin exploring data engineering and building a portfolio of hands-on work.

I've worked with Python and SQL through coursework, but I wanted to start applying those skills outside of the classroom. My goal is to continue learning, gain experience with different technologies, and build a collection of projects on GitHub that shows my progress over time.

For this project, I built a basic ETL (Extract, Transform, Load) pipeline using Python, PostgreSQL, and the Open-Meteo API.

This is the first of several projects I plan to build.

### Project Overview

The pipeline retrieves hourly temperature forecasts for Wichita Falls, Texas, from Open-Meteo. Python processes the API response and loads the data into a PostgreSQL database, where I can use SQL to analyze temperature trends.

The project consists of three main Python scripts:

- `extract.py` — Requests weather data from the API and runs the pipeline.
- `transform.py` — Validates timestamps, handles missing values, and formats the data.
- `load.py` — Inserts new records into PostgreSQL and updates existing forecasts when temperatures change.

I also added logging, API retries, and error handling to make it easier to identify issues when running the pipeline.

### Technologies

Python | PostgreSQL | SQL | REST API | Git

**Python libraries:** Requests, Psycopg 3, python-dotenv

### How the Pipeline Works

Open-Meteo API → Python (Extract) → Python (Transform) → PostgreSQL (Load) → SQL Analysis

The API returns weather forecasts in JSON format. The data is then converted into individual records containing a city, UTC timestamp, and temperature in Fahrenheit.

PostgreSQL uses a unique constraint on the city and forecast timestamp to prevent duplicates. If an existing forecast changes, the pipeline updates the temperature instead of creating another record.

### Data Scope and Limitations

This is a single-city forecast ETL project. Each city/hour retains the latest forecast fetched by the pipeline; new values overwrite earlier predictions. Older forecast hours remain in the table, so the analysis queries summarize all stored records, not just the newest seven-day response.

The table does not preserve forecast versions or collect actual weather observations. It cannot show how predictions changed over time or measure forecast accuracy. Those questions would require forecast snapshots with collection times and a separate observed-weather dataset. The creation and update timestamps describe database writes, not when the weather model issued a forecast.

### SQL Analysis

After loading the data, I wrote SQL queries to review average, minimum, and maximum temperatures, including daily summaries.

One of the initial runs processed 168 hourly forecasts for Wichita Falls.

| Metric | Result |
|---|---|
| Records processed | 168 |
| Average temperature | 68.14°F |
| Lowest forecast | 46.0°F |
| Highest forecast | 92.1°F |

These results are from an October 2026 run and represent forecast data, not actual weather observations.

The SQL queries are available in `sql/analysis.sql`. Daily summaries include `hours_available` so partial dates are visible alongside the temperature statistics. A seven-day UTC response can span eight Central Time dates; an October example has 5 hours on the first date and 19 on the last. Missing temperatures can also reduce coverage. A local day can contain 23 or 25 hours when daylight saving time changes, so 24 is not a universal completeness rule.

### Running the Project

You'll need Python 3, PostgreSQL, and Git installed.

**1. Clone the repository**

```bash
git clone https://github.com/0Trace-sys/weather-data-pipeline.git
cd weather-data-pipeline
```

**2. Create a virtual environment and install dependencies**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

**3. Configure PostgreSQL**

First, make sure your PostgreSQL server is running. The commands below use a macOS/Linux shell and should be run from the repository root.

Copy the example configuration, then edit `.env` to set your database name, existing PostgreSQL user, host, and port:

```bash
cp .env.example .env
```

If your server requires a password, uncomment and set `PGPASSWORD` in `.env`. Both Psycopg and the PostgreSQL command-line tools recognize this setting. Quote values containing spaces or shell-special characters. Keep `.env` private; it is excluded by `.gitignore`. A configured PostgreSQL password file is another option.

Load your local configuration into the current terminal so the setup commands and Python use the same settings:

```bash
set -a
source .env
set +a
```

Create the database (skip this command if it already exists). The configured user needs permission to create a database, or an administrator must create it for that user:

```bash
createdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$DB_NAME"
```

Create the database table:

```bash
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 -f sql/schema.sql
```

Repeat the configuration-loading step when opening a new terminal or changing `.env`. Python also loads `.env` automatically; existing environment variables take precedence.

**4. Run the pipeline**

```bash
python src/extract.py
```

The script retrieves weather forecasts, transforms the data, and inserts or updates records in PostgreSQL.

**5. Run the SQL queries**

```bash
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 -f sql/analysis.sql
```

This displays the forecast record count, temperature statistics, and daily temperature summaries.

### Project Files

- `src/extract.py` — API extraction and pipeline execution
- `src/transform.py` — Data transformation and validation
- `src/load.py` — PostgreSQL database loading
- `sql/schema.sql` — Database schema
- `sql/analysis.sql` — SQL analysis queries
- `tests/tests_transform.py` — Unit tests for data transformation
- `tests/test_load_integration.py` — Optional PostgreSQL loading and SQL coverage tests
- `requirements.txt` — Python dependencies
- `.env.example` — Database configuration template
- `.gitignore` — Files excluded from Git
- `README.md` — Project documentation

### Testing

I added seven unit tests using Python's built-in unittest library to check the data transformation process.

The tests cover valid weather records, missing temperatures, invalid timestamps, empty forecasts, non-finite temperatures, and mismatched timestamp and temperature counts.

Missing temperatures are skipped when usable records remain. Empty or all-missing forecasts and non-finite temperatures (NaN or infinity) raise an error before loading; the pipeline logs the failure and exits with a nonzero status.

To run the seven unit tests:

```bash
python -m unittest discover -s tests -p 'tests_transform.py' -v
```

These tests use sample data and do not require an API connection or a running PostgreSQL database.

Four optional integration tests check inserts and repeat loads, changed forecasts, transaction rollback, and hourly coverage in the daily SQL summaries. They use a dedicated test database and create a temporary schema that is removed afterward. No API connection is required.

With the same connection settings loaded above, create a separate database for these tests (once):

```bash
createdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" weather_pipeline_test
```

Run all eleven tests with an explicit test database connection. The test user must be able to create schemas:

```bash
PGHOST="$DB_HOST" PGPORT="$DB_PORT" PGUSER="$DB_USER" \
WEATHER_TEST_DSN='dbname=weather_pipeline_test' \
python -m unittest discover -s tests -v
```

Without `WEATHER_TEST_DSN`, the four integration tests are skipped and the seven unit tests still run. Database connection failures with `WEATHER_TEST_DSN` set are reported as failures, not skipped tests. Always point this setting at a disposable test database.

**Data source:** [Open-Meteo](https://open-meteo.com/)

