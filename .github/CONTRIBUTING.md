# Contributing to Turnitout

Thank you for your interest in contributing to Turnitout! Community contributions are welcomed to improve similarity reduction algorithms, add new synonym dictionaries, or enhance developer experience.

## Code of Conduct

By participating in this project, compliance with the [Code of Conduct](CODE_OF_CONDUCT.md) is required.

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Git

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/AhmadHassan-BTed/Turnitout.git
   cd Turnitout
   ```

2. Set up a virtual environment:
   ```bash
   python -m venv env
   # On Windows:
   env\Scripts\activate
   # On macOS/Linux:
   source env/bin/activate
   ```

3. Install dependencies in editable mode:
   ```bash
   pip install -e .[dev]
   ```

## Development Workflow

### Coding Standards
Standard PEP 8 formatting rules are followed.
- Run `black --check src/ tests/` to verify code formatting.
- Run `flake8 src/ tests/` to perform lint checks.

### Running Tests
Before opening a Pull Request, verify that all tests pass:
```bash
pytest
```

## Pull Request Guidelines

1. **Create a branch**: Create your feature or bugfix branch off of `main`:
   ```bash
   git checkout -b feature/my-new-feature
   ```
2. **Commit Conventions**: Use descriptive semantic commit messages (e.g. `feat: add support for nested subheads`, `fix: correct unmatched braces in equation zones`).
3. **Write Tests**: If adding features or changing behavior, ensure to write corresponding unit tests inside the `tests/` folder.
4. **Push & Open PR**: Push to your branch and open a Pull Request. Ensure that all checks (format, lint, tests) pass on GitHub Actions.
