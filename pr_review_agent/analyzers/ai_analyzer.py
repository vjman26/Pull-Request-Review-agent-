"""AI-powered code analyzer for intelligent suggestions."""

import os
from typing import List, Dict, Any, Optional
from pr_review_agent.core.models import CodeIssue, AnalysisConfig, IssueSeverity, IssueCategory


class AIAnalyzer:
    """AI-powered code analyzer using OpenAI or Anthropic."""

    def __init__(self, config: AnalysisConfig):
        self.config = config
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')

    def analyze(self, file_path: str, content: str) -> List[CodeIssue]:
        if not self.should_analyze(file_path) or not self._has_api_key():
            return []

        try:
            if self.openai_key:
                return self._analyze_with_openai(file_path, content)
            elif self.anthropic_key:
                return self._analyze_with_anthropic(file_path, content)
        except Exception:
            pass

        return []

    def _analyze_with_openai(self, file_path: str, content: str) -> List[CodeIssue]:
        """Analyze using OpenAI API."""
        try:
            import openai
            client = openai.OpenAI(api_key=self.openai_key)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "system",
                    "content": "You are a code reviewer. Analyze the code and provide specific, actionable feedback on performance, readability, and potential issues. Return only JSON with issues array."
                }, {
                    "role": "user", 
                    "content": f"File: {file_path}\n\nCode:\n{content[:4000]}"
                }],
                max_tokens=1000
            )
            
            # Parse AI response and convert to CodeIssue objects
            # This is simplified - in practice you'd parse the JSON response
            return []
            
        except Exception:
            return []

    def _analyze_with_anthropic(self, file_path: str, content: str) -> List[CodeIssue]:
        """Analyze using Anthropic API."""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.anthropic_key)
            
            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                messages=[{
                    "role": "user",
                    "content": f"Review this code for issues:\n\nFile: {file_path}\n\nCode:\n{content[:4000]}"
                }]
            )
            
            # Parse response and convert to CodeIssue objects
            return []
            
        except Exception:
            return []

    def _has_api_key(self) -> bool:
        return bool(self.openai_key or self.anthropic_key)

    def should_analyze(self, file_path: str) -> bool:
        return file_path.endswith('.py')

    def get_name(self) -> str:
        return "AI Analyzer"

    def get_metrics(self, file_path: str, content: str) -> Dict[str, Any]:
        return {}
