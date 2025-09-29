# Clean Architecture Template

What's included in the template?

- Domain layer with sample entities.
- Application layer with abstractions for:
  - Example use cases
  - Cross-cutting concerns (logging, validation)
- Infrastructure layer with:
  - Authentication
  - SQLAlchemy with SQLite for local development and PostgreSQL for Docker.
  - Rate limiting on registration
- Testing projects
  - Pytest unit tests
  - Pytest integration tests (e2e tests)

I'm open to hearing your feedback about the template and what you'd like to see in future iterations. DM me on LinkedIn or email me.

--

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

*   **Swagger UI:** [docs.html](./docs.html)
*   **ReDoc:** [redoc.html](./redoc.html)


Cheers!