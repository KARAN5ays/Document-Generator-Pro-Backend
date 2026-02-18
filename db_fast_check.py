import os
import django
import sqlite3

# Option 1: Direct SQLite3 (doesn't load Django)
def direct_sqlite():
    print("--- Direct SQLite3 Check ---")
    try:
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        print("Users:")
        cursor.execute("SELECT id, username FROM backendapp_user")
        users = cursor.fetchall()
        for u in users:
            print(f"  ID: {u[0]}, Username: {u[1]}")
            
        print("\nDocument counts by user ID:")
        cursor.execute("SELECT issued_by_id, COUNT(*) FROM backendapp_document GROUP BY issued_by_id")
        counts = cursor.fetchall()
        for c in counts:
            print(f"  User ID: {c[0]}, Count: {c[1]}")

        print("\nOutstanding tokens:")
        cursor.execute("SELECT COUNT(*) FROM token_blacklist_outstandingtoken")
        print(f"  Count: {cursor.fetchone()[0]}")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    direct_sqlite()
