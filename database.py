import mysql.connector
from mysql.connector import Error

# MySQL Database Credentials
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "samyu@8306",
    "database": "hms"
}

def create_connection():
    """Establish a connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            print(" Connected to MySQL database")
            return connection
        else:
            print("❌ Connection failed")
            return None
    except Error as e:
        print("❌ Error while connecting to MySQL:", e)
        return None

def close_connection(connection):
    """Close the MySQL connection."""
    if connection and connection.is_connected():
        connection.close()
        print("✅ MySQL connection closed")

def execute_query(query, values=None, fetch=False):
    """Execute a query on the database."""
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            if values:
                cursor.execute(query, values)
            else:
                cursor.execute(query)
            if fetch:
                result = cursor.fetchall()  # Fetch result if required
                close_connection(connection)
                return result
            connection.commit()  # Commit changes for INSERT/UPDATE/DELETE
            close_connection(connection)
            return True
        except Error as e:
            print("❌ Error executing query:", e)
            close_connection(connection)
            return None
    return None
