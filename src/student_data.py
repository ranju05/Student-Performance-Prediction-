from werkzeug.security import generate_password_hash, check_password_hash
from database import connect
def register_student(name, email, username, password, semester, roll_no, address):
    hashed_password = generate_password_hash(password)
    conn = connect()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO students (name, email, username, password, semester, roll_no, address)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (name, email, username, hashed_password, semester, roll_no, address))
        conn.commit()
        return True
    except Exception as e:
        print("❌ Error registering student:", e)
        return False
    finally:
        cur.close()
        conn.close()