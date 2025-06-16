import psycopg2

def connect():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="student_performance",  
            user="postgres",               
            password="root"        
        )
        print("Database connection successful.")
        return conn
    except Exception as e:
        print("Database connection failed:", e)
        return None

# Run this block only when this script is executed directly
if __name__ == "__main__":
    connect()
