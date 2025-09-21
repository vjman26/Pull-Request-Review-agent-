# PR Review Agent

A comprehensive Python-based pull request review agent that supports multiple git servers and provides intelligent code analysis and feedback.

## Features

### Core Features
- **Multi-server Support**: GitHub, GitLab, and Bitbucket integration
- **Code Quality Analysis**: Automated checks for code quality, standards, and potential issues
- **Feedback Generation**: Structured feedback on code structure, readability, and bugs
- **Modular Architecture**: Extensible design for easy customization

### Advanced Features
- **AI-driven Suggestions**: Performance, readability, and security improvements using AI
- **Inline Review Comments**: GitHub/GitLab style inline comments
- **CI/CD Integration**: Automated reviews before merging
- **Scoring System**: Quantitative PR quality evaluation
- **Security Analysis**: Vulnerability detection and security best practices

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```bash
# Review a PR from GitHub
pr-review --provider github --repo owner/repo --pr 123

# Review with AI suggestions
pr-review --provider github --repo owner/repo --pr 123 --ai-suggestions

# CI/CD integration
pr-review --provider gitlab --repo owner/repo --pr 456 --ci-mode
```

## Configuration

Create a `.env` file in your project root:

```env
# GitHub
GITHUB_TOKEN=your_github_token

# GitLab
GITLAB_TOKEN=your_gitlab_token
GITLAB_URL=https://gitlab.com

# Bitbucket
BITBUCKET_USERNAME=your_username
BITBUCKET_APP_PASSWORD=your_app_password

# AI Services (optional)
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

## Usage

### Command Line Interface

```bash
# Basic usage
pr-review --provider <provider> --repo <owner/repo> --pr <number>

# With options
pr-review --provider github --repo microsoft/vscode --pr 1234 --ai-suggestions --output-format json
```

### Python API

```python
from pr_review_agent import PRReviewAgent

agent = PRReviewAgent()
result = agent.review_pr(
    provider="github",
    repo="owner/repo",
    pr_number=123,
    ai_suggestions=True
)
```

## Supported Providers

- **GitHub**: Full API support with authentication
- **GitLab**: Self-hosted and GitLab.com support
- **Bitbucket**: Cloud and Server support

## Code Analysis

The agent performs comprehensive analysis including:

- **Code Quality**: Pylint, Flake8, Black formatting
- **Type Checking**: MyPy static analysis
- **Security**: Bandit security scanning
- **Dependencies**: Safety vulnerability checks
- **Performance**: AI-driven performance suggestions
- **Readability**: Code complexity and maintainability metrics

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details
