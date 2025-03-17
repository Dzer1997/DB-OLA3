import time
import mysql.connector
from db_connector import get_db_connection

def update_match_result_pessimistic(match_id, winner_id, admin_name):

    connection = get_db_connection()
    if not connection:
        print(f"[{admin_name}] Database connection failed.")
        return False

    try:
        connection.start_transaction() 
        cursor = connection.cursor()

        print(f"[{admin_name}] Attempting to lock match {match_id}...")
        try:
            cursor.execute("SELECT winner_id FROM Matches WHERE match_id = %s FOR UPDATE NOWAIT", (match_id,))
        except mysql.connector.Error as err:
            if err.errno == 3572: 
                print(f"[{admin_name}] Match {match_id} is locked by another admin. Try again later.")
                return False
            else:
                raise  

        row = cursor.fetchone()
        if row is None:
            print(f"[{admin_name}] Match {match_id} not found.")
            return False

        print(f"[{admin_name}] Match {match_id} locked! Updating winner...")
        time.sleep(5) 

        # Update the winner
        cursor.execute("UPDATE Matches SET winner_id = %s WHERE match_id = %s", (winner_id, match_id))
        connection.commit()

        print(f"[{admin_name}] Match {match_id} updated successfully!")
        return True

    except Exception as e:
        print(f"[{admin_name}] Error: {e}")
        return False
    finally:
        cursor.close()
        connection.close()
