import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('user_requests.db')
cursor = conn.cursor()

# Create the table
create_table_query = '''
CREATE TABLE IF NOT EXISTS users (
    user_name TEXT UNIQUE,
    user_id INTEGER UNIQUE,
    email TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''
cursor.execute(create_table_query)

# Commit the changes and close the connection
conn.commit()
conn.close()

