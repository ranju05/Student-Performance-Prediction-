from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import psycopg2
import os
import pickle
import bcrypt
import numpy as np
from werkzeug.security import check_password_hash
from database import connect
import student_data  # Optional helper

# ========== Flask Setup ==========
template_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'web_app', 'templates'))
static_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'web_app', 'static'))
app = Flask(__name__, template_folder=template_path, static_folder=static_path)
app.secret_key = "your_secret_key"

# ========== Load ML Model ==========
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
model_path = os.path.join(base_dir, 'src', 'models', 'student_model.pkl')
try:
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
except FileNotFoundError:
    model = None
    print("⚠️ Warning: student_model.pkl not found. Prediction will not work.")

# ========== Home ==========
@app.route('/')
def home():
    return render_template('home.html')

# ========== Student Registration ==========
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        username = data.get('username')
        email = data.get('email')
        phone = data.get('phone')
        password = data.get('password')
        address = data.get('address')
        semester = data.get('semester')
        roll_no = data.get('roll_no')

        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        conn = connect()
        cur = conn.cursor()
        cur.execute("SELECT id FROM students WHERE email = %s OR username = %s OR roll_no = %s OR phone = %s",
                    (email, username, roll_no, phone))
        if cur.fetchone():
            cur.close()
            conn.close()
            return jsonify({"message": "Email, username, roll number, or phone already exists."}), 400

        cur.execute("""
            INSERT INTO students (name, username, password, email, address, semester, roll_no, phone)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (name, username, hashed_pw, email, address, semester, roll_no, phone))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Registration successful! Please log in."})

    return render_template('register.html')

# ========== Student Login ==========
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        conn = connect()
        cur = conn.cursor()
        cur.execute("SELECT id, email, password, username FROM students WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
            session['user_id'] = user[0]
            session['email'] = user[1]
            session['username'] = user[3]
            return jsonify({"message": "Login successful!"})
        else:
            return jsonify({"message": "Invalid credentials"}), 401

    return render_template('login.html')

# ========== Student Dashboard ==========
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please log in to view your student dashboard.")
        return redirect(url_for('login'))

    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, attendance, internal_marks, prediction
        FROM predictions
        WHERE user_id = %s
        ORDER BY id DESC
    """, (session.get('user_id'),))
    predictions = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('student_dashboard.html', predictions=predictions)

# ========== Prediction ==========
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if 'user_id' not in session:
        flash("Please log in to access prediction.")
        return redirect(url_for('login'))

    prediction = None
    if request.method == 'POST':
        if model is None:
            flash("Prediction model not available.")
            return redirect(url_for('predict'))

        attendance = float(request.form['attendance'])
        internal_marks = float(request.form['internal_marks'])
        input_data = np.array([[attendance, internal_marks]])
        prediction = float(round(model.predict(input_data)[0], 2))

        conn = connect()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO predictions (user_id, attendance, internal_marks, prediction)
            VALUES (%s, %s, %s, %s)
        """, (session.get('user_id'), attendance, internal_marks, prediction))
        conn.commit()
        cur.close()
        conn.close()

    return render_template('predict.html', prediction=prediction)
@app.route('/home')
def home_page():
    return render_template('home.html')


# ========== Logout ==========
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for('login'))

# ========== Admin Login ==========
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
        else:
            username = request.form.get('username')
            password = request.form.get('password')

        conn = connect()
        cur = conn.cursor()
        cur.execute("SELECT password FROM admins WHERE username = %s", (username,))
        result = cur.fetchone()
        cur.close()
        conn.close()

        if result and check_password_hash(result[0], password):
            session['admin_logged_in'] = True
            session['username'] = 'admin'
            return jsonify({"message": "Admin login successful!"}) if request.is_json else redirect(url_for('admin_dashboard'))
        else:
            message = "Invalid admin credentials."
            if request.is_json:
                return jsonify({"error": message}), 401
            else:
                flash(message)
                return redirect(url_for('admin_login'))

    return render_template('admin_login.html')

# ========== Admin Dashboard ==========
@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        flash("Please log in as admin.")
        return redirect(url_for('admin_login'))

    section = request.args.get('section', 'overview')

    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT id, username FROM students")
    users = cur.fetchall()
    cur.execute("""
        SELECT p.id, s.username, p.attendance, p.internal_marks, p.prediction
        FROM predictions p
        JOIN students s ON p.user_id = s.id
    """)
    predictions = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('admin_dashboard.html', section=section, users=users, predictions=predictions)

# ========== Admin Delete Operations ==========
@app.route('/admin/delete_user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    if not session.get('admin_logged_in'):
        return jsonify({"error": "Unauthorized"}), 401

    conn = connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM students WHERE id = %s", (user_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "User deleted successfully."})

@app.route('/admin/delete_prediction/<int:prediction_id>', methods=['DELETE'])
def delete_prediction(prediction_id):
    if not session.get('admin_logged_in'):
        return jsonify({"error": "Unauthorized"}), 401

    conn = connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM predictions WHERE id = %s", (prediction_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Prediction deleted successfully."})
# ========== Admin Logout ==========
@app.route('/admin_logout')
def admin_logout():
    session.clear()
    flash("Admin logged out successfully.")
    return redirect(url_for('admin_login'))


# ========== Run App ==========
if __name__ == '__main__':
    app.run(debug=True)