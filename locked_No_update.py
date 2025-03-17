import threading
import time
from PessimisticConcurrency import update_match_result_pessimistic

def simulate_concurrent_updates():
    match_id = 1  # Match ID to update
    winner_id = 2  # Winner ID to set

    # Create two admin threads
    admin1_thread = threading.Thread(target=update_match_result_pessimistic, args=(match_id, winner_id, "Admin 1"))
    admin2_thread = threading.Thread(target=update_match_result_pessimistic, args=(match_id, winner_id, "Admin 2"))

    # Start Admin 1
    admin1_thread.start()
    time.sleep(1)  # Simulate Admin 2 starting slightly later

    # Start Admin 2
    admin2_thread.start()

    # Wait for both threads to finish
    admin1_thread.join()
    admin2_thread.join()

# Run the test
if __name__ == "__main__":
    simulate_concurrent_updates()
