"""CI/CD integration example."""

import os
import sys
from pr_review_agent import PRReviewAgent
from pr_review_agent.core.models import AnalysisConfig, IssueSeverity


def ci_review():
    """Run PR review in CI environment."""
    
    # Get CI environment variables
    provider = os.getenv('CI_PROVIDER', 'github')
    repo = os.getenv('CI_REPO')
    pr_number = int(os.getenv('CI_PR_NUMBER', '0'))
    
    if not repo or pr_number == 0:
        print("Error: CI_REPO and CI_PR_NUMBER environment variables required")
        sys.exit(1)
    
    # Create configuration for CI
    config = AnalysisConfig(
        enable_ai_analysis=bool(os.getenv('OPENAI_API_KEY')),
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
    
    try:
        # Run review
        result = agent.review_pr(
            provider=provider,
            repo=repo,
            pr_number=pr_number,
            post_comments=True  # Post comments in CI
        )
        
        # Check if review passed
        score = result.feedback.overall_score
        critical_issues = [i for i in result.feedback.issues if i.severity.value == 'critical']
        high_issues = [i for i in result.feedback.issues if i.severity.value == 'high']
        
        print(f"PR Review Score: {score}/10")
        print(f"Critical Issues: {len(critical_issues)}")
        print(f"High Issues: {len(high_issues)}")
        
        # Fail CI if score is too low or critical issues exist
        if score < 6.0:
            print("❌ PR Review failed: Score too low")
            sys.exit(1)
        
        if critical_issues:
            print("❌ PR Review failed: Critical issues found")
            for issue in critical_issues:
                print(f"  - {issue.file_path}:{issue.line_number} - {issue.message}")
            sys.exit(1)
        
        if high_issues and score < 7.0:
            print("⚠️  PR Review warning: High severity issues with low score")
            for issue in high_issues:
                print(f"  - {issue.file_path}:{issue.line_number} - {issue.message}")
        
        print("✅ PR Review passed")
        
    except Exception as e:
        print(f"❌ PR Review failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    ci_review()
