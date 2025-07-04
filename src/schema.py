# src/schema.py

from database import connect

def create_tables():
    conn = connect()
    cur = conn.cursor()
    cur.execute("""

           CREATE TABLE IF NOT EXISTS students (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            address VARCHAR(100) NOT NULL,
            semester VARCHAR(15) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            roll_no VARCHAR(50) UNIQUE NOT NULL,
            attendance FLOAT CHECK (attendance >= 0 AND attendance <= 100),
            internal_marks FLOAT CHECK (internal_marks >= 0 AND internal_marks <= 100),
            predicted_result VARCHAR(100),
            predicted_score FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)



    # Add this inside the create_tables() function in schema.py

    cur.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
            attendance FLOAT CHECK (attendance >= 0 AND attendance <= 100),
            internal_marks FLOAT CHECK (internal_marks >= 0 AND internal_marks <= 100),
            prediction FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Same CREATE TABLE statements here...

    conn.commit()
    cur.close()
    conn.close()
if __name__ == "__main__":
    create_tables()
