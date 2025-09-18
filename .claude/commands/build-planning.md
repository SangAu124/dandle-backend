You are a senior software architect. Your task is to populate the `PLANNING.md` file in the project's root directory with detailed information based on the project's codebase and the DNA defined in `.claude/README.md`.

Instructions:
1.  Read the content of `.claude/README.md` to understand the project's core principles.
2.  Read the existing `PLANNING.md` file.
3.  Analyze the entire codebase to gather specific details.
4.  Update the `PLANNING.md` file by filling in the 'TBD' sections with accurate and detailed information. Refer to the project's DNA for high-level concepts and to the code for implementation details.

### Sections to fill:

-   **Project Overview**: Briefly describe the project's purpose.
-   **Architecture**: Detail the Clean Architecture layers (Domain, Application, Infrastructure, Interface) as implemented in the project.
-   **Core Components**: Describe the roles of `api`, `core`, `domain`, `infra`, and `services` directories.
-   **Data Model**: Analyze SQLAlchemy models in the `domain` layer to describe the database schema.
-   **API Endpoints**: List and describe the API endpoints defined in the `api` directory.
-   **Technology Stack**: List the technologies from `.claude/README.md` (Python, FastAPI, SQLAlchemy, PostgreSQL, Redis).
-   **Project Structure**: Provide a more detailed view of the project structure from `.claude/README.md`.
-   **Testing Strategy**: Elaborate on the testing strategy (pytest, Testcontainers, etc.) as defined in the DNA.
-   **Development Commands**: Suggest standard commands for building, running tests, and linting (e.g., `pip install`, `pytest`, `black .`, `flake8 .`).
-   **Environment Setup**: Explain how to set up the development environment (e.g., Python version, virtual environment, environment variables).
-   **Development Guidelines**: Reinforce the coding conventions and rules from the DNA (PEP8, snake_case, no fat controllers, etc.).
-   **Security Considerations**: Mention the security rules from the DNA (no hardcoded secrets, use of environment variables).
-   **Future Considerations**: Suggest potential future improvements based on the current architecture (e.g., replacing AWS Rekognition with a custom model).

After updating the file, present the new content of `PLANNING.md` to the user.
