import sqlite3
from datetime import datetime, timedelta

from model.utils import RetValue


def check_table():
    # Connect to the SQLite database
    conn = sqlite3.connect('db/user_requests.db')
    cursor = conn.cursor()

    # Check if the table exists
    table_name = 'users'
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    result = cursor.fetchone()

    # If the table doesn't exist, create it
    if result is None:
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS users (
            user_name TEXT UNIQUE,
            user_id INTEGER UNIQUE,
            email TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        '''
        cursor.execute(create_table_query)
        conn.commit()
        print("Table created successfully.")

    # Close the database connection
    conn.close()


def check_from_db(user_id, user_name, target_email):
    conn = sqlite3.connect('db/user_requests.db')

    check_table()
    cursor = conn.cursor()
    select_query = "SELECT timestamp FROM users WHERE user_id = ?"
    cursor.execute(select_query, (user_id,))
    result = cursor.fetchone()
    if result:
        # User found in the database, get the timestamp value
        stored_timestamp = datetime.strptime(result[0], '%Y-%m-%d %H:%M:%S')

        # Compare the stored timestamp with the current datetime
        current_datetime = datetime.now()

        time_difference = current_datetime - stored_timestamp
        if time_difference < timedelta(hours=23, minutes=59):
            # Perform any desired actions if the stored timestamp is older than the current datetime
            remaining_time = timedelta(hours=24) - time_difference

            remaining_seconds = remaining_time.total_seconds()
            hours = int(remaining_seconds // 3600)
            minutes = int((remaining_seconds % 3600) // 60)
            seconds = int(remaining_seconds % 60)
            conn.close()
            return [RetValue.EarlyRequestFail, hours, minutes, seconds, current_datetime]
    else:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Insert the user information into the database
        insert_query = '''INSERT INTO users (user_name, user_id, email, timestamp)VALUES (?, ?, ?, ?)'''
        user_data = (user_name, user_id, target_email, timestamp)
        cursor.execute(insert_query, user_data)
        conn.commit()
        conn.close()

        return [RetValue.Success]
