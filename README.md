# Fake News Detection System
**Human-in-the-Loop News Verification System**

## 👨‍💻 Project Information

## 📝 Project Description
A web-based fake news detection system that combines machine learning predictions with human reviewer verification. The system provides an initial automated classification, but requires human judgment for final verification - implementing a true Human-in-the-Loop approach.

## ✨ Features
- ✅ User Authentication (Registration & Login)
- ✅ Role-Based Access Control (User, Reviewer, Admin)
- ✅ News Article Submission
- ✅ Automated ML Classification
- ✅ Manual Review Workflow
- ✅ Admin Dashboard with Statistics
- ✅ SQLite Database
- ✅ Responsive Web Interface

## 🏗️ System Architecture

### Three User Roles:

**1. General User**
- Submit news articles for verification
- View ML predictions
- Check review status
- See final verdicts

**2. Reviewer**
- View pending articles
- See ML model suggestions
- Approve (Real) or Reject (Fake) articles
- Track review history

**3. Administrator**
- View system statistics
- Manage user accounts
- Monitor all articles
- Access system reports

## 🛠️ Technologies Used
- **Backend:** Python Flask
- **Database:** SQLite3
- **Frontend:** HTML, CSS (embedded)
- **Security:** Werkzeug password hashing
- **Session Management:** Flask sessions

## 📋 Prerequisites
- Python 3.7 or higher
- pip (Python package manager)


## 👥 Demo Accounts

### Admin
- **Email:** admin@system.com
- **Password:** admin123

### Reviewer
- **Email:** reviewer@system.com
- **Password:** reviewer123

### User
- **Email:** user@system.com
- **Password:** user123

## 📊 How It Works

### Workflow:
1. **User submits** a news article with title and text
2. **ML Model analyzes** the content and provides initial classification
3. **Article is assigned** to reviewer queue
4. **Reviewer examines** the article and ML suggestion
5. **Reviewer makes final decision** (Approve/Reject)
6. **Final verdict stored** and visible to the user

### ML Classification Algorithm:
The system uses keyword-based classification:

**Fake News Indicators:**
- hoax
- conspiracy
- unverified
- shocking
- miracle cure
- secret
- they dont want you to know

**Real News Indicators:**
- according to
- research shows
- official statement
- confirmed
- study
- experts

