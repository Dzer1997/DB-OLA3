import mysql.connector
from db_connector import get_db_connection 
import threading
def register_player(tournament_id, player_id):
    connection = get_db_connection()
    if not connection:
        return False

    try:
        cursor = connection.cursor()

        # Start transaction
        connection.start_transaction()

        cursor.execute("SELECT max_players FROM Tournaments WHERE tournament_id = %s FOR UPDATE", (tournament_id,))
        tournament = cursor.fetchone()

        if not tournament:
            print("Tournament not found.")
            connection.rollback()
            return False

        max_players = tournament[0]

        # make count
        cursor.execute("SELECT COUNT(*) FROM Tournament_Registrations WHERE tournament_id = %s", (tournament_id,))
        current_players = cursor.fetchone()[0]

        if current_players >= max_players:
            print("Tournament is full! Registration rejected.")
            connection.rollback()
            return False

      
        cursor.execute("INSERT INTO Tournament_Registrations (tournament_id, player_id) VALUES (%s, %s)", 
                       (tournament_id, player_id))
        connection.commit()
        print(f"Player {player_id} successfully registered.")
        return True

    except mysql.connector.Error as e:
        print("Error:", e)
        connection.rollback() 
        return False

    finally:
        cursor.close()
        connection.close()


def register_player_to_tournament(tournament_id, player_1,player_2):
  admin1_thread = threading.Thread(target=register_player, args=(tournament_id, player_1))
  admin2_thread = threading.Thread(target=register_player, args=(tournament_id, player_2))
  admin1_thread.start()
  admin2_thread.start()


  admin1_thread.join()
  admin2_thread.join()


if __name__ == "__main__":
  tournament_id = 2
  player_1 = 4
  player_2 = 5
  register_player_to_tournament(tournament_id,player_1,player_2)  