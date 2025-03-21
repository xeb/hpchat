# HPChat Development Guidelines

## Build & Run Commands
- `make setup`: Install project in development mode
- `make server`: Start the web server
- `make process`: Preprocess video data and sermon listings
- `make chat`: Launch chat session CLI
- `make shell`: Start debug shell
- `make transcribe`: Transcribe all videos
- `make clean`: Remove build artifacts

## Code Style Guidelines
- **Imports**: Standard imports at top, grouped by stdlib, third-party, local
- **Formatting**: 4-space indentation, max line length 88 characters
- **Naming**: snake_case for variables/functions, CamelCase for classes
- **Types**: Use type hints for function parameters and return values
- **Documentation**: Docstrings for all public functions and classes
- **Error Handling**: Use try/except blocks with specific exception classes
- **CLI Tools**: Use the `fire` library for command-line interfaces
- **Database**: Use `psycopg2` with parameterized queries for Postgres

## Project Structure
- `/hpchat`: Main package source code
- `/sermons`: Source sermon text files
- `/output`: Processed output files
- `/spiders`: Web crawlers for data collection

This project is a Flask-based web application with CLI tools for processing sermon content.