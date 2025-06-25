# app.py (updated full version for login, register, home, predict, dashboard)

from flask import Flask, render_template, request, redirect, url_for, session, flash,jsonify
import psycopg2, os
import pickle
import numpy as np
import student_data  # assuming this contains register_student()
from database import connect

# Custom template/static path
template_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'web_app', 'templates'))
static_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'web_app', 'static'))
app = Flask(__name__, template_folder=template_path, static_folder=static_path)
app.secret_key = "your_secret_key"

# Load trained model
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
model_path = os.path.join(base_dir, 'models', 'student_model.pkl')
model = pickle.load(open(model_path, 'rb'))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            session['username'] = username
            session['user_id'] = user[0]  # store user ID for later use
            return redirect(url_for('home'))
        else:
            flash('Invalid login')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    name = data.get('name')
    email = data.get('email')
    address = data.get('address')
    semester = data.get('semester')
    roll_no = data.get('roll_no')  # Required, but missing in your Postman JSON

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO students (name, email, address, semester, roll_no)
        VALUES (%s, %s, %s, %s, %s)
    """, (name, email, address, semester, roll_no))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Student registered successfully!"})


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    prediction = None
    if request.method == 'POST':
        attendance = float(request.form['attendance'])
        internal_marks = float(request.form['internal_marks'])
        input_data = np.array([[attendance, internal_marks]])
        prediction = round(model.predict(input_data)[0], 2)

        # save prediction to DB
        conn = connect()
        cur = conn.cursor()
        cur.execute("INSERT INTO predictions (user_id, attendance, internal_marks, prediction) VALUES (%s, %s, %s, %s)",
                    (session.get('user_id'), attendance, internal_marks, prediction))
        conn.commit()
        cur.close()
        conn.close()

    return render_template('predict.html', prediction=prediction)

@app.route('/dashboard')
def dashboard():
    if session.get('username') != 'admin':
        return redirect(url_for('home'))

    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT id, username FROM users")
    users = cur.fetchall()

    cur.execute("SELECT p.id, u.username, p.attendance, p.internal_marks, p.prediction FROM predictions p JOIN users u ON p.user_id = u.id")
    predictions = cur.fetchall()

    cur.close()
    conn.close()
    return render_template('dashboard.html', users=users, predictions=predictions)

if __name__ == '__main__':
    app.run(debug=True)
