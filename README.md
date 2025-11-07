

# Install all dependencies.
- Run `pip install -r requirements-dev.txt`

# How to run app. Using Docker with PostgreSQL.
- Install Docker Desktop
- Run `docker compose up`
- Run `docker compose down` to stop all services

# How to run locally without postgres or docker.
- The project is configured to use SQLite by default for local development.
- Run `uvicorn src.main:app --reload`

# How to run tests.
- Run `pytest` to run all tests

# Documentation

The API documentation is available in two formats:

*   **Swagger UI:** [docs.html](https://sha1kh4.github.io/Quiz-app-Api/docs)
*   **ReDoc:** [redoc.html](https://sha1kh4.github.io/Quiz-app-Api/redoc)


Cheers!
