# app_complete_with_analytics.py - Enhanced with Analytics & Visualizations
# Multi-Level Verification with Charts and Statistics
# Created by: Anchalpreet Singh Bhatia (72310132)

from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime
import random
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

def init_db():
    """Initialize database with users and articles tables and default users."""
    conn = sqlite3.connect('fake_news_detection.db')
    c = conn.cursor()
        
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )''')
        
    c.execute('''CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        text TEXT NOT NULL,
        submitted_by INTEGER,
        submitted_at TEXT,
        ml_prediction TEXT,
        ml_confidence REAL,
        status TEXT DEFAULT 'pending',          -- pending, reviewed, admin_reviewed
        reviewed_by INTEGER,
        final_verdict TEXT,                     -- 'Real' or 'Fake' (set by Reviewer/Admin)
        reviewed_at TEXT,
        admin_verified INTEGER DEFAULT 0,
        admin_verified_by INTEGER,
        admin_verified_at TEXT,
        needs_admin_review INTEGER DEFAULT 0,   -- Flag set by Reviewer
        reliable_source_json TEXT,
        FOREIGN KEY (submitted_by) REFERENCES users(id),
        FOREIGN KEY (reviewed_by) REFERENCES users(id),
        FOREIGN KEY (admin_verified_by) REFERENCES users(id)
    )''')
        
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        # Generate hashes once for the default users
        default_users = [
            ('Admin User', 'admin@system.com', generate_password_hash('admin123'), 'admin'),
            ('Reviewer Priya', 'reviewer@system.com', generate_password_hash('reviewer123'), 'reviewer'),
            ('General User', 'user@system.com', generate_password_hash('user123'), 'user')
        ]
        c.executemany('INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)', default_users)
        conn.commit()
    conn.close()

def get_reliable_sources(title):
    """Mock external search for reliable sources"""
    topic = "General News"
    if "climate" in title.lower():
        topic = "Climate Science"
    elif "vaccine" in title.lower() or "health" in title.lower():
        topic = "Health"
    elif "earnings" in title.lower() or "stock" in title.lower():
        topic = "Finance"
    
    if topic == "Climate Science":
        sources = [
            {"title": "NASA Climate Change", "uri": "https://climate.nasa.gov/"},
            {"title": "NOAA Climate.gov", "uri": "https://www.climate.gov/"}
        ]
    elif topic == "Health":
        sources = [
            {"title": "CDC - Centers for Disease Control", "uri": "https://www.cdc.gov/"},
            {"title": "WHO - World Health Organization", "uri": "https://www.who.int/"}
        ]
    elif topic == "Finance":
        sources = [
            {"title": "Wall Street Journal", "uri": "https://www.wsj.com/"},
            {"title": "Bloomberg", "uri": "https://www.bloomberg.com/"}
        ]
    else:
        sources = [
            {"title": "Associated Press News", "uri": "https://apnews.com/"},
            {"title": "Reuters Fact-Check", "uri": "https://www.reuters.com/fact-check/"}
        ]
    return json.dumps(sources)

def classify_article(text, title):
    """Enhanced ML classification"""
    fake_keywords = {
        'hoax': 3, 'conspiracy': 3, 'unverified': 2, 'shocking': 2,
        'miracle cure': 4, 'secret': 2, 'breaking': 2, 'exposed': 2,
        'they don\'t want you to know': 4, 'incredible': 1, 'amazing': 1
    }
    real_keywords = {
        'according to': 3, 'research shows': 4, 'official statement': 4,
        'confirmed': 3, 'study': 3, 'experts': 2, 'published': 2,
        'peer-reviewed': 4, 'data indicates': 3, 'report': 2
    }
        
    text_lower = text.lower()
    fake_score = sum(weight for keyword, weight in fake_keywords.items() if keyword in text_lower)
    real_score = sum(weight for keyword, weight in real_keywords.items() if keyword in text_lower)
        
    has_sources = bool(any(word in text_lower for word in ['source:', 'according to', 'cited', 'reference']))
    has_dates = bool(any(char.isdigit() for char in text[:100]))
    word_count = len(text.split())
        
    if has_sources:
        real_score += 2
    if has_dates:
        real_score += 1
    if word_count < 50:
        fake_score += 2
        
    total_score = fake_score + real_score
    if total_score > 0:
        score_diff = abs(fake_score - real_score)
        confidence = 0.60 + min(score_diff / total_score, 0.35)
    else:
        confidence = 0.55
        
    if fake_score > real_score:
        prediction = 'Fake'
    elif real_score > fake_score:
        prediction = 'Real'
    else:
        prediction = random.choice(['Real', 'Fake'])
        confidence = 0.55
        
    return prediction, min(confidence, 0.95), get_reliable_sources(title)

# Enhanced HTML with Chart.js for visualizations (Background color changed here)
BASE_HTML = '''<!DOCTYPE html><html><head>
    <title>Fake News Detection System</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        :root {
            --primary: #2563eb; --primary-dark: #1e40af; --secondary: #7c3aed;
            --success: #10b981; --danger: #ef4444; --warning: #f59e0b;
            --gray-50: #f9fafb; --gray-100: #f3f4f6; --gray-200: #e5e7eb;
            --gray-600: #4b5563; --gray-700: #374151; --gray-900: #111827;
        }
        body {
            font-family: 'Inter', sans-serif;
            /* --- REVISED BACKGROUND COLOR --- */
            background: linear-gradient(135deg, #e0f7fa 0%, #f1f8e9 100%); 
            /* -------------------------------- */
            min-height: 100vh; position: relative; overflow-x: hidden;
        }
        @keyframes fadeInUp { from { opacity: 0; transform: translateY(40px); } to { opacity: 1; transform: translateY(0); } }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; position: relative; z-index: 1; }
        .navbar {
            background: rgba(255, 255, 255, 0.98); backdrop-filter: blur(20px);
            padding: 24px 40px; box-shadow: 0 10px 40px rgba(0, 0, 0, 0.12);
            margin-bottom: 35px; display: flex; justify-content: space-between;
            align-items: center; border-radius: 20px; animation: fadeInUp 0.7s;
        }
        .navbar h1 {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            font-size: 32px; font-weight: 900; font-family: 'Space Grotesk', sans-serif;
            display: flex; align-items: center; gap: 12px;
        }
        .navbar h1::before { content: '🛡️'; font-size: 36px; }
        .navbar .user-info span {
            color: var(--gray-700); font-weight: 600; padding: 10px 20px;
            background: linear-gradient(135deg, var(--gray-100), var(--gray-50));
            border-radius: 25px; font-size: 14px;
        }
        .btn {
            padding: 12px 32px; background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            color: white; border: none; border-radius: 14px; cursor: pointer;
            font-weight: 700; font-size: 14px; transition: all 0.3s;
            box-shadow: 0 4px 20px rgba(37, 99, 235, 0.4);
            text-decoration: none; display: inline-flex; align-items: center; gap: 8px;
        }
        .btn-danger { background: linear-gradient(135deg, var(--danger), #dc2626); }
        .btn-success { background: linear-gradient(135deg, var(--success), #059669); }
        .card {
            background: rgba(255, 255, 255, 0.98); backdrop-filter: blur(20px);
            padding: 35px; border-radius: 24px; box-shadow: 0 10px 40px rgba(0, 0, 0, 0.12);
            margin-bottom: 30px; animation: fadeInUp 0.7s; transition: all 0.4s; position: relative;
        }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 30px; }
        .stat-card {
            background: rgba(255, 255, 255, 0.98); backdrop-filter: blur(20px);
            padding: 30px; border-radius: 24px; box-shadow: 0 10px 40px rgba(0, 0, 0, 0.12);
            transition: all 0.4s; animation: scaleIn 0.6s; position: relative;
        }
        .stat-card .number {
            font-size: 56px; font-weight: 900; margin: 15px 0;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            font-family: 'Space Grotesk', sans-serif;
        }
        .chart-container {
            position: relative; height: 300px; margin: 20px 0;
        }
        .form-group { margin-bottom: 24px; }
        .form-group label { display: block; margin-bottom: 10px; color: var(--gray-900); font-weight: 700; }
        .form-group input, .form-group textarea, .form-group select {
            width: 100%; padding: 16px 20px; border: 2px solid var(--gray-200);
            border-radius: 14px; font-size: 15px; font-family: 'Inter', sans-serif;
            transition: all 0.3s; background: white;
        }
        .alert {
            padding: 18px 24px; border-radius: 16px; margin-bottom: 24px;
            font-weight: 600; display: flex; align-items: center; gap: 12px;
        }
        .alert-error { background: linear-gradient(135deg, #fee2e2, #fecaca); color: #991b1b; border: 2px solid var(--danger); }
        .article-item {
            border: 2px solid var(--gray-200); padding: 24px; border-radius: 18px;
            margin-bottom: 20px; transition: all 0.3s; background: linear-gradient(135deg, #ffffff, #fafafa);
        }
        .badge {
            display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px;
            border-radius: 20px; font-size: 12px; font-weight: 800; text-transform: uppercase;
        }
        .badge-real { background: linear-gradient(135deg, #d1fae5, #a7f3d0); color: #065f46; border: 2px solid var(--success); }
        .badge-fake { background: linear-gradient(135deg, #fee2e2, #fecaca); color: #991b1b; border: 2px solid var(--danger); }
        .badge-pending { background: linear-gradient(135deg, #fef3c7, #fde68a); color: #92400e; border: 2px solid var(--warning); }
        .login-container {
            max-width: 500px; margin: 80px auto; background: rgba(255, 255, 255, 0.98);
            padding: 50px; border-radius: 32px; box-shadow: 0 25px 80px rgba(0, 0, 0, 0.4);
        }
        .demo-accounts {
            background: linear-gradient(135deg, #dbeafe, #bfdbfe); padding: 24px;
            border-radius: 20px; margin-top: 30px; font-size: 13px; border: 2px solid var(--primary);
        }
        @media (max-width: 768px) {
            .navbar { flex-direction: column; gap: 18px; }
            .grid { grid-template-columns: 1fr; }
        }
    </style></head><body>
    {% block content %}{% endblock %}
</body></html>'''

@app.route('/')
def index():
    if 'user_id' in session:
        role = session.get('user_role')
        if role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif role == 'reviewer':
            return redirect(url_for('reviewer_dashboard'))
        else:
            return redirect(url_for('user_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = sqlite3.connect('fake_news_detection.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_role'] = user['role']
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password')
            
    html = BASE_HTML.replace('{% block content %}{% endblock %}', '''
    <div class="login-container">
        <div style="text-align:center;margin-bottom:30px;"><div style="font-size:72px;">🛡️</div></div>
        <h1 style="text-align:center;color:var(--gray-900);margin-bottom:10px;font-size:32px;">Fake News Detection</h1>
        <p style="text-align:center;color:var(--gray-600);margin-bottom:30px;">Multi-Level Verification</p>
        {% with messages = get_flashed_messages() %}{% if messages %}{% for message in messages %}<div class="alert alert-error">{{ message }}</div>{% endfor %}{% endif %}{% endwith %}
        <form method="POST">
            <div class="form-group">
                <label>📧 Email</label>
                <input type="email" name="email" required>
            </div>
            <div class="form-group">
                <label>🔒 Password</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit" class="btn" style="width:100%;justify-content:center;">Sign In</button>
        </form>
        <div class="demo-accounts">
            <strong>🎯 Demo Accounts:</strong>
            Admin: admin@system.com / admin123<br>
            Reviewer: reviewer@system.com / reviewer123<br>
            User: user@system.com / user123
        </div>
    </div>''')
    return render_template_string(html)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/user/dashboard', methods=['GET', 'POST'])
def user_dashboard():
    if 'user_id' not in session or session.get('user_role') != 'user':
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        text = request.form['text']
        prediction, confidence, sources_json = classify_article(text, title)
        conn = sqlite3.connect('fake_news_detection.db')
        c = conn.cursor()
        c.execute('''INSERT INTO articles (title, text, submitted_by, submitted_at, ml_prediction, ml_confidence, status, reliable_source_json) 
                     VALUES (?, ?, ?, ?, ?, ?, 'pending', ?)''',
                   (title, text, session['user_id'], datetime.now().isoformat(), prediction, confidence, sources_json))
        conn.commit()
        conn.close()
        flash(f'✨ Article submitted! AI predicts: {prediction} ({confidence*100:.1f}% confidence)')
        return redirect(url_for('user_dashboard'))

    conn = sqlite3.connect('fake_news_detection.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
    user = c.fetchone()
    c.execute('SELECT * FROM articles WHERE submitted_by = ? ORDER BY submitted_at DESC', (session['user_id'],))
    articles = c.fetchall()
    conn.close()

    total_submitted = len(articles)
    reviewed_articles = [a for a in articles if a['status'] != 'pending']
    total_reviewed = len(reviewed_articles)

    real_count = len([a for a in reviewed_articles if a['final_verdict'] == 'Real'])
    fake_count = len([a for a in reviewed_articles if a['final_verdict'] == 'Fake'])
    
    ai_correct = len([a for a in reviewed_articles if a['ml_prediction'] == a['final_verdict']])
    accuracy_rate = (ai_correct / total_reviewed * 100) if total_reviewed > 0 else 0
    
    stats = {
        'total': total_submitted,
        'reviewed': total_reviewed,
        'pending': total_submitted - total_reviewed,
        'real': real_count,
        'fake': fake_count,
        'accuracy': accuracy_rate
    }
    
    articles_with_sources = []
    for article in articles:
        a = dict(article)
        try:
            a['parsed_sources'] = json.loads(a['reliable_source_json'])
        except:
            a['parsed_sources'] = []
        articles_with_sources.append(a)

    # HTML for User Dashboard (including analytics charts)
    html = BASE_HTML.replace('{% block content %}{% endblock %}', '''
    <div class="navbar">
        <h1>User Dashboard</h1>
        <div class="user-info">
            <span>👤 {{ user.name }}</span>
            <a href="{{ url_for('logout') }}" class="btn btn-danger">Logout</a>
        </div>
    </div>
    <div class="container">
        {% with messages = get_flashed_messages() %}{% if messages %}{% for message in messages %}<div class="alert alert-success">{{ message }}</div>{% endfor %}{% endif %}{% endwith %}

        <div class="grid" style="margin-bottom:30px;">
            <div class="stat-card">
                <h3>Total Submitted</h3>
                <div class="number">{{ stats.total }}</div>
                <small>Articles you submitted</small>
            </div>
            <div class="stat-card">
                <h3>Reviewed</h3>
                <div class="number" style="background:linear-gradient(135deg,var(--success),#059669);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{{ stats.reviewed }}</div>
                <small>Verification complete</small>
            </div>
            <div class="stat-card">
                <h3>Pending</h3>
                <div class="number" style="background:linear-gradient(135deg,var(--warning),#d97706);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{{ stats.pending }}</div>
                <small>Awaiting review</small>
            </div>
        </div>

        {% if stats.reviewed > 0 %}
        <div class="card">
            <h2>📊 Your Submission Analytics</h2>
            <div class="grid">
                <div>
                    <h3 style="color:var(--gray-700);margin-bottom:15px;">Verification Results</h3>
                    <div class="chart-container">
                        <canvas id="userPieChart"></canvas>
                    </div>
                    <div style="text-align:center;margin-top:15px;">
                        <span class="badge badge-real">{{ stats.real }} Real</span>
                        <span class="badge badge-fake">{{ stats.fake }} Fake</span>
                    </div>
                </div>
                <div>
                    <h3 style="color:var(--gray-700);margin-bottom:15px;">AI Accuracy on Your Articles</h3>
                    <div class="chart-container">
                        <canvas id="userAccuracyChart"></canvas>
                    </div>
                    <div style="text-align:center;margin-top:15px;font-size:32px;font-weight:800;color:var(--primary);">
                        {{ "%.1f"|format(stats.accuracy) }}%
                    </div>
                    <p style="text-align:center;color:var(--gray-600);font-size:13px;">AI correctly predicted your articles</p>
                </div>
            </div>
        </div>
        {% endif %}

        <div class="grid">
            <div class="card">
                <h2>📝 Submit Article</h2>
                <form method="POST">
                    <div class="form-group">
                        <label>Article Title</label>
                        <input type="text" name="title" required>
                    </div>
                    <div class="form-group">
                        <label>Article Text</label>
                        <textarea name="text" rows="8" required></textarea>
                    </div>
                    <button type="submit" class="btn" style="width:100%;justify-content:center;">🔍 Analyze</button>
                </form>
            </div>
            <div class="card">
                <h2>📋 My Submissions ({{ stats.total }})</h2>
                <div style="max-height:500px;overflow-y:auto;">
                    {% if articles_with_sources %}
                        {% for article in articles_with_sources %}
                            <div class="article-item">
                                <h3>{{ article.title }}</h3>
                                <div style="margin:10px 0;">
                                    <span class="badge {% if article.ml_prediction == 'Fake' %}badge-fake{% else %}badge-real{% endif %}">
                                        🤖 ML: {{ article.ml_prediction }} ({{ "%.0f"|format(article.ml_confidence * 100) }}%)
                                    </span>
                                </div>
                                {% if article.status == 'pending' %}
                                    <span class="badge badge-pending">⏳ Pending</span>
                                {% else %}
                                    <span class="badge {% if article.final_verdict == 'Fake' %}badge-fake{% else %}badge-real{% endif %}">
                                        ✅ {{ article.final_verdict }} (Reviewed)
                                    </span>
                                    <div class="sources-box">
                                        <strong>📚 Reliable Sources:</strong>
                                        <ul>
                                            {% for source in article.parsed_sources %}
                                                <li><a href="{{ source.uri }}" target="_blank">{{ source.title }}</a></li>
                                            {% endfor %}
                                        </ul>
                                    </div>
                                {% endif %}
                            </div>
                        {% endfor %}
                    {% else %}
                        <p style="color:var(--gray-600); text-align:center; padding:20px;">No articles submitted yet.</p>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            var userPieCtx = document.getElementById('userPieChart');
            var userAccuracyCtx = document.getElementById('userAccuracyChart');

            if (userPieCtx && userAccuracyCtx) {
                // User Verdict Chart (Pie)
                new Chart(userPieCtx, {
                    type: 'pie',
                    data: {
                        labels: ['Real', 'Fake'],
                        datasets: [{
                            data: [{{ stats.real }}, {{ stats.fake }}],
                            backgroundColor: ['#10B981', '#EF4444'],
                            hoverOffset: 4
                        }]
                    },
                    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } }
                });

                // User Accuracy Chart (Gauge)
                new Chart(userAccuracyCtx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Correct', 'Incorrect'],
                        datasets: [{
                            data: [{{ stats.accuracy | int }}, {{ 100 - (stats.accuracy | int) }}],
                            backgroundColor: ['#2563EB', '#E5E7EB'],
                            borderWidth: 0
                        }]
                    },
                    options: {
                        responsive: true, maintainAspectRatio: false, cutout: '80%',
                        plugins: { legend: { display: false }, tooltip: { enabled: false } },
                        rotation: -90, circumference: 180, 
                    }
                });
            }
        });
    </script>
    ''')
    return render_template_string(html, user=user, articles_with_sources=articles_with_sources, stats=stats)


@app.route('/reviewer/dashboard', methods=['GET', 'POST'])
def reviewer_dashboard():
    if 'user_id' not in session or session.get('user_role') != 'reviewer':
        return redirect(url_for('login'))

    conn = sqlite3.connect('fake_news_detection.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    if request.method == 'POST':
        article_id = request.form.get('article_id')
        action = request.form.get('action')

        if action == 'review':
            final_verdict = request.form['final_verdict']
            needs_admin_review = 1 if request.form.get('needs_admin_review') == 'on' else 0 
            
            c.execute('''UPDATE articles SET status = 'reviewed', final_verdict = ?,
                         reviewed_by = ?, reviewed_at = ?, needs_admin_review = ?
                         WHERE id = ?''',
                      (final_verdict, session['user_id'], datetime.now().isoformat(), needs_admin_review, article_id))
            flash('Article reviewed successfully!')
        elif action == 'dismiss_admin_review': 
            c.execute('''UPDATE articles SET needs_admin_review = 0 WHERE id = ? AND reviewed_by = ?''',
                      (article_id, session['user_id']))
            flash('Admin review request dismissed.')
        
        conn.commit()
        conn.close()
        return redirect(url_for('reviewer_dashboard'))

    c.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
    reviewer = c.fetchone()

    c.execute('''SELECT a.*, u.name as submitted_by_name FROM articles a
                 JOIN users u ON a.submitted_by = u.id
                 WHERE a.status = 'pending' ORDER BY a.submitted_at DESC''')
    pending_articles = c.fetchall()

    c.execute('''SELECT a.*, u.name as submitted_by_name FROM articles a
                 JOIN users u ON a.submitted_by = u.id
                 WHERE a.reviewed_by = ? ORDER BY a.reviewed_at DESC''', (session['user_id'],))
    reviewed_articles_by_reviewer = c.fetchall()

    total_reviewed = len(reviewed_articles_by_reviewer)
    marked_for_admin_review = len([a for a in reviewed_articles_by_reviewer if a['needs_admin_review'] == 1 and a['admin_verified'] == 0])
    
    reviewer_ai_correct = len([a for a in reviewed_articles_by_reviewer if a['ml_prediction'] == a['final_verdict']])
    reviewer_accuracy_rate = (reviewer_ai_correct / total_reviewed * 100) if total_reviewed > 0 else 0

    reviewer_verdict_counts = {'Real': 0, 'Fake': 0}
    for article in reviewed_articles_by_reviewer:
        if article['final_verdict'] in reviewer_verdict_counts:
            reviewer_verdict_counts[article['final_verdict']] += 1

    ml_prediction_counts = {'Real': 0, 'Fake': 0}
    for article in pending_articles + reviewed_articles_by_reviewer:
        if article['ml_prediction'] in ml_prediction_counts:
            ml_prediction_counts[article['ml_prediction']] += 1
            
    conn.close()

    stats = {
        'total_pending': len(pending_articles),
        'total_reviewed_by_reviewer': total_reviewed,
        'marked_for_admin_review': marked_for_admin_review,
        'reviewer_accuracy': reviewer_accuracy_rate
    }
    
    pending_articles_with_sources = []
    for article in pending_articles:
        a = dict(article)
        try: a['parsed_sources'] = json.loads(a['reliable_source_json'])
        except: a['parsed_sources'] = []
        pending_articles_with_sources.append(a)

    reviewed_by_reviewer_with_sources = []
    for article in reviewed_articles_by_reviewer:
        a = dict(article)
        try: a['parsed_sources'] = json.loads(a['reliable_source_json'])
        except: a['parsed_sources'] = []
        reviewed_by_reviewer_with_sources.append(a)

    # HTML for Reviewer Dashboard (including analytics charts)
    html = BASE_HTML.replace('{% block content %}{% endblock %}', '''
    <div class="navbar">
        <h1>Reviewer Dashboard</h1>
        <div class="user-info">
            <span>🕵️‍♀️ {{ reviewer.name }}</span>
            <a href="{{ url_for('logout') }}" class="btn btn-danger">Logout</a>
        </div>
    </div>
    <div class="container">
        {% with messages = get_flashed_messages() %}{% if messages %}{% for message in messages %}<div class="alert alert-success">{{ message }}</div>{% endfor %}{% endif %}{% endwith %}

        <div class="grid" style="margin-bottom:30px;">
            <div class="stat-card">
                <h3>Pending Articles</h3>
                <div class="number" style="background:linear-gradient(135deg,var(--warning),#d97706);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{{ stats.total_pending }}</div>
                <small>Awaiting your review</small>
            </div>
            <div class="stat-card">
                <h3>Total Reviewed</h3>
                <div class="number" style="background:linear-gradient(135deg,var(--success),#059669);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{{ stats.total_reviewed_by_reviewer }}</div>
                <small>Articles you have verified</small>
            </div>
            <div class="stat-card">
                <h3>For Admin Review</h3>
                <div class="number" style="background:linear-gradient(135deg,#60a5fa,#3b82f6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{{ stats.marked_for_admin_review }}</div>
                <small>Flagged for admin verification</small>
            </div>
        </div>

        
        <div class="card">
            <h2>📊 Reviewer Analytics</h2>
            <div class="grid">
                <div>
                    <h3 style="color:var(--gray-700);margin-bottom:15px;">Your Verdicts Distribution (Real vs. Fake)</h3>
                    <div class="chart-container">
                        <canvas id="reviewerVerdictChart"></canvas>
                    </div>
                    <div style="text-align:center;margin-top:15px;">
                        <span class="badge badge-real">{{ reviewer_verdict_counts.Real }} Real</span>
                        <span class="badge badge-fake">{{ reviewer_verdict_counts.Fake }} Fake</span>
                    </div>
                </div>
                <div>
                    <h3 style="color:var(--gray-700);margin-bottom:15px;">Overall ML Prediction on All Articles Seen</h3>
                    <div class="chart-container">
                        <canvas id="reviewerMLPredictionChart"></canvas>
                    </div>
                    <div style="text-align:center;margin-top:15px;">
                        <span class="badge badge-real" style="background:linear-gradient(135deg, #dbeafe, #93c5fd); color:#1e40af; border:2px solid #3b82f6;">{{ ml_prediction_counts.Real }} ML Real</span>
                        <span class="badge badge-fake" style="background:linear-gradient(135deg, #fef3c7, #fde68a); color:#92400e; border:2px solid #f59e0b;">{{ ml_prediction_counts.Fake }} ML Fake</span>
                    </div>
                </div>
            </div>
            <div class="feature-highlight">
                ✨ The AI accuracy (ML vs. Your Verdicts) is <b>{{ "%.1f"|format(stats.reviewer_accuracy) }}%</b>.
            </div>
        </div>

        <div class="card">
            <h2>⏳ Articles Pending Your Review ({{ stats.total_pending }})</h2>
            {% if pending_articles_with_sources %}
                {% for article in pending_articles_with_sources %}
                    <div class="article-item" style="border-color:var(--warning);">
                        <h3>{{ article.title }} <span style="font-size:12px;color:var(--gray-600);">by {{ article.submitted_by_name }} on {{ article.submitted_at.split('T')[0] }}</span></h3>
                        <p style="color:var(--gray-700); font-size:14px; margin-top:10px;">{{ article.text[:200] }}...</p>
                        <div style="margin:10px 0;">
                            <span class="badge {% if article.ml_prediction == 'Fake' %}badge-fake{% else %}badge-real{% endif %}">
                                🤖 ML Prediction: {{ article.ml_prediction }} ({{ "%.0f"|format(article.ml_confidence * 100) }}%)
                            </span>
                        </div>
                        <div class="sources-box">
                            <strong>📚 Reliable Sources Found:</strong>
                            <ul>
                                {% for source in article.parsed_sources %}
                                    <li><a href="{{ source.uri }}" target="_blank">{{ source.title }}</a></li>
                                {% endfor %}
                            </ul>
                        </div>
                        <form method="POST" style="margin-top:20px;">
                            <input type="hidden" name="article_id" value="{{ article.id }}">
                            <input type="hidden" name="action" value="review">
                            <div class="form-group">
                                <label>Final Verdict</label>
                                <select name="final_verdict">
                                    <option value="Real">Real News (Verified)</option>
                                    <option value="Fake">Fake News (Misinformation)</option>
                                </select>
                            </div>
                            <div class="form-group" style="display:flex; align-items:center; gap:10px;">
                                <input type="checkbox" name="needs_admin_review" id="admin_review_{{ article.id }}" style="width:20px; height:20px;">
                                <label for="admin_review_{{ article.id }}" style="margin-bottom:0; font-weight:500;">Flag for Admin Review (High Importance/Controversy)</label>
                            </div>
                            <button type="submit" class="btn btn-success" style="width:100%;justify-content:center;">Submit Verification</button>
                        </form>
                    </div>
                {% endfor %}
            {% else %}
                <p style="color:var(--gray-600); text-align:center; padding:20px;">🎉 No articles are currently pending your review.</p>
            {% endif %}
        </div>
        
        <div class="card">
            <h2>✅ My Reviewed Articles ({{ stats.total_reviewed_by_reviewer }})</h2>
            {% if reviewed_by_reviewer_with_sources %}
                {% for article in reviewed_by_reviewer_with_sources %}
                    <div class="article-item" style="border-color:{% if article.needs_admin_review and article.admin_verified == 0 %}#3b82f6{% elif article.final_verdict == 'Fake' %}var(--danger){% else %}var(--success){% endif %};">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <h3>{{ article.title }}</h3>
                            {% if article.admin_verified == 1 %}
                                <span class="badge" style="background:linear-gradient(135deg,#dbeafe,#93c5fd); color:#1e40af; border:2px solid #3b82f6;">
                                    👑 Admin Finalized: {{ article.final_verdict }}
                                </span>
                            {% elif article.needs_admin_review == 1 %}
                                <span class="badge" style="background:linear-gradient(135deg,#fef3c7,#fde68a); color:#92400e; border:2px solid #f59e0b;">
                                    🚨 Admin Check Requested
                                </span>
                            {% else %}
                                <span class="badge {% if article.final_verdict == 'Fake' %}badge-fake{% else %}badge-real{% endif %}">
                                    ✅ Final Verdict: {{ article.final_verdict }}
                                </span>
                            {% endif %}
                        </div>
                        <p style="font-size:12px; color:var(--gray-600); margin-top:5px;">Reviewed on {{ article.reviewed_at.split('T')[0] }}</p>
                        {% if article.needs_admin_review and article.admin_verified == 0 %}
                            <form method="POST" style="margin-top:10px;">
                                <input type="hidden" name="article_id" value="{{ article.id }}">
                                <input type="hidden" name="action" value="dismiss_admin_review">
                                <button type="submit" class="btn" style="background:var(--gray-600); padding:8px 15px; font-size:12px; border-radius:8px; box-shadow:none;">Dismiss Admin Review Request</button>
                            </form>
                        {% endif %}
                    </div>
                {% endfor %}
            {% else %}
                <p style="color:var(--gray-600); text-align:center; padding:20px;">Start reviewing articles to see them here.</p>
            {% endif %}
        </div>
    </div>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Reviewer Verdict Chart (Pie)
            new Chart(document.getElementById('reviewerVerdictChart'), {
                type: 'pie',
                data: {
                    labels: ['Real News', 'Fake News'],
                    datasets: [{
                        data: [{{ reviewer_verdict_counts.Real }}, {{ reviewer_verdict_counts.Fake }}],
                        backgroundColor: ['#10B981', '#EF4444'],
                        hoverOffset: 4
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } }
            });

            // Reviewer ML Prediction Chart (Doughnut)
            new Chart(document.getElementById('reviewerMLPredictionChart'), {
                type: 'doughnut',
                data: {
                    labels: ['ML Real', 'ML Fake'],
                    datasets: [{
                        data: [{{ ml_prediction_counts.Real }}, {{ ml_prediction_counts.Fake }}],
                        backgroundColor: ['#3B82F6', '#F59E0B'],
                        hoverOffset: 4
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false, cutout: '70%', plugins: { legend: { position: 'bottom' } } }
            });
        });
    </script>
    ''')
    return render_template_string(html, reviewer=reviewer, pending_articles_with_sources=pending_articles_with_sources, 
                                  reviewed_by_reviewer_with_sources=reviewed_by_reviewer_with_sources, stats=stats, 
                                  reviewer_verdict_counts=reviewer_verdict_counts, ml_prediction_counts=ml_prediction_counts)

@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if 'user_id' not in session or session.get('user_role') != 'admin':
        return redirect(url_for('login'))

    conn = sqlite3.connect('fake_news_detection.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    if request.method == 'POST':
        article_id = request.form.get('article_id')
        action = request.form.get('action')

        if action == 'admin_verify':
            admin_verdict = request.form['admin_verdict']
            
            c.execute('''UPDATE articles SET admin_verified = 1, final_verdict = ?, status = 'admin_reviewed',
                         admin_verified_by = ?, admin_verified_at = ?, needs_admin_review = 0
                         WHERE id = ?''',
                      (admin_verdict, session['user_id'], datetime.now().isoformat(), article_id))
            flash('Article administratively verified successfully!')
        
        conn.commit()
        conn.close()
        return redirect(url_for('admin_dashboard'))

    # --- Fetch Data for Analytics and Display ---
    
    c.execute('SELECT * FROM users WHERE role = "reviewer"')
    reviewers = c.fetchall()
    
    c.execute('SELECT * FROM articles')
    all_articles = c.fetchall()
    
    c.execute('SELECT COUNT(*) FROM users')
    total_users = c.fetchone()[0]
    conn.close()

    # 1. Status Distribution 
    total_articles = len(all_articles)
    pending_count = len([a for a in all_articles if a['status'] == 'pending'])
    reviewed_count = len([a for a in all_articles if a['status'] == 'reviewed'])
    admin_reviewed_count = len([a for a in all_articles if a['status'] == 'admin_reviewed'])
    needs_admin_review_count = len([a for a in all_articles if a['needs_admin_review'] == 1 and a['admin_verified'] == 0])
    
    # 2. ML Prediction & Final Verdict Distribution
    ml_prediction_counts = {'Real': 0, 'Fake': 0}
    final_verdict_counts = {'Real': 0, 'Fake': 0}
    
    reviewed_articles = [a for a in all_articles if a['status'] != 'pending']
    
    for article in all_articles:
        if article['ml_prediction'] in ml_prediction_counts:
            ml_prediction_counts[article['ml_prediction']] += 1

    for article in reviewed_articles:
        if article['final_verdict'] in final_verdict_counts:
            final_verdict_counts[article['final_verdict']] += 1
            
    total_final_verdicts = sum(final_verdict_counts.values())
    
    # 3. ML Accuracy (vs. Final Human Verdict)
    ai_correct_count = len([a for a in reviewed_articles if a['ml_prediction'] == a['final_verdict']])
    ml_accuracy_rate = (ai_correct_count / total_final_verdicts * 100) if total_final_verdicts > 0 else 0

    # 4. Reviewer Activity
    reviewer_activity = {}
    for reviewer in reviewers:
        reviewer_id = reviewer['id']
        reviewed_count_by_reviewer = len([a for a in reviewed_articles if a['reviewed_by'] == reviewer_id]) 
        reviewer_activity[reviewer['name']] = reviewed_count_by_reviewer

    # 5. Articles Requiring Admin Review (List)
    conn = sqlite3.connect('fake_news_detection.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''SELECT a.*, u.name as submitted_by_name, r.name as reviewed_by_name FROM articles a
                 JOIN users u ON a.submitted_by = u.id
                 LEFT JOIN users r ON a.reviewed_by = r.id
                 WHERE a.needs_admin_review = 1 AND a.admin_verified = 0 ORDER BY a.reviewed_at DESC''')
    admin_review_articles = c.fetchall()
    conn.close()

    admin_review_articles_with_sources = []
    for article in admin_review_articles:
        a = dict(article)
        try: a['parsed_sources'] = json.loads(a['reliable_source_json'])
        except: a['parsed_sources'] = []
        admin_review_articles_with_sources.append(a)

    admin_stats = {
        'total_users': total_users,
        'total_reviewers': len(reviewers),
        'total_articles': total_articles,
        'pending_review': pending_count,
        'needs_admin_review': needs_admin_review_count,
        'ml_accuracy': ml_accuracy_rate,
        'reviewed_total': total_final_verdicts
    }

    # --- HTML & Visualization Setup ---
    html = BASE_HTML.replace('{% block content %}{% endblock %}', '''
    <div class="navbar">
        <h1>Admin Dashboard</h1>
        <div class="user-info">
            <span>👑 {{ session.user_name }}</span>
            <a href="{{ url_for('logout') }}" class="btn btn-danger">Logout</a>
        </div>
    </div>
    <div class="container">
        {% with messages = get_flashed_messages() %}{% if messages %}{% for message in messages %}<div class="alert alert-success">{{ message }}</div>{% endfor %}{% endif %}{% endwith %}

        <div class="grid" style="margin-bottom:30px;">
            <div class="stat-card">
                <h3>Total Articles</h3>
                <div class="number">{{ admin_stats.total_articles }}</div>
                <small>Total submissions in the system</small>
            </div>
            <div class="stat-card">
                <h3>Pending Review</h3>
                <div class="number" style="background:linear-gradient(135deg,var(--warning),#d97706);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{{ admin_stats.pending_review }}</div>
                <small>Awaiting first human review</small>
            </div>
            <div class="stat-card">
                <h3>Needs Admin Check</h3>
                <div class="number" style="background:linear-gradient(135deg,#60a5fa,#3b82f6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{{ admin_stats.needs_admin_review }}</div>
                <small>Articles flagged by Reviewers</small>
            </div>
            <div class="stat-card">
                <h3>Total Users</h3>
                <div class="number" style="background:linear-gradient(135deg,var(--secondary),#5b21b6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{{ admin_stats.total_users }}</div>
                <small>Registered accounts</small>
            </div>
        </div>

        <div class="card">
            <h2>🌍 System-Wide Analytics</h2>
            <div class="grid" style="grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));">
                <div>
                    <h3 style="color:var(--gray-700);margin-bottom:15px;">Article Status Distribution</h3>
                    <div class="chart-container"><canvas id="adminStatusChart"></canvas></div>
                </div>

                <div>
                    <h3 style="color:var(--gray-700);margin-bottom:15px;">Final Human Verdicts ({{ admin_stats.reviewed_total }})</h3>
                    <div class="chart-container"><canvas id="adminVerdictChart"></canvas></div>
                </div>
            </div>

            <div class="grid" style="grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); margin-top:30px;">
                <div>
                    <h3 style="color:var(--gray-700);margin-bottom:15px;">ML Model Accuracy vs. Human Verdict</h3>
                    <div class="chart-container">
                        <canvas id="adminAccuracyChart"></canvas>
                        <div style="text-align:center;margin-top:15px;font-size:36px;font-weight:800;color:var(--primary);">
                            {{ "%.1f"|format(admin_stats.ml_accuracy) }}%
                        </div>
                        <p style="text-align:center;color:var(--gray-600);font-size:13px;">AI Model's Success Rate</p>
                    </div>
                </div>

                <div>
                    <h3 style="color:var(--gray-700);margin-bottom:15px;">Reviewer Activity</h3>
                    <div class="chart-container" style="height:350px;"><canvas id="adminReviewerActivityChart"></canvas></div>
                </div>
            </div>
        </div>

        <div class="card">
            <h2>🚨 Articles Requiring Administrative Verification ({{ admin_stats.needs_admin_review }})</h2>
            {% if admin_review_articles_with_sources %}
                {% for article in admin_review_articles_with_sources %}
                    <div class="article-item" style="border-color:#3b82f6;">
                        <h3>{{ article.title }} 
                            <span style="font-size:12px;color:var(--gray-600);">
                                Submitted by: {{ article.submitted_by_name }} | Reviewed by: {{ article.reviewed_by_name }}
                            </span>
                        </h3>
                        <p style="color:var(--gray-700); font-size:14px; margin-top:10px;">{{ article.text[:200] }}...</p>
                        <div style="margin:10px 0;">
                            <span class="badge {% if article.ml_prediction == 'Fake' %}badge-fake{% else %}badge-real{% endif %}">
                                🤖 ML: {{ article.ml_prediction }} ({{ "%.0f"|format(article.ml_confidence * 100) }}%)
                            </span>
                            <span class="badge {% if article.final_verdict == 'Fake' %}badge-danger{% else %}badge-success{% endif %}" style="margin-left:10px;">
                                ✍️ Reviewer Verdict: {{ article.final_verdict }}
                            </span>
                        </div>

                        <form method="POST" style="margin-top:20px; display:flex; gap:10px; align-items:flex-end;">
                            <input type="hidden" name="article_id" value="{{ article.id }}">
                            <input type="hidden" name="action" value="admin_verify">
                            <div class="form-group" style="flex-grow:1; margin-bottom:0;">
                                <label style="font-weight:600; font-size:13px;">Admin Final Verdict</label>
                                <select name="admin_verdict">
                                    <option value="Real">Real News (Final Admin Veto)</option>
                                    <option value="Fake">Fake News (Final Admin Veto)</option>
                                </select>
                            </div>
                            <button type="submit" class="btn btn-primary" style="padding:15px 30px; margin-bottom:0; flex-shrink:0;">Finalize & Publish</button>
                        </form>
                    </div>
                {% endfor %}
            {% else %}
                <p style="color:var(--gray-600); text-align:center; padding:20px;">All articles have been reviewed. System is clean!</p>
            {% endif %}
        </div>
    </div>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Chart 1: Article Status Distribution
            new Chart(document.getElementById('adminStatusChart'), {
                type: 'pie',
                data: {
                    labels: ['Pending', 'Reviewed by Reviewer', 'Admin Reviewed'],
                    datasets: [{
                        data: [{{ pending_count }}, {{ reviewed_count }}, {{ admin_reviewed_count }}],
                        backgroundColor: ['#F59E0B', '#10B981', '#3B82F6'],
                        hoverOffset: 4
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } }
            });

            // Chart 2: Final Verdict Distribution
            new Chart(document.getElementById('adminVerdictChart'), {
                type: 'doughnut',
                data: {
                    labels: ['Real News', 'Fake News'],
                    datasets: [{
                        data: [{{ final_verdict_counts.Real }}, {{ final_verdict_counts.Fake }}],
                        backgroundColor: ['#10B981', '#EF4444'],
                        hoverOffset: 4
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false, cutout: '70%', plugins: { legend: { position: 'bottom' } } }
            });

            // Chart 3: ML Accuracy (Gauge)
            new Chart(document.getElementById('adminAccuracyChart'), {
                type: 'doughnut',
                data: {
                    labels: ['Correct', 'Incorrect'],
                    datasets: [{
                        data: [{{ admin_stats.ml_accuracy | int }}, {{ 100 - (admin_stats.ml_accuracy | int) }}],
                        backgroundColor: ['#2563EB', '#E5E7EB'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true, maintainAspectRatio: false, cutout: '80%',
                    plugins: { legend: { display: false }, tooltip: { enabled: false } },
                    rotation: -90, circumference: 180,
                }
            });

            // Chart 4: Reviewer Activity Bar Chart
            const reviewerNames = {{ reviewer_activity.keys() | list | tojson }};
            const reviewedCounts = {{ reviewer_activity.values() | list | tojson }};

            new Chart(document.getElementById('adminReviewerActivityChart'), {
                type: 'bar',
                data: {
                    labels: reviewerNames,
                    datasets: [{
                        label: 'Articles Reviewed',
                        data: reviewedCounts,
                        backgroundColor: '#7c3aed',
                        borderRadius: 8,
                    }]
                },
                options: {
                    responsive: true, maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { beginAtZero: true, title: { display: true, text: 'Number of Articles' } },
                        x: { grid: { display: false } }
                    }
                }
            });
        });
    </script>
    ''')
    
    return render_template_string(html, admin_stats=admin_stats, pending_count=pending_count, reviewed_count=reviewed_count, 
                                  admin_reviewed_count=admin_reviewed_count, final_verdict_counts=final_verdict_counts, 
                                  admin_review_articles_with_sources=admin_review_articles_with_sources, 
                                  reviewer_activity=reviewer_activity)

if __name__ == '__main__':
    # Initial setup for the database and default users
    init_db()
    app.run(debug=True)