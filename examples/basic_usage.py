"""Basic usage example of PR Review Agent."""

from pr_review_agent import PRReviewAgent
from pr_review_agent.core.models import AnalysisConfig, IssueSeverity

def main():
    """Basic example of using PR Review Agent."""
    
    # Create configuration
    config = AnalysisConfig(
        enable_ai_analysis=True,
        severity_threshold=IssueSeverity.MEDIUM,
        enable_pylint=True,
        enable_flake8=True,
        enable_black=True,
        enable_mypy=True,
        enable_bandit=True,
        enable_safety=True
    )
    
    # Create agent
    agent = PRReviewAgent(config)
    
    # Review a PR
    try:
        result = agent.review_pr(
            provider="github",
            repo="microsoft/vscode",
            pr_number=1234,
            post_comments=False
        )
        
        # Print results
        print(f"PR #{result.pr_info.number}: {result.pr_info.title}")
        print(f"Overall Score: {result.feedback.overall_score}/10")
        print(f"Summary: {result.feedback.summary}")
        print(f"Issues found: {len(result.feedback.issues)}")
        
        # Print top issues
        for issue in result.feedback.issues[:5]:
            print(f"  - {issue.severity.value.upper()}: {issue.message}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
