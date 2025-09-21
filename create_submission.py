#!/usr/bin/env python3
"""
Create clean submission package for CodeMate IDE
Removes system files and creates a clean zip for submission
"""

import os
import zipfile
import shutil
from pathlib import Path

def create_submission():
    """Create a clean submission package"""
    
    print("📦 Creating CodeMate IDE submission package...")
    
    # Files to include
    include_files = [
        # Core application files
        'app.py',
        'deploy.py',
        'requirements_web.txt',
        
        # Core modules
        'pr_review_agent/',
        'simple_pr_review.py',
        
        # Web templates and static files
        'templates/',
        'static/',
        
        # Documentation
        'README.md',
        'WEB_README.md',
        'GUI_README.md',
        'FEATURES.md',
        'docs/',
        
        # Examples
        'examples/',
        
        # Tests
        'tests/',
        
        # Configuration
        'pyproject.toml',
        'setup.py',
        'LICENSE',
        'env.example'
    ]
    
    # Files/folders to exclude
    exclude_patterns = [
        '__pycache__',
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '.pytest_cache',
        '.coverage',
        'htmlcov',
        '.tox',
        '.venv',
        'venv',
        'env',
        '.env',
        'node_modules',
        '.git',
        '.gitignore',
        '.DS_Store',
        'Thumbs.db',
        '*.log',
        '*.tmp',
        '*.temp',
        '.vscode',
        '.idea',
        '*.egg-info',
        'dist',
        'build'
    ]
    
    # Create submission directory
    submission_dir = 'pr_review_agent_submission'
    if os.path.exists(submission_dir):
        shutil.rmtree(submission_dir)
    os.makedirs(submission_dir)
    
    print(f"📁 Creating submission directory: {submission_dir}")
    
    # Copy files
    copied_files = []
    for item in include_files:
        if os.path.exists(item):
            if os.path.isfile(item):
                shutil.copy2(item, submission_dir)
                copied_files.append(item)
                print(f"✅ Copied file: {item}")
            elif os.path.isdir(item):
                dest_dir = os.path.join(submission_dir, item)
                shutil.copytree(item, dest_dir, ignore=shutil.ignore_patterns(*exclude_patterns))
                copied_files.append(item)
                print(f"✅ Copied directory: {item}")
        else:
            print(f"⚠️  File not found: {item}")
    
    # Create a simple README for submission
    submission_readme = f"""# PR Review Agent - CodeMate Submission

## 🚀 Quick Start

### Method 1: Web Application (Recommended)
```bash
python deploy.py
```
Then open http://localhost:5000 in your browser

### Method 2: Direct Flask
```bash
python app.py
```

### Method 3: Desktop GUI
```bash
python pr_review_gui_enhanced.py
```

## 📁 Project Structure

- `app.py` - Main Flask web application
- `pr_review_agent/` - Core Python package
- `templates/` - Web UI templates
- `static/` - CSS and JavaScript files
- `examples/` - Usage examples
- `tests/` - Test suite

## ✨ Features

- Multi-server support (GitHub, GitLab, Bitbucket)
- Code quality analysis
- Security vulnerability detection
- AI-powered suggestions
- Web interface and desktop GUI
- Export reports
- Analysis history

## 🎯 How to Use

1. Run the web application
2. Paste your Python code
3. Click "Analyze Code"
4. View results and suggestions

## 📊 Analysis Capabilities

- Code quality scoring (0-10)
- Issue detection and categorization
- Security vulnerability scanning
- Performance suggestions
- Style and readability checks

Files included: {len(copied_files)}
"""
    
    with open(os.path.join(submission_dir, 'SUBMISSION_README.md'), 'w') as f:
        f.write(submission_readme)
    
    # Create zip file
    zip_filename = 'pr_review_agent_submission.zip'
    print(f"📦 Creating zip file: {zip_filename}")
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(submission_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, submission_dir)
                zipf.write(file_path, arcname)
    
    print(f"✅ Submission package created: {zip_filename}")
    print(f"📊 Total files included: {len(copied_files)}")
    print(f"📁 Package size: {os.path.getsize(zip_filename) / 1024:.1f} KB")
    
    # Clean up
    shutil.rmtree(submission_dir)
    
    print("\n🎉 Ready for CodeMate IDE submission!")
    print(f"📤 Upload: {zip_filename}")

if __name__ == "__main__":
    create_submission()
