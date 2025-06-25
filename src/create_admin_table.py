from database import connect

def create_admin_table():
    conn = connect()
    cur = conn.cursor()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL, 
                password VARCHAR(255) NOT NULL
            );
        """)
        conn.commit()
        print("'admins' table created successfully.")
    except Exception as e:
        print("Failed to create 'admins' table:", e)
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    create_admin_table()
