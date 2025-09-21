# Configuration Guide

## Environment Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file in your project root:

```env
# GitHub Authentication
GITHUB_TOKEN=ghp_your_token_here

# GitLab Authentication  
GITLAB_TOKEN=glpat_your_token_here
GITLAB_URL=https://gitlab.com

# Bitbucket Authentication
BITBUCKET_USERNAME=your_username
BITBUCKET_APP_PASSWORD=your_app_password

# AI Services (Optional)
OPENAI_API_KEY=sk-your_openai_key
ANTHROPIC_API_KEY=sk-ant-your_anthropic_key
```

### 3. Verify Installation

```bash
pr-review config
```

## Provider Configuration

### GitHub

1. Go to GitHub Settings > Developer settings > Personal access tokens
2. Generate a new token with `repo` scope
3. Set `GITHUB_TOKEN` environment variable

### GitLab

1. Go to GitLab > User Settings > Access Tokens
2. Create a token with `api` scope
3. Set `GITLAB_TOKEN` and optionally `GITLAB_URL` for self-hosted instances

### Bitbucket

1. Go to Bitbucket Settings > App passwords
2. Create a new app password with `Repositories: Read` and `Pull requests: Write` permissions
3. Set `BITBUCKET_USERNAME` and `BITBUCKET_APP_PASSWORD`

## Analysis Configuration

### Basic Configuration

```python
from pr_review_agent.core.models import AnalysisConfig, IssueSeverity

config = AnalysisConfig(
    enable_pylint=True,
    enable_flake8=True,
    enable_black=True,
    enable_mypy=True,
    enable_bandit=True,
    enable_safety=True,
    severity_threshold=IssueSeverity.MEDIUM
)
```

### Advanced Configuration

```python
config = AnalysisConfig(
    # Code Quality Tools
    enable_pylint=True,
    enable_flake8=True,
    enable_black=True,
    enable_mypy=True,
    
    # Security Tools
    enable_bandit=True,
    enable_safety=True,
    
    # AI Analysis
    enable_ai_analysis=True,
    ai_provider="openai",  # or "anthropic"
    
    # Filtering
    severity_threshold=IssueSeverity.HIGH,
    max_issues_per_file=25,
    
    # Custom Rules
    custom_rules=["custom-rule-1", "custom-rule-2"]
)
```

## CLI Configuration

### Command Line Options

```bash
# Basic review
pr-review review --provider github --repo owner/repo --pr 123

# With AI suggestions
pr-review review --provider github --repo owner/repo --pr 123 --ai-suggestions

# Post comments on PR
pr-review review --provider github --repo owner/repo --pr 123 --post-comments

# Custom severity threshold
pr-review review --provider github --repo owner/repo --pr 123 --severity-threshold high

# Disable specific tools
pr-review review --provider github --repo owner/repo --pr 123 --disable-tools pylint --disable-tools mypy

# JSON output
pr-review review --provider github --repo owner/repo --pr 123 --output-format json
```

### Configuration File

Create a `pr-review.yaml` file in your project root:

```yaml
defaults:
  provider: github
  severity_threshold: medium
  ai_suggestions: true
  post_comments: false

analyzers:
  pylint:
    enabled: true
    options: "--disable=C0114,C0116"
  flake8:
    enabled: true
    max_line_length: 88
  black:
    enabled: true
  mypy:
    enabled: true
  bandit:
    enabled: true
    severity: medium
  safety:
    enabled: true

ai:
  provider: openai
  model: gpt-3.5-turbo
  max_tokens: 1000
```

## CI/CD Configuration

### GitHub Actions

```yaml
name: PR Review
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: |
          pr-review review \
            --provider github \
            --repo ${{ github.repository }} \
            --pr ${{ github.event.pull_request.number }} \
            --ai-suggestions \
            --post-comments
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

### GitLab CI

```yaml
pr-review:
  stage: review
  image: python:3.9
  script:
    - pip install -r requirements.txt
    - pr-review review --provider gitlab --repo $CI_PROJECT_PATH --pr $CI_MERGE_REQUEST_IID
  only:
    - merge_requests
  variables:
    GITLAB_TOKEN: $GITLAB_TOKEN
```

### Bitbucket Pipelines

```yaml
pipelines:
  pull-requests:
    '**':
      - step:
          name: PR Review
          image: python:3.9
          script:
            - pip install -r requirements.txt
            - pr-review review --provider bitbucket --repo $BITBUCKET_REPO_FULL_NAME --pr $BITBUCKET_PR_ID
          services:
            - python
```

## Custom Rules

### Creating Custom Analyzers

```python
from pr_review_agent.analyzers.base import CodeAnalyzer
from pr_review_agent.core.models import CodeIssue, IssueSeverity, IssueCategory

class BusinessRuleAnalyzer(CodeAnalyzer):
    def analyze(self, file_path: str, content: str) -> List[CodeIssue]:
        issues = []
        # Your custom analysis logic
        return issues
    
    def should_analyze(self, file_path: str) -> bool:
        return file_path.endswith('.py')
    
    def get_name(self) -> str:
        return "Business Rules"
```

### Adding Custom Rules to Agent

```python
from pr_review_agent import PRReviewAgent

agent = PRReviewAgent()
agent.analyzers.append(BusinessRuleAnalyzer(config))
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify tokens are correctly set
   - Check token permissions
   - Ensure repository access

2. **Analysis Tool Errors**
   - Install missing tools: `pip install pylint flake8 black mypy bandit safety`
   - Check tool versions compatibility

3. **AI Analysis Not Working**
   - Verify API keys are set
   - Check API quota and limits
   - Ensure internet connectivity

4. **Performance Issues**
   - Reduce `max_issues_per_file`
   - Disable heavy analyzers for large PRs
   - Use severity filtering

### Debug Mode

Enable debug logging:

```bash
export PR_REVIEW_DEBUG=1
pr-review review --provider github --repo owner/repo --pr 123
```

### Verbose Output

```bash
pr-review review --provider github --repo owner/repo --pr 123 --output-format json | jq .
```
