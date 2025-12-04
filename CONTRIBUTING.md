# Contributing to dj-payfast

We welcome contributions! Here's how to get started.

## Development Setup

1. Fork the repository
2. Clone your fork:
```bash
   git clone https://github.com/your-username/dj-payfast.git
   cd dj-payfast
```

3. Create a virtual environment:
```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
```

4. Install development dependencies:
```bash
   pip install -e ".[dev]"
```

## Running Tests
```bash
pytest
```

## Code Style

We use Black, isort, and flake8:
```bash
black payfast tests
isort payfast tests
flake8 payfast tests
```

## Submitting Changes

1. Create a new branch
2. Make your changes
3. Add tests
4. Run tests and linters
5. Commit and push
6. Create a Pull Request