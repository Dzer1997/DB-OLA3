import time
import threading
from datetime import datetime, timedelta
from db_queries import update_tournament_start_date_pcc
from db_connector import get_db_connection
def get_tournament_version(tournament_id):
    connection = get_db_connection()
    if not connection:
        return None
    cursor = connection.cursor(dictionary=True)
    query = "SELECT version FROM Tournaments WHERE tournament_id = %s"
    
    try:
        cursor.execute(query, (tournament_id,))
        result = cursor.fetchone() 

        if result:
            return result['version']
        else:
            print(f"No tournament found with ID: {tournament_id}")
            return None 
    finally:
        cursor.close()
        connection.close()

def generate_new_date(admin_counter):
    base_date = datetime(2025, 7, 1, 12, 0, 0)  
    new_date = base_date + timedelta(minutes=admin_counter * 3)  
    return new_date.strftime("%Y-%m-%d %H:%M:%S")

def run_pesimistic_test(num_threads):
    start_time = time.time()
  
    tournament_id = 1 
    threads = []
    for admin_counter in range(1, num_threads + 1): 
        new_date_str = generate_new_date(admin_counter)
        t = threading.Thread(target=update_tournament_start_date_pcc, args=(tournament_id,new_date_str, admin_counter))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
        

    end_time = time.time()
    print(f"Optimistic Concurrency: {num_threads} threads -> Time Taken: {end_time - start_time:.2f} sec")

if __name__ == "__main__":
    print("Running Pessimistic Concurrency Control Test")
    run_pesimistic_test(100)  