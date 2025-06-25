from database import connect
from werkzeug.security import generate_password_hash

def create_admin():
    username = "Ranju"         # Admin username
    password = "ranju1"        # Admin password
    email = "ranju2@gmail.com" # Admin email
    hashed_password = generate_password_hash(password)

    conn = connect()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO admins (username, password, email)
            VALUES (%s, %s, %s)
        """, (username, hashed_password, email))
        conn.commit()
        print("Admin user created successfully.")
    except Exception as e:
        print("Failed to create admin user:", e)
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    create_admin()
