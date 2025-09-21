# PR Review Agent API Documentation

## Core Classes

### PRReviewAgent

The main class for reviewing pull requests.

```python
from pr_review_agent import PRReviewAgent
from pr_review_agent.core.models import AnalysisConfig, IssueSeverity

# Create configuration
config = AnalysisConfig(
    enable_ai_analysis=True,
    severity_threshold=IssueSeverity.MEDIUM
)

# Create agent
agent = PRReviewAgent(config)

# Review a PR
result = agent.review_pr(
    provider="github",
    repo="owner/repo",
    pr_number=123,
    post_comments=False
)
```

#### Methods

##### `review_pr(provider, repo, pr_number, post_comments=False)`

Review a pull request and return analysis results.

**Parameters:**
- `provider` (str): Git server provider ("github", "gitlab", "bitbucket")
- `repo` (str): Repository in format "owner/repo"
- `pr_number` (int): Pull request number
- `post_comments` (bool): Whether to post comments on the PR

**Returns:** `PRReviewResult` object

### AnalysisConfig

Configuration class for customizing analysis behavior.

```python
config = AnalysisConfig(
    enable_pylint=True,
    enable_flake8=True,
    enable_black=True,
    enable_mypy=True,
    enable_bandit=True,
    enable_safety=True,
    enable_ai_analysis=False,
    ai_provider="openai",
    severity_threshold=IssueSeverity.MEDIUM,
    max_issues_per_file=50
)
```

#### Parameters

- `enable_pylint` (bool): Enable Pylint analysis
- `enable_flake8` (bool): Enable Flake8 analysis
- `enable_black` (bool): Enable Black formatter checks
- `enable_mypy` (bool): Enable MyPy type checking
- `enable_bandit` (bool): Enable Bandit security analysis
- `enable_safety` (bool): Enable Safety dependency checks
- `enable_ai_analysis` (bool): Enable AI-powered analysis
- `ai_provider` (str): AI provider ("openai" or "anthropic")
- `severity_threshold` (IssueSeverity): Minimum severity to report
- `max_issues_per_file` (int): Maximum issues per file

### Data Models

#### PRReviewResult

Complete result of a PR review.

```python
class PRReviewResult:
    pr_info: PRInfo
    feedback: ReviewFeedback
    analysis_duration: float
    provider: str
    timestamp: datetime
    metadata: Dict[str, Any]
```

#### ReviewFeedback

Feedback generated for a pull request.

```python
class ReviewFeedback:
    overall_score: float  # 0-10
    summary: str
    issues: List[CodeIssue]
    suggestions: List[str]
    strengths: List[str]
    ai_insights: Optional[Dict[str, Any]]
    metrics: Dict[str, Any]
```

#### CodeIssue

Individual code issue found during analysis.

```python
class CodeIssue:
    file_path: str
    line_number: int
    column_number: Optional[int]
    severity: IssueSeverity  # low, medium, high, critical
    category: IssueCategory  # bug, security, performance, etc.
    message: str
    rule_id: Optional[str]
    suggestion: Optional[str]
    code_snippet: Optional[str]
```

## Providers

### GitHubProvider

```python
from pr_review_agent.providers import GitHubProvider

provider = GitHubProvider(token="your_token")
pr_info = provider.get_pr_info("owner/repo", 123)
```

### GitLabProvider

```python
from pr_review_agent.providers import GitLabProvider

provider = GitLabProvider(token="your_token", base_url="https://gitlab.com")
pr_info = provider.get_pr_info("owner/repo", 123)
```

### BitbucketProvider

```python
from pr_review_agent.providers import BitbucketProvider

provider = BitbucketProvider(username="user", password="app_password")
pr_info = provider.get_pr_info("owner/repo", 123)
```

## Custom Analyzers

Create custom analyzers by extending the `CodeAnalyzer` base class:

```python
from pr_review_agent.analyzers.base import CodeAnalyzer
from pr_review_agent.core.models import CodeIssue, IssueSeverity, IssueCategory

class CustomAnalyzer(CodeAnalyzer):
    def analyze(self, file_path: str, content: str) -> List[CodeIssue]:
        # Your analysis logic here
        return issues
    
    def should_analyze(self, file_path: str) -> bool:
        return file_path.endswith('.py')
    
    def get_name(self) -> str:
        return "Custom Analyzer"
```

## Environment Variables

Set these environment variables for authentication and AI features:

```bash
# GitHub
GITHUB_TOKEN=your_github_token

# GitLab
GITLAB_TOKEN=your_gitlab_token
GITLAB_URL=https://gitlab.com

# Bitbucket
BITBUCKET_USERNAME=your_username
BITBUCKET_APP_PASSWORD=your_app_password

# AI Services
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```
