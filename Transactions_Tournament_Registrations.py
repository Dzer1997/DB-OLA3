import mysql.connector
from mysql.connector import Error
from db_connector import get_db_connection
import mysql.connector
from db_connector import get_db_connection

def register_player(tournament_id, player_id):
    connection = get_db_connection()
    if not connection:
        print("Error: Database connection failed.")
        return

    try:
        cursor = connection.cursor(dictionary=True)

        connection.start_transaction()

        # we make check if the tournament is full
        cursor.execute("SELECT COUNT(*) as player_count, max_players FROM Tournaments "
                       "JOIN Tournament_Registrations ON Tournaments.tournament_id = Tournament_Registrations.tournament_id "
                       "WHERE Tournaments.tournament_id = %s GROUP BY max_players", (tournament_id,))
        result = cursor.fetchone()

        if result and result['player_count'] >= result['max_players']:
            print("Tournament is full. Registration failed.")
            connection.rollback()  # Rollback transaction
            return

        # we add registration
        cursor.execute("INSERT INTO Tournament_Registrations (tournament_id, player_id) VALUES (%s, %s)", 
                       (tournament_id, player_id))

        cursor.execute("UPDATE Players SET ranking = ranking + 10 WHERE player_id = %s", (player_id,))
        connection.commit()
        print("Registration successful!")

    except mysql.connector.Error as e:
        connection.rollback() 
        print("Error during registration:", e)

    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    tournament_id = 2  
    player_id = 5    
    register_player(tournament_id, player_id)
