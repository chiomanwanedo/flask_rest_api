from flask import Flask, jsonify, render_template, request
import pymysql
import os

app = Flask(__name__)

# ✅ Use Environment Variables for Security (Set these in your EC2 instance)
DB_HOST = os.getenv("DB_HOST", "flask-mysql-db.czuqasgyocvc.eu-west-2.rds.amazonaws.com")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "123456789")  # ⚠️ Change this to an environment variable
DB_NAME = os.getenv("DB_NAME", "flask-mysql-db")

def get_db_connection():
    """Create a MySQL database connection with error handling."""
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            db='flask-mysql-db',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return None

@app.route('/health')
def health():
    return "✅ Up & Running"

@app.route('/create_table')
def create_table():
    """Create a MySQL table if it doesn't exist."""
    connection = get_db_connection()
    if connection is None:
        return "❌ Failed to connect to database"

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS example_table (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL
                )
            """)
            connection.commit()
        return "✅ Table created successfully"
    except Exception as e:
        return f"❌ Error creating table: {e}"
    finally:
        connection.close()

@app.route('/insert_record', methods=['POST'])
def insert_record():
    """Insert a new record into the MySQL table."""
    data = request.get_json()
    if "name" not in data:
        return jsonify({"error": "Missing 'name' field"}), 400

    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "Failed to connect to database"}), 500

    try:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO example_table (name) VALUES (%s)", (data["name"],))
            connection.commit()
        return jsonify({"message": "✅ Record inserted successfully!"}), 201
    except Exception as e:
        return jsonify({"error": f"❌ Error inserting record: {e}"}), 500
    finally:
        connection.close()

@app.route('/data', methods=['GET'])
def data():
    """Retrieve all records from the MySQL table."""
    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "Failed to connect to database"}), 500

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM example_table")
            result = cursor.fetchall()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"❌ Error fetching data: {e}"}), 500
    finally:
        connection.close()

@app.route('/')
def index():
    """Render the UI."""
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
