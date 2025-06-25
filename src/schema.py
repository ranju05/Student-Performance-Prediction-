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

    # Same CREATE TABLE statements here...

    conn.commit()
    cur.close()
    conn.close()
if __name__ == "__main__":
    create_tables()
