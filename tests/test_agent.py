"""Tests for PR Review Agent."""

import pytest
from unittest.mock import Mock, patch
from pr_review_agent.core.agent import PRReviewAgent
from pr_review_agent.core.models import AnalysisConfig, IssueSeverity, PRInfo, CodeIssue
from datetime import datetime


class TestPRReviewAgent:
    """Test cases for PRReviewAgent."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = AnalysisConfig(
            enable_pylint=False,
            enable_flake8=False,
            enable_black=False,
            enable_mypy=False,
            enable_bandit=False,
            enable_safety=False,
            enable_ai_analysis=False
        )
        self.agent = PRReviewAgent(self.config)
    
    def test_agent_initialization(self):
        """Test agent initialization."""
        assert self.agent.config == self.config
        assert len(self.agent.analyzers) == 0  # All analyzers disabled
    
    def test_should_analyze_file(self):
        """Test file filtering logic."""
        # Should analyze Python files
        assert self.agent._should_analyze_file("test.py") == True
        assert self.agent._should_analyze_file("src/main.py") == True
        
        # Should not analyze binary files
        assert self.agent._should_analyze_file("image.png") == False
        assert self.agent._should_analyze_file("data.zip") == False
        assert self.agent._should_analyze_file("executable.exe") == False
    
    def test_get_severity_level(self):
        """Test severity level conversion."""
        assert self.agent._get_severity_level("low") == 1
        assert self.agent._get_severity_level("medium") == 2
        assert self.agent._get_severity_level("high") == 3
        assert self.agent._get_severity_level("critical") == 4
    
    def test_calculate_score_no_issues(self):
        """Test score calculation with no issues."""
        pr_info = Mock()
        pr_info.files_changed = ["test.py"]
        score = self.agent._calculate_score([], pr_info)
        assert score == 10.0
    
    def test_calculate_score_with_issues(self):
        """Test score calculation with issues."""
        pr_info = Mock()
        pr_info.files_changed = ["test.py"]
        
        issues = [
            CodeIssue(
                file_path="test.py",
                line_number=1,
                severity=IssueSeverity.MEDIUM,
                category="bug",
                message="Test issue"
            )
        ]
        
        score = self.agent._calculate_score(issues, pr_info)
        assert score < 10.0
        assert score >= 0.0
    
    def test_generate_summary_no_issues(self):
        """Test summary generation with no issues."""
        pr_info = Mock()
        pr_info.additions = 10
        pr_info.deletions = 5
        pr_info.files_changed = ["test.py"]
        
        summary = self.agent._generate_summary([], pr_info)
        assert "Great work" in summary
        assert "No issues found" in summary
    
    def test_generate_summary_with_issues(self):
        """Test summary generation with issues."""
        pr_info = Mock()
        pr_info.files_changed = ["test.py"]
        
        issues = [
            CodeIssue(
                file_path="test.py",
                line_number=1,
                severity=IssueSeverity.HIGH,
                category="bug",
                message="Test issue"
            ),
            CodeIssue(
                file_path="test.py",
                line_number=2,
                severity=IssueSeverity.LOW,
                category="style",
                message="Style issue"
            )
        ]
        
        summary = self.agent._generate_summary(issues, pr_info)
        assert "Found 2 issues" in summary
        assert "1 high severity" in summary
        assert "1 low severity" in summary
    
    def test_extract_suggestions(self):
        """Test suggestion extraction."""
        issues = [
            CodeIssue(
                file_path="test.py",
                line_number=1,
                severity=IssueSeverity.MEDIUM,
                category="bug",
                message="Issue 1",
                suggestion="Fix this"
            ),
            CodeIssue(
                file_path="test.py",
                line_number=2,
                severity=IssueSeverity.HIGH,
                category="security",
                message="Issue 2",
                suggestion="Fix this too"
            ),
            CodeIssue(
                file_path="test.py",
                line_number=3,
                severity=IssueSeverity.LOW,
                category="style",
                message="Issue 3",
                suggestion="Fix this"
            )
        ]
        
        suggestions = self.agent._extract_suggestions(issues)
        assert len(suggestions) == 2  # Duplicate suggestion removed
        assert "Fix this" in suggestions
        assert "Fix this too" in suggestions
    
    def test_extract_strengths(self):
        """Test strength extraction."""
        pr_info = Mock()
        pr_info.additions = 10
        pr_info.deletions = 5
        pr_info.files_changed = ["test.py", "README.md", "test_test.py"]
        
        issues = []
        strengths = self.agent._extract_strengths(issues, pr_info)
        
        assert "Good balance of additions and deletions" in strengths
        assert "Focused changes across reasonable number of files" in strengths
        assert "Includes documentation updates" in strengths
        assert "Includes test updates" in strengths


class TestMockProvider:
    """Test with mocked provider."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = AnalysisConfig(
            enable_pylint=False,
            enable_flake8=False,
            enable_black=False,
            enable_mypy=False,
            enable_bandit=False,
            enable_safety=False,
            enable_ai_analysis=False
        )
        self.agent = PRReviewAgent(self.config)
    
    @patch('pr_review_agent.core.agent.PRReviewAgent._get_provider')
    def test_review_pr_success(self, mock_get_provider):
        """Test successful PR review."""
        # Mock provider
        mock_provider = Mock()
        mock_provider.get_pr_info.return_value = PRInfo(
            number=123,
            title="Test PR",
            description="Test description",
            author="testuser",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            base_branch="main",
            head_branch="feature",
            files_changed=["test.py"],
            additions=10,
            deletions=5,
            commits=1
        )
        mock_provider.get_file_content.return_value = "print('hello world')"
        mock_get_provider.return_value = mock_provider
        
        # Run review
        result = self.agent.review_pr("github", "owner/repo", 123)
        
        # Verify results
        assert result.pr_info.number == 123
        assert result.pr_info.title == "Test PR"
        assert result.provider == "github"
        assert result.analysis_duration > 0
    
    @patch('pr_review_agent.core.agent.PRReviewAgent._get_provider')
    def test_review_pr_with_comments(self, mock_get_provider):
        """Test PR review with comment posting."""
        # Mock provider
        mock_provider = Mock()
        mock_provider.get_pr_info.return_value = PRInfo(
            number=123,
            title="Test PR",
            description="Test description",
            author="testuser",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            base_branch="main",
            head_branch="feature",
            files_changed=["test.py"],
            additions=10,
            deletions=5,
            commits=1
        )
        mock_provider.get_file_content.return_value = "print('hello world')"
        mock_provider.post_comment.return_value = True
        mock_get_provider.return_value = mock_provider
        
        # Run review with comments
        result = self.agent.review_pr("github", "owner/repo", 123, post_comments=True)
        
        # Verify comment was posted
        assert mock_provider.post_comment.called


if __name__ == "__main__":
    pytest.main([__file__])
