import sqlite3

conn = sqlite3.connect('tickets.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    message TEXT,
    status TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    admin_response TEXT
)
''')
conn.commit()

def add_ticket(user_id, username, message):
    cursor.execute("INSERT INTO tickets (user_id, username, message, status) VALUES (?, ?, ?, ?)",
                   (user_id, username, message, 'new'))
    conn.commit()

def get_new_tickets():
    cursor.execute("SELECT id, username, message FROM tickets WHERE status = 'new'")
    return cursor.fetchall()

def reply_to_ticket(ticket_id, reply):
    cursor.execute("UPDATE tickets SET status = 'processed', admin_response = ? WHERE id = ?",
                   (reply, ticket_id))
    conn.commit()

def get_user_id_by_ticket(ticket_id):
    cursor.execute("SELECT user_id FROM tickets WHERE id = ?", (ticket_id,))
    result = cursor.fetchone()
    return result[0] if result else None
