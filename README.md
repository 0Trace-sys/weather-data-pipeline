
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

The SQL queries are available in `sql/analysis.sql`.

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

First, make sure your PostgreSQL server is running.

Create a database named `weather_pipeline`:

```bash
createdb weather_pipeline
```

Copy `.env.example` to `.env` and update the connection settings for your local PostgreSQL installation:

```bash
cp .env.example .env
```

Create the database table:

```bash
psql -d weather_pipeline -v ON_ERROR_STOP=1 -f sql/schema.sql
```

**4. Run the pipeline**

```bash
python src/extract.py
```

The script retrieves weather forecasts, transforms the data, and inserts or updates records in PostgreSQL.

**5. Run the SQL queries**

```bash
psql -d weather_pipeline -v ON_ERROR_STOP=1 -f sql/analysis.sql
```

This displays the forecast record count, temperature statistics, and daily temperature summaries.

### Project Files

- `src/extract.py` — API extraction and pipeline execution
- `src/transform.py` — Data transformation and validation
- `src/load.py` — PostgreSQL database loading
- `sql/schema.sql` — Database schema
- `sql/analysis.sql` — SQL analysis queries
- `tests/tests_transform.py` — Unit tests for data transformation
- `requirements.txt` — Python dependencies
- `.env.example` — Database configuration template
- `.gitignore` — Files excluded from Git
- `README.md` — Project documentation

### Testing

I added seven unit tests using Python's built-in unittest library to check the data transformation process.

The tests cover valid weather records, missing temperatures, invalid timestamps, empty forecasts, non-finite temperatures, and mismatched timestamp and temperature counts.

Missing temperatures are skipped when usable records remain. Empty or all-missing forecasts and non-finite temperatures (NaN or infinity) raise an error before loading; the pipeline logs the failure and exits with a nonzero status.

To run the tests:

```bash
python -m unittest discover -s tests -v
```

These tests use sample data and do not require an API connection or a running PostgreSQL database.

**Data source:** [Open-Meteo](https://open-meteo.com/)
