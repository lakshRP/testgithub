from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import uuid
import subprocess
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
app.secret_key = 'secret_key'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __init__(self, email, password, name):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    feedback_text = db.Column(db.Text, nullable=False)
    session_id = db.Column(db.String(100), nullable=False)  # New column

    def __init__(self, user_id, feedback_text, session_id):
        self.user_id = user_id
        self.feedback_text = feedback_text
        self.session_id = session_id

# Store sessions in a dictionary (for simplicity)
sessionslist = {} 
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['email'] = user.email
            return redirect('/dashboard')
        else:
            error = 'Invalid email or password'
            return render_template('login.html', error=error)

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        return render_template('dashboard.html', user=user)

    return redirect('/login')

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect('/login')

@app.route('/createform')
def createform():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        return render_template('createform.html', user=user)

    return redirect('/login')

@app.route('/create_session', methods=['GET'])
def create_session():
    question = request.args.get('question')
    color = request.args.get('color')
    print(color, question)
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        user_email = user.email
    # Generate a unique session ID
    session_id = str(uuid.uuid4())
    # Store the session (for demo purposes, just storing in a dictionary)
    sessionslist[session_id] = {'status': 'active'}
    # Redirect to the session URL
    
    return redirect(url_for('teacher', session_id=session_id, teacher_email=user_email, question=question, color=color))

@app.route('/teacher/<teacher_email>/<session_id>/<question>/<color>')
def teacher(session_id, teacher_email, question, color):
    if 'email' in session:
        if teacher_email == session['email']:
            user = User.query.filter_by(email=session['email']).first()
            if session_id in sessionslist:
                feedbacks = Feedback.query.filter_by(session_id=session_id).all()  # Filter by session ID
                return render_template('analytics.html', user=user, session_id=session_id, question=question, color=color, feedbacks=feedbacks)
            else:
                return 'Session not found!', 404
    return redirect('/login')

@app.route('/join/<teacher_email>/<session_id>/<question>/<color>')
def join(session_id, teacher_email, question, color):
    if session_id in sessionslist:
        return render_template('form.html', teacher_email=teacher_email, session_id=session_id, question=question, color=color)
    else:
        return 'Session not found!', 404

@app.route('/submit_feedback/<teacher_email>/<session_id>', methods=['POST'])
def submit_feedback(session_id, teacher_email):
    feedback_text = request.form['feedback']
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        if user:
            new_feedback = Feedback(user_id=user.id, feedback_text=feedback_text, session_id=session_id)
            db.session.add(new_feedback)
            db.session.commit()
            return redirect(url_for('thank_you'))
    return redirect('/login')

@app.route('/thank_you')
def thank_you():
    return "Thank you for your feedback!"

@app.route('/summarize_feedback', methods=['POST'])
def summarize_feedback():
    data = request.get_json()
    feedbacks = data['feedbacks']
    
    # Call the summarization script
    summary = summarize(feedbacks)
    
    return jsonify({'summary': summary})

def summarize(feedbacks):
    import subprocess
    result = subprocess.run(['python', 'summarize.py'], input=json.dumps(feedbacks), text=True, capture_output=True)
    return result.stdout.strip()

if __name__ == '__main__':
    app.run(debug=True)
