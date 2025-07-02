from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import psycopg2
import os
import pickle
import bcrypt
import numpy as np
from werkzeug.security import check_password_hash
from database import connect
import student_data  # Optional helper

# Custom template/static path
template_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'web_app', 'templates'))
static_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'web_app', 'static'))
app = Flask(__name__, template_folder=template_path, static_folder=static_path)
app.secret_key = "your_secret_key"

# Load ML model
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
model_path = os.path.join(base_dir, 'models', 'student_model.pkl')
model = pickle.load(open(model_path, 'rb'))

# ========== Home ==========
@app.route('/')
def home():
    return render_template('home.html')


# ========== Login ==========
@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def api_login():
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


# ========== Register ==========
# === Keep your GET route as is ===
@app.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')

# === Updated POST route ===
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    print("Received data:", data)   # ✅ Debug

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

    cur.execute("""
        SELECT id FROM students 
        WHERE email = %s OR username = %s OR roll_no = %s OR phone = %s
    """, (email, username, roll_no, phone))

    if cur.fetchone():
        print("Duplicate detected.")   # ✅ Debug
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
    print("Student inserted successfully.")   # ✅ Debug

    flash("Student registered successfully! Please log in.")
    return redirect(url_for('login'))


# ========== Logout ==========
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


# ========== Prediction ==========
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    prediction = None
    if request.method == 'POST':
        attendance = float(request.form['attendance'])
        internal_marks = float(request.form['internal_marks'])
        input_data = np.array([[attendance, internal_marks]])
        prediction =float(round(model.predict(input_data)[0], 2))

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


# ========== Admin Dashboard ==========
@app.route('/dashboard')
def dashboard():
    if session.get('username') != 'admin':
        return redirect(url_for('home'))

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

    return render_template('dashboard.html', users=users, predictions=predictions)


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
            return jsonify({"message": "Admin login successful!"}) if request.is_json else redirect(url_for('dashboard'))
        else:
            message = "Invalid admin credentials"
            return jsonify({"error": message}), 401 if request.is_json else flash(message) or redirect(url_for('admin_login'))

    return render_template('admin_login.html')


@app.route('/admin/delete_user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM students WHERE id = %s", (user_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "User deleted successfully"})

@app.route('/admin/delete_prediction/<int:prediction_id>', methods=['DELETE'])
def delete_prediction(prediction_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM predictions WHERE id = %s", (prediction_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Prediction deleted successfully"})


# ========== Run App ==========
if __name__ == '__main__':
    app.run(debug=True)
