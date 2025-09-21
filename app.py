#!/usr/bin/env python3
"""
PR Review Agent - Web Application
A beautiful web-based code review tool that can be hosted online
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import json
from datetime import datetime
from simple_pr_review import analyze_file, calculate_score, generate_feedback, SimplePRInfo, display_results
import tempfile
import uuid

app = Flask(__name__)
app.secret_key = 'pr-review-agent-secret-key'

# Store analysis history in memory (in production, use a database)
analysis_history = []

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_code():
    """API endpoint to analyze code"""
    try:
        data = request.get_json()
        code = data.get('code', '')
        filename = data.get('filename', 'main.py')
        
        if not code.strip():
            return jsonify({'error': 'No code provided'}), 400
        
        # Analyze the code
        issues = analyze_file(filename, content)
        
        # Create PR info
        pr_info = SimplePRInfo(
            number=1,
            title=f"Analysis of {filename}",
            author="web_user",
            files_changed=[filename],
            additions=len(code.split('\n')),
            deletions=0
        )
        
        # Generate feedback
        feedback = generate_feedback(issues, pr_info)
        
        # Store in history
        analysis_id = str(uuid.uuid4())
        analysis_data = {
            'id': analysis_id,
            'timestamp': datetime.now().isoformat(),
            'filename': filename,
            'score': feedback.overall_score,
            'issues_count': len(feedback.issues),
            'issues': [
                {
                    'file_path': issue.file_path,
                    'line_number': issue.line_number,
                    'severity': issue.severity,
                    'category': issue.category,
                    'message': issue.message,
                    'suggestion': issue.suggestion
                } for issue in feedback.issues
            ],
            'suggestions': feedback.suggestions,
            'strengths': feedback.strengths,
            'summary': feedback.summary
        }
        
        analysis_history.append(analysis_data)
        
        return jsonify({
            'success': True,
            'analysis_id': analysis_id,
            'score': feedback.overall_score,
            'issues_count': len(feedback.issues),
            'issues': analysis_data['issues'],
            'suggestions': feedback.suggestions,
            'strengths': feedback.strengths,
            'summary': feedback.summary,
            'file_stats': {
                'lines': len(code.split('\n')),
                'filename': filename
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/demo', methods=['POST'])
def run_demo():
    """API endpoint to run demo analysis"""
    try:
        # Demo code
        demo_code = '''def authenticate_user(username, password):
    # TODO: Add rate limiting
    print(f"Authenticating user: {username}")
    user_password = "admin123"  # Hardcoded password
    if password == user_password:
        return True
    return False

def create_session(user_id):
    # This is a very long line that exceeds the recommended line length
    session = Session(user_id=user_id, created_at=datetime.now())
    return session

def process_payment(amount):
    try:
        # Process payment
        result = payment_gateway.charge(amount)
        return result
    except:  # Bare except clause
        return None'''
        
        # Analyze demo code
        issues = analyze_file("demo.py", demo_code)
        
        # Create PR info
        pr_info = SimplePRInfo(
            number=123,
            title="Demo: Add user authentication feature",
            author="demo_user",
            files_changed=["demo.py"],
            additions=len(demo_code.split('\n')),
            deletions=0
        )
        
        # Generate feedback
        feedback = generate_feedback(issues, pr_info)
        
        # Store in history
        analysis_id = str(uuid.uuid4())
        analysis_data = {
            'id': analysis_id,
            'timestamp': datetime.now().isoformat(),
            'filename': 'demo.py',
            'score': feedback.overall_score,
            'issues_count': len(feedback.issues),
            'issues': [
                {
                    'file_path': issue.file_path,
                    'line_number': issue.line_number,
                    'severity': issue.severity,
                    'category': issue.category,
                    'message': issue.message,
                    'suggestion': issue.suggestion
                } for issue in feedback.issues
            ],
            'suggestions': feedback.suggestions,
            'strengths': feedback.strengths,
            'summary': feedback.summary
        }
        
        analysis_history.append(analysis_data)
        
        return jsonify({
            'success': True,
            'analysis_id': analysis_id,
            'score': feedback.overall_score,
            'issues_count': len(feedback.issues),
            'issues': analysis_data['issues'],
            'suggestions': feedback.suggestions,
            'strengths': feedback.strengths,
            'summary': feedback.summary,
            'file_stats': {
                'lines': len(demo_code.split('\n')),
                'filename': 'demo.py'
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history')
def get_history():
    """Get analysis history"""
    return jsonify({
        'success': True,
        'history': analysis_history[-10:]  # Last 10 analyses
    })

@app.route('/api/export/<analysis_id>')
def export_analysis(analysis_id):
    """Export analysis as text file"""
    try:
        # Find analysis
        analysis = next((a for a in analysis_history if a['id'] == analysis_id), None)
        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404
        
        # Create report content
        report = f"""PR Review Agent - Analysis Report
{'='*50}

Generated: {analysis['timestamp']}
File: {analysis['filename']}
Score: {analysis['score']:.1f}/10

SUMMARY:
{analysis['summary']}

ISSUES FOUND ({analysis['issues_count']}):
"""
        
        for i, issue in enumerate(analysis['issues'], 1):
            report += f"{i}. {issue['severity'].upper()} - {issue['file_path']}:{issue['line_number']}\n"
            report += f"   {issue['message']}\n"
            if issue['suggestion']:
                report += f"   Suggestion: {issue['suggestion']}\n"
            report += "\n"
        
        if analysis['suggestions']:
            report += "SUGGESTIONS:\n"
            for i, suggestion in enumerate(analysis['suggestions'], 1):
                report += f"{i}. {suggestion}\n"
        
        if analysis['strengths']:
            report += "\nSTRENGTHS:\n"
            for strength in analysis['strengths']:
                report += f"• {strength}\n"
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(report)
            temp_path = f.name
        
        return send_file(temp_path, as_attachment=True, download_name=f"analysis_{analysis_id}.txt")
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
