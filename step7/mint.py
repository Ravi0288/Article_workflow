import os
import mysql.connector
from mysql.connector import Error


# connect to the pid database
def connect_pid_db():
    # Fetch database credentials from environment variables
    db_name = os.getenv("PID_DB_NAME")
    db_user = os.getenv("PID_DB_USER")
    db_password = os.getenv("PID_DB_PASSWORD")
    db_host = os.getenv("PID_DB_HOST")
    db_port = os.getenv("PID_DB_PORT")

    try:
        # Establish the database connection
        connection = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name,
            port=db_port,
            charset="utf8mb4",
            collation="utf8mb4_general_ci"
        )

        # if connection is successful
        if connection.is_connected():
            return connection
        else:
            return None

    # return None if connection is not successful
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None


'''
This function will take input citation_object as dictionary and return the 
updated citation object with PID, success / error message and the PID
'''
def pid_minter(citation_object) -> list:
    pid_db_connection = connect_pid_db()

    # if pid_db_connection and article_db_connection:
    if pid_db_connection:
        pid_db = pid_db_connection.cursor()

        # generate the new PID
        # Call the stored procedure to get the next PID
        # pid_db.callproc('get_next_pid')

        pid_db.execute("SELECT nextval(pid) from pid")

        # Fetch the result
        row = pid_db.fetchone()
        next_pid = row[0] if row else None
        
        # # Fetch the result (next_pid)
        # next_pid = None
        # for result in pid_db.stored_results():
        #     next_pid = result.fetchone()[0]

        if not next_pid:
            return None

        if citation_object.type != 'journal-article':
            result = [citation_object, "Non Article", None]

        else:
            citation_object.local.identifiers.setdefault('pid', None)
            if citation_object.local.identifiers['pid']:
                result = [citation_object, "PID Already Assinged", None]
            else:
                citation_object.local.identifiers['pid'] = next_pid
                result = [citation_object, "PID Assinged", next_pid]

    else:
        result = [citation_object, "Database connection error occured", None]

    if pid_db_connection:
        pid_db_connection.close()
    
    return result
