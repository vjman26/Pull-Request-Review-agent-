"""Data models for the PR Review Agent."""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class IssueSeverity(str, Enum):
    """Severity levels for code issues."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IssueCategory(str, Enum):
    """Categories of code issues."""
    BUG = "bug"
    SECURITY = "security"
    PERFORMANCE = "performance"
    READABILITY = "readability"
    STYLE = "style"
    COMPLEXITY = "complexity"
    MAINTAINABILITY = "maintainability"


class CodeIssue(BaseModel):
    """Represents a code issue found during analysis."""
    file_path: str
    line_number: int
    column_number: Optional[int] = None
    severity: IssueSeverity
    category: IssueCategory
    message: str
    rule_id: Optional[str] = None
    suggestion: Optional[str] = None
    code_snippet: Optional[str] = None


class ReviewFeedback(BaseModel):
    """Feedback generated for a pull request."""
    overall_score: float = Field(ge=0.0, le=10.0, description="Overall PR quality score")
    summary: str
    issues: List[CodeIssue] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    ai_insights: Optional[Dict[str, Any]] = None
    metrics: Dict[str, Any] = Field(default_factory=dict)


class PRInfo(BaseModel):
    """Information about a pull request."""
    number: int
    title: str
    description: str
    author: str
    created_at: datetime
    updated_at: datetime
    base_branch: str
    head_branch: str
    files_changed: List[str]
    additions: int
    deletions: int
    commits: int


class PRReviewResult(BaseModel):
    """Complete result of a PR review."""
    pr_info: PRInfo
    feedback: ReviewFeedback
    analysis_duration: float
    provider: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AnalysisConfig(BaseModel):
    """Configuration for code analysis."""
    enable_pylint: bool = True
    enable_flake8: bool = True
    enable_black: bool = True
    enable_mypy: bool = True
    enable_bandit: bool = True
    enable_safety: bool = True
    enable_ai_analysis: bool = False
    ai_provider: Optional[str] = None
    custom_rules: List[str] = Field(default_factory=list)
    severity_threshold: IssueSeverity = IssueSeverity.MEDIUM
    max_issues_per_file: int = 50
