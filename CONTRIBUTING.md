# Contributing to THDORA

Thank you for your interest in contributing to THDORA. We welcome community involvement to improve our NLP-driven Telegram bot platform.

## Workflow
1. **Fork** the repository and create your branch from `feature/agent-platform-v2`.
2. **Setup Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Commit Messages**: Follow Conventional Commits.
4. **Testing**: Run pytest before submitting a PR. All tests must pass.
5. **Code Style**: Use ruff for linting and formatting. Ensure type hints are used throughout the codebase (Python 3.12).

## Pull Requests
- PRs must target the `feature/agent-platform-v2` branch.
- Include a clear description of the changes.
- Ensure all new features are covered by tests in `tests/`.
