# 🌐 PR Review Agent - Web Application

A beautiful, GitHub-themed web application for code quality analysis that can be hosted online.

## 🚀 Quick Start

### **Method 1: Auto-Deploy (Recommended)**
```bash
python deploy.py
```

### **Method 2: Manual Setup**
```bash
# Install requirements
pip install -r requirements_web.txt

# Run the app
python app.py
```

### **Method 3: Direct Flask**
```bash
flask run --host=0.0.0.0 --port=5000
```

## 🌍 Access the Application

Once running, open your browser and go to:
- **Local**: http://localhost:5000
- **Network**: http://your-ip:5000

## ✨ Features

### 🎨 **GitHub-Inspired Design**
- **Dark Theme**: GitHub's signature dark color scheme
- **Professional UI**: Clean, modern interface
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Smooth Animations**: Polished user experience

### 🔧 **Core Functionality**
- **Live Code Analysis**: Paste code and get instant feedback
- **Demo Mode**: Try it with sample code
- **Real-time Results**: See analysis progress
- **Export Reports**: Download analysis results
- **Analysis History**: Track previous analyses

### 📊 **Advanced Features**
- **Quality Scoring**: 0-10 quality score
- **Issue Categorization**: Critical, High, Medium, Low severity
- **Smart Suggestions**: Actionable improvement recommendations
- **File Statistics**: Lines of code, issue counts
- **Interactive Tabs**: Summary, Issues, Suggestions

## 🎯 How to Use

### **1. Analyze Your Code**
1. Open the web application
2. Paste your Python code in the editor
3. Click "🔍 Analyze Code"
4. View results in the tabs

### **2. Try the Demo**
1. Click "🎯 Run Demo"
2. See sample analysis results
3. Understand how the system works

### **3. Review Results**
- **📋 Summary**: Overall score and statistics
- **🐛 Issues**: Detailed problem analysis
- **💡 Suggestions**: Improvement recommendations

## 🚀 Deployment Options

### **Local Development**
```bash
python app.py
```

### **Production Deployment**

#### **Using Gunicorn**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### **Using Heroku**
1. Create `Procfile`:
   ```
   web: gunicorn app:app
   ```
2. Deploy to Heroku

#### **Using Docker**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements_web.txt .
RUN pip install -r requirements_web.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

#### **Using Railway/Render**
- Connect your GitHub repository
- Set build command: `pip install -r requirements_web.txt`
- Set start command: `python app.py`

## 🔧 Configuration

### **Environment Variables**
```bash
export FLASK_ENV=production
export FLASK_DEBUG=False
```

### **Custom Port**
```bash
python app.py --port 8080
```

## 📱 Mobile Support

The web application is fully responsive and works great on:
- **Desktop**: Full-featured experience
- **Tablet**: Optimized layout
- **Mobile**: Touch-friendly interface

## 🎨 Design System

### **Colors**
- **Background**: GitHub dark theme
- **Primary**: GitHub green (#238636)
- **Danger**: GitHub red (#da3633)
- **Warning**: GitHub yellow (#d29922)
- **Info**: GitHub blue (#0969da)

### **Typography**
- **Font**: Inter (GitHub's font)
- **Monospace**: Monaco/Menlo for code
- **Sizes**: Responsive scaling

## 🔍 API Endpoints

### **POST /api/analyze**
Analyze Python code
```json
{
  "code": "print('hello world')",
  "filename": "main.py"
}
```

### **POST /api/demo**
Run demo analysis

### **GET /api/history**
Get analysis history

### **GET /api/export/<analysis_id>**
Export analysis report

## 🛠️ Development

### **Project Structure**
```
├── app.py                 # Flask application
├── templates/
│   └── index.html        # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css     # GitHub-themed styles
│   └── js/
│       └── app.js        # Frontend JavaScript
├── requirements_web.txt  # Web dependencies
└── deploy.py            # Deployment script
```

### **Adding Features**
1. **Backend**: Modify `app.py`
2. **Frontend**: Update `templates/index.html` and `static/js/app.js`
3. **Styling**: Edit `static/css/style.css`

## 🌐 Hosting Platforms

### **Free Hosting Options**
- **Heroku**: Easy deployment
- **Railway**: Modern platform
- **Render**: Simple setup
- **Vercel**: Fast deployment
- **Netlify**: Static + serverless

### **Paid Hosting Options**
- **AWS**: Full control
- **Google Cloud**: Scalable
- **DigitalOcean**: Simple VPS
- **Linode**: Developer-friendly

## 📊 Performance

### **Optimizations**
- **Minified Assets**: Compressed CSS/JS
- **Efficient API**: Fast analysis
- **Caching**: Browser caching
- **CDN Ready**: Static asset delivery

### **Scalability**
- **Stateless**: Easy horizontal scaling
- **Database Ready**: Can add persistent storage
- **Load Balancer**: Multiple instances
- **Microservices**: Modular architecture

## 🔒 Security

### **Built-in Security**
- **Input Validation**: Sanitized code input
- **CSRF Protection**: Flask security
- **XSS Prevention**: Safe HTML rendering
- **Rate Limiting**: API protection

## 🎉 Live Demo

The application provides a complete code review experience:

1. **Professional Interface**: GitHub-quality design
2. **Real-time Analysis**: Instant feedback
3. **Comprehensive Results**: Detailed insights
4. **Export Capabilities**: Save reports
5. **History Tracking**: Previous analyses

## 🚀 Ready to Deploy!

Your PR Review Agent is now ready for hosting. Choose your preferred platform and deploy with confidence!

**Access your live application at: http://your-domain.com**
