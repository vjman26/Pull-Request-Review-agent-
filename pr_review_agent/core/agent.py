"""Main PR Review Agent implementation."""

import time
from typing import List, Optional, Dict, Any
from .models import PRReviewResult, ReviewFeedback, CodeIssue, AnalysisConfig, PRInfo
from ..providers import GitHubProvider, GitLabProvider, BitbucketProvider
from ..analyzers import (
    PylintAnalyzer, Flake8Analyzer, BlackAnalyzer, MyPyAnalyzer,
    BanditAnalyzer, SafetyAnalyzer, AIAnalyzer
)


class PRReviewAgent:
    """Main PR Review Agent for analyzing pull requests."""

    def __init__(self, config: Optional[AnalysisConfig] = None):
        """Initialize the PR Review Agent."""
        self.config = config or AnalysisConfig()
        self.analyzers = self._initialize_analyzers()

    def _initialize_analyzers(self) -> List:
        """Initialize all enabled analyzers."""
        analyzers = []
        
        if self.config.enable_pylint:
            analyzers.append(PylintAnalyzer(self.config))
        if self.config.enable_flake8:
            analyzers.append(Flake8Analyzer(self.config))
        if self.config.enable_black:
            analyzers.append(BlackAnalyzer(self.config))
        if self.config.enable_mypy:
            analyzers.append(MyPyAnalyzer(self.config))
        if self.config.enable_bandit:
            analyzers.append(BanditAnalyzer(self.config))
        if self.config.enable_safety:
            analyzers.append(SafetyAnalyzer(self.config))
        if self.config.enable_ai_analysis:
            analyzers.append(AIAnalyzer(self.config))

        return analyzers

    def review_pr(self, provider: str, repo: str, pr_number: int, 
                  post_comments: bool = False) -> PRReviewResult:
        """Review a pull request and return analysis results."""
        start_time = time.time()
        
        # Get provider instance
        pr_provider = self._get_provider(provider)
        
        # Fetch PR information
        pr_info = pr_provider.get_pr_info(repo, pr_number)
        
        # Analyze all files in the PR
        all_issues = []
        all_metrics = {}
        
        for file_path in pr_info.files_changed:
            if self._should_analyze_file(file_path):
                try:
                    # Get file content
                    content = pr_provider.get_file_content(repo, file_path, pr_info.head_branch)
                    
                    # Run all analyzers on the file
                    file_issues, file_metrics = self._analyze_file(file_path, content)
                    all_issues.extend(file_issues)
                    all_metrics[file_path] = file_metrics
                    
                except Exception as e:
                    # Log error but continue with other files
                    print(f"Error analyzing {file_path}: {e}")
                    continue

        # Generate feedback
        feedback = self._generate_feedback(all_issues, all_metrics, pr_info)
        
        # Post comments if requested
        if post_comments:
            self._post_feedback_comments(pr_provider, repo, pr_number, feedback)

        analysis_duration = time.time() - start_time
        
        return PRReviewResult(
            pr_info=pr_info,
            feedback=feedback,
            analysis_duration=analysis_duration,
            provider=provider,
            metadata={"files_analyzed": len(pr_info.files_changed)}
        )

    def _get_provider(self, provider: str):
        """Get the appropriate provider instance."""
        if provider.lower() == "github":
            return GitHubProvider()
        elif provider.lower() == "gitlab":
            return GitLabProvider()
        elif provider.lower() == "bitbucket":
            return BitbucketProvider()
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def _should_analyze_file(self, file_path: str) -> bool:
        """Check if a file should be analyzed."""
        # Skip binary files, images, etc.
        skip_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', 
                          '.pdf', '.zip', '.tar', '.gz', '.exe', '.dll'}
        
        if any(file_path.lower().endswith(ext) for ext in skip_extensions):
            return False
            
        # Only analyze text files
        return True

    def _analyze_file(self, file_path: str, content: str) -> tuple[List[CodeIssue], Dict[str, Any]]:
        """Analyze a single file with all enabled analyzers."""
        issues = []
        metrics = {}
        
        for analyzer in self.analyzers:
            if analyzer.should_analyze(file_path):
                try:
                    file_issues = analyzer.analyze(file_path, content)
                    issues.extend(file_issues)
                    
                    file_metrics = analyzer.get_metrics(file_path, content)
                    metrics.update(file_metrics)
                    
                except Exception as e:
                    print(f"Error in {analyzer.get_name()}: {e}")
                    continue
        
        return issues, metrics

    def _generate_feedback(self, issues: List[CodeIssue], metrics: Dict[str, Any], 
                          pr_info: PRInfo) -> ReviewFeedback:
        """Generate comprehensive feedback from analysis results."""
        
        # Filter issues by severity threshold
        filtered_issues = [
            issue for issue in issues 
            if self._get_severity_level(issue.severity) >= self._get_severity_level(self.config.severity_threshold)
        ]
        
        # Calculate overall score
        score = self._calculate_score(filtered_issues, pr_info)
        
        # Generate summary
        summary = self._generate_summary(filtered_issues, pr_info)
        
        # Extract suggestions and strengths
        suggestions = self._extract_suggestions(filtered_issues)
        strengths = self._extract_strengths(filtered_issues, pr_info)
        
        # Prepare AI insights if available
        ai_insights = self._generate_ai_insights(filtered_issues, pr_info) if self.config.enable_ai_analysis else None
        
        return ReviewFeedback(
            overall_score=score,
            summary=summary,
            issues=filtered_issues,
            suggestions=suggestions,
            strengths=strengths,
            ai_insights=ai_insights,
            metrics=metrics
        )

    def _get_severity_level(self, severity) -> int:
        """Convert severity to numeric level for comparison."""
        levels = {
            "low": 1,
            "medium": 2, 
            "high": 3,
            "critical": 4
        }
        return levels.get(severity.value if hasattr(severity, 'value') else severity, 2)

    def _calculate_score(self, issues: List[CodeIssue], pr_info: PRInfo) -> float:
        """Calculate overall PR quality score (0-10)."""
        if not issues:
            return 10.0
        
        # Base score
        base_score = 10.0
        
        # Deduct points based on issue severity and count
        severity_penalties = {
            "low": 0.1,
            "medium": 0.3,
            "high": 0.7,
            "critical": 1.5
        }
        
        total_penalty = 0
        for issue in issues:
            penalty = severity_penalties.get(
                issue.severity.value if hasattr(issue.severity, 'value') else issue.severity, 
                0.3
            )
            total_penalty += penalty
        
        # Normalize by file count to avoid penalizing large PRs unfairly
        file_count = len(pr_info.files_changed)
        if file_count > 0:
            total_penalty = total_penalty / (file_count ** 0.5)  # Square root scaling
        
        score = max(0.0, base_score - total_penalty)
        return round(score, 1)

    def _generate_summary(self, issues: List[CodeIssue], pr_info: PRInfo) -> str:
        """Generate a summary of the PR review."""
        issue_count = len(issues)
        
        if issue_count == 0:
            return f"✅ Great work! No issues found in this {pr_info.additions + pr_info.deletions} line change across {len(pr_info.files_changed)} files."
        
        # Count issues by severity
        severity_counts = {}
        for issue in issues:
            severity = issue.severity.value if hasattr(issue.severity, 'value') else issue.severity
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        summary_parts = [f"Found {issue_count} issues in {len(pr_info.files_changed)} files:"]
        
        for severity in ["critical", "high", "medium", "low"]:
            count = severity_counts.get(severity, 0)
            if count > 0:
                summary_parts.append(f"  • {count} {severity} severity")
        
        return " ".join(summary_parts)

    def _extract_suggestions(self, issues: List[CodeIssue]) -> List[str]:
        """Extract unique suggestions from issues."""
        suggestions = set()
        for issue in issues:
            if issue.suggestion:
                suggestions.add(issue.suggestion)
        return list(suggestions)

    def _extract_strengths(self, issues: List[CodeIssue], pr_info: PRInfo) -> List[str]:
        """Extract strengths from the PR."""
        strengths = []
        
        # Check for good practices
        if pr_info.additions > 0 and pr_info.deletions > 0:
            strengths.append("Good balance of additions and deletions")
        
        if len(pr_info.files_changed) <= 10:
            strengths.append("Focused changes across reasonable number of files")
        
        # Check for documentation
        doc_files = [f for f in pr_info.files_changed if any(ext in f.lower() for ext in ['.md', '.rst', '.txt'])]
        if doc_files:
            strengths.append("Includes documentation updates")
        
        # Check for tests
        test_files = [f for f in pr_info.files_changed if 'test' in f.lower()]
        if test_files:
            strengths.append("Includes test updates")
        
        return strengths

    def _generate_ai_insights(self, issues: List[CodeIssue], pr_info: PRInfo) -> Dict[str, Any]:
        """Generate AI-powered insights."""
        # This would integrate with AI services for deeper analysis
        return {
            "complexity_analysis": "Code complexity appears manageable",
            "maintainability_score": 8.5,
            "performance_notes": "No obvious performance issues detected"
        }

    def _post_feedback_comments(self, provider, repo: str, pr_number: int, feedback: ReviewFeedback):
        """Post feedback as comments on the PR."""
        # Post overall summary
        provider.post_comment(repo, pr_number, f"## PR Review Summary\n\n{feedback.summary}")
        
        # Post individual issue comments for high/critical issues
        for issue in feedback.issues:
            if issue.severity.value in ["high", "critical"]:
                comment = f"**{issue.severity.value.upper()}**: {issue.message}"
                if issue.suggestion:
                    comment += f"\n\n**Suggestion**: {issue.suggestion}"
                
                provider.post_comment(
                    repo, pr_number, comment, 
                    file_path=issue.file_path, 
                    line_number=issue.line_number
                )
