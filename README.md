# **Performance Analysis Report: Optimistic vs. Pessimistic Concurrency Control**

## **📝 Student Names: Rabee, Kevin og Ermin**

---

## **📌 Introduction**
### **Objective:**
This report analyzes and compares the performance of **Optimistic Concurrency Control (OCC) vs. Pessimistic Concurrency Control (PCC)** when handling concurrent transactions in an Esports Tournament database.

### **Scenario Overview:**
- **OCC is tested** by simulating multiple players registering for the same tournament concurrently.
- **PCC is tested** by simulating multiple administrators updating the same match result simultaneously.

---

## **📌 Experiment Setup**
### **Database Schema Used:**
```sql
CREATE DATABASE final_assignment;
USE final_assignment;
CREATE TABLE Players (
    player_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    ranking INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Tournaments (
    tournament_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    game VARCHAR(50) NOT NULL,
    max_players INT NOT NULL,
    start_date DATETIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Tournament_Registrations (
    registration_id INT PRIMARY KEY AUTO_INCREMENT,
    tournament_id INT NOT NULL,
    player_id INT NOT NULL,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tournament_id) REFERENCES Tournaments(tournament_id) ON DELETE CASCADE,
    FOREIGN KEY (player_id) REFERENCES Players(player_id) ON DELETE CASCADE
);

CREATE TABLE Matches (
    match_id INT PRIMARY KEY AUTO_INCREMENT,
    tournament_id INT NOT NULL,
    player1_id INT NOT NULL,
    player2_id INT NOT NULL,
    winner_id INT NULL,
    match_date DATETIME NOT NULL,
    FOREIGN KEY (tournament_id) REFERENCES Tournaments(tournament_id) ON DELETE CASCADE,
    FOREIGN KEY (player1_id) REFERENCES Players(player_id) ON DELETE CASCADE,
    FOREIGN KEY (player2_id) REFERENCES Players(player_id) ON DELETE CASCADE,
    FOREIGN KEY (winner_id) REFERENCES Players(player_id) ON DELETE SET NULL
);
ALTER TABLE Tournaments ADD COLUMN version INT DEFAULT 1;
INSERT INTO Tournaments (name, game, max_players, start_date, version)
VALUES 
('Champions Cup', 'CS:GO', 16, '2025-06-15 14:00:00', 1),
('Battle Royale', 'Fortnite', 50, '2025-07-01 18:00:00', 1);
INSERT INTO Players (username, email, ranking) VALUES
('Player1', 'player1@example.com', 1),
('Player2', 'player2@example.com', 2),
('Player3', 'player3@example.com', 3),
('Player4', 'player4@example.com', 4);

INSERT INTO Tournaments (name, game, max_players, start_date) VALUES
('Summer Tournament', 'Fortnite', 16, '2025-07-01 12:00:00');
INSERT INTO Matches (tournament_id, player1_id, player2_id, match_date) VALUES
(1, 1, 2, '2025-07-01 14:00:00'),  -- Match between Player1 and Player2
(1, 3, 4, '2025-07-01 15:00:00');  -- Match between Player3 and Player4
-- Admin 1 updates the winner of match_id = 1 to Player 1
UPDATE Matches 
SET winner_id = 1 
WHERE match_id = 1;

INSERT INTO Tournament_Registrations (tournament_id, player_id) VALUES
(2, 1);

INSERT INTO Tournament_Registrations (tournament_id, player_id) VALUES
(2, 2);

DELIMITER $$

CREATE PROCEDURE UpdatePlayerRanking(IN player_id INT,IN increment_value INT)
BEGIN
    DECLARE current_ranking INT;
    START TRANSACTION;

    SELECT ranking INTO current_ranking 
    FROM Players 
    WHERE player_id = player_id 
    FOR UPDATE;
    UPDATE Players 
     SET ranking = ranking + increment_value
    WHERE player_id = player_id;

    COMMIT;
END $$

DELIMITER ;


```

### **Concurrency Control Techniques Implemented:**
- **Optimistic Concurrency Control (OCC)** using a **version column** in the `Tournaments` table.
- **Pessimistic Concurrency Control (PCC)** using `SELECT ... FOR UPDATE` when updating `Matches`.

### Test Parameters:

| Parameter                         | Value  |
|-----------------------------------|--------|
| Number of concurrent transactions | 100    |
| Database                          | mySQL  |
| Execution Environment             | Window |
| Python threading                  | Python |


---

## **📌 Results & Observations**

### **1️⃣ Optimistic Concurrency Control (OCC) Results**

### Optimistic Concurrency Control (OCC) Results
| Metric                                      | Value    |
|---------------------------------------------|---------|
| Execution Time (ms)                         | 16.01 sec |
| Number of successful transactions          | 11      |
| Number of retries due to version mismatch  | 89      |

---

### **2️⃣ Pessimistic Concurrency Control (PCC) Results**

### Pessimistic Concurrency Control (PCC) Results

| Metric                                      | Value    |
|---------------------------------------------|---------|
| Execution Time (ms)                         | 9.14 sec |
| Number of successful transactions          | 90      |
| Number of retries due to version mismatch  | 10      |


---

| Metric                     | Optimistic CC (OCC)                                | Pessimistic CC (PCC)                          |
|----------------------------|---------------------------------------------------|-----------------------------------------------|
| Execution Time             | Hurtigere (5.61-11.36 sek for 100 tråde)          | Langsommere (Pga. låse, ventetider)          |
| Transaction Success Rate   | Lavere (90/100 eller 9/100 succes)                | Højere (Sikrer succes via låse)              |
| Lock Contention           | Ingen/lav (Ingen låse, men version-mismatch)      | Høj (Rækker er låst, ventetid øges)         |
| Best Use Case              | Læs-tunge systemer (Få samtidige opdateringer, fx rapporter) | Skriv-tunge systemer (Hyppige opdateringer, fx banktransaktioner) |

