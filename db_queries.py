import threading
import mysql.connector
from db_connector import get_db_connection
import time

def update_tournament_start_date(tournament_id, new_date, current_version, admin_name):
    print(f"{admin_name} is trying to update tournament with version {current_version}...")
    
    connection = get_db_connection()
    if not connection:
        print(f"{admin_name}: Connection failed!")
        return

    cursor = connection.cursor()
    query = """
        UPDATE Tournaments 
        SET start_date = %s, version = version + 1 
        WHERE tournament_id = %s AND version = %s
    """
    
    # Simulate a delay so both admins try to update at the same time
    time.sleep(1)
    
    cursor.execute(query, (new_date, tournament_id, current_version))
    connection.commit()

    if cursor.rowcount > 0:
        print(f"{admin_name}: Tournament updated successfully!")
    else:
        print(f"{admin_name}: Update failed. Version mismatch.")
    
    cursor.close()
    connection.close()

# Function to simulate Admin 1 and Admin 2
def simulate_concurrent_updates():
    tournament_id = 1
    new_start_date_admin1 = '2025-06-01 10:00:00'
    new_start_date_admin2 = '2025-07-01 10:00:00'
    
    # Admin 1 fetches the tournament and gets version 1
    current_version_admin1 = 4
    
    # Admin 2 fetches the tournament and gets version 1
    current_version_admin2 = 4
    
    # Create threads for Admin 1 and Admin 2
    admin1_thread = threading.Thread(target=update_tournament_start_date, args=(tournament_id, new_start_date_admin1, current_version_admin1, "Admin 1"))
    admin2_thread = threading.Thread(target=update_tournament_start_date, args=(tournament_id, new_start_date_admin2, current_version_admin2, "Admin 2"))

    # Start both threads to simulate concurrent updates
    admin1_thread.start()
    admin2_thread.start()

    # Wait for both threads to finish
    admin1_thread.join()
    admin2_thread.join()

# Run the simulation
simulate_concurrent_updates()

