# Contributing to pytest-evals

Thank you for considering contributing to `pytest-evals`! 🎉

Whether you're reporting bugs, improving docs, or suggesting features - every contribution matters and helps make 
testing better for the Python community. No contribution is too small, and we're excited to help you get started!

## Show Us How You Use It!

Share your experiences! Whether it's evaluation patterns, example notebooks, or testing approaches - your real-world 
usage helps others get started. Even a simple write-up of how you use pytest-evals makes a difference! 🚀

## Prerequisites

- Python 3.9 or higher ([python.org/downloads](https://www.python.org/downloads/))
- [uv](https://github.com/astral/uv) for Python package and environment management
- [pre-commit](https://pre-commit.com/) for git hooks management

## Development Setup

1. Clone your fork:
    ```bash
    git clone git@github.com:AlmogBaku/pytest-evals.git
    ```

2. Set up development environment:
    ```bash
    # Install all dependencies including dev extras
    uv sync --all-extras --dev
    
    # Install pre-commit hooks
    pre-commit install
    ```

## Before Submitting a PR

1. Run pre-commit hooks:
    ```bash
    pre-commit run --all-files
    ```

2. Run tests with coverage:
    ```bash
    coverage run --source=pytest_evals -m pytest
    coverage report
    ```

## Testing Guidelines

We value testing to keep pytest-evals reliable and maintainable. When adding new features or fixing bugs:

- Include tests that cover the new functionality or reproduce the bug
- Aim for clear, readable test cases that help document behavior
- Consider edge cases and error conditions
- Use the existing test suite as a guide for style and structure

If you need help with testing, feel free to ask in your PR - we're here to help!

To run the test suite:

```bash
# Run tests with coverage reporting
coverage run --source=pytest_evals -m pytest
coverage report
```

Remember: if you're adding new functionality, including tests helps everyone understand how your code works and ensures
it keeps working as the project evolves. If you're stuck with testing, don't hesitate to ask for help in your PR - we're
here to help!

## PR Process

Individual commits should not be tagged separately, but will generally be assumed to match the PR. For instance, if you
have a bugfix in with a breaking change, it's generally encouraged to submit the bugfix separately, but if you must put
them in one PR, mark the commit separately.

### Commit Message Format

We are using [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) to standardize our commit messages.
This allows us to automatically generate changelogs and release notes, to create a more readable git history and to
automatically trigger semantic versioning.

Please make sure to follow the following format when writing commit messages and PR titles:

```
<type>(<scope>): <short summary>
  │       │             │
  │       │             └─⫸ Summary in present tense
  │       │
  │       └─⫸ [optional] Commit Scope: ipython, eval, analysis, etc.
  │
  └─⫸ Commit Type: build|ci|docs|feat|fix|perf|refactor|test
```

We support the following types:

| Type       | Description                                                           |
|------------|-----------------------------------------------------------------------|
| `feat`     | A new feature (correlates with `MINOR` in semantic versioning)        |
| `fix`      | A bug fix                                                             |
| `docs`     | Documentation only changes                                            |
| `style`    | Changes that do not affect code meaning (whitespace, formatting, etc) |
| `refactor` | Code change that neither fixes a bug nor adds a feature               |
| `perf`     | Code change that improves performance                                 |
| `test`     | Adding or correcting tests                                            |
| `build`    | Changes affecting build system or dependencies                        |
| `ci`       | Changes to CI configuration                                           |
| `chore`    | Other changes that don't modify src or test files                     |

Examples:

```
fix: correct metric calculation in eval_results
feat(core): add support for parallel evaluation runs
refactor!: change the evaluation API
docs(readme): clarify usage instructions
```

### Breaking changes

Breaking changes should be marked with a `!` after the type/scope. This will trigger a `MAJOR` version bump when the
commit is merged. For example:

```
refactor!: change the evaluation API
```

Breaking changes should be avoided if possible. When necessary, they must be properly documented in the PR description
with:

- What changed
- Why it was necessary
- Migration instructions for users

## Where the CI Tests are configured

Check the [GitHub Actions workflows](.github/workflows) directory, particularly:

- `test.yaml` for the main test suite
- `publish.yaml` for the release process
- `pr-triage.yaml` for PR automation

## Code of conduct

Participation in the pytest-evals community is governed by
the [Python Community Code of Conduct](https://www.python.org/psf/conduct/).