# **Part 1: Performance Analysis Report: Optimistic vs. Pessimistic Concurrency Control**

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

# **Part 2: Denormalization & Partitions & Query Optimization**

# Denormalizing Total Sales per Order
```sql
CREATE TABLE Orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    order_date DATE
);

CREATE TABLE OrderDetails (
    order_detail_id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT,
    product_id INT,
    quantity INT,
    price DECIMAL(10,2),
    FOREIGN KEY (order_id) REFERENCES Orders(order_id)
);
```
```sql
ALTER TABLE Orders ADD COLUMN total_amount DECIMAL(10,2);

UPDATE Orders o
SET total_amount = (
    SELECT SUM(quantity * price)
    FROM OrderDetails
    WHERE order_id = o.order_id
);
```
## What are the performance benefits of this approach?
Ved at denormalisere vores total sales per order bliver databasen hurtigere, og vi undgår at bruge joins, som ellers ville gøre databasen langsommere.

## How should we ensure the totalAmount stays accurate when an order is updated?
Vi benytter os af en trigger, som aktiveres hver gang der sker en opdatering på enten order quantity eller order price.

---

# Denormalizing Customer Data in Orders
```sql
CREATE TABLE Customers (
    customer_id INT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100)
);

CREATE TABLE Orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    order_date DATE,
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
);
```
```sql
ALTER TABLE Orders ADD COLUMN customer_name VARCHAR(100);
ALTER TABLE Orders ADD COLUMN customer_email VARCHAR(100);

UPDATE Orders o
JOIN Customers c ON o.customer_id = c.customer_id
SET o.customer_name = c.name, o.customer_email = c.email;
```

## When would this denormalization be useful?
Denormaliseringen gør, at vi ikke har et lige så stort behov for joins i vores database.  
Det ville være nyttigt, når vi har kundedata, der ikke opdateres ofte.

## How should updates to Customers be handled in this case?
Vi ville benytte os af triggere, der opdaterer kundedata i vores ordre-tabel.

---

# Using Partitioning for Sales Data

## How does partitioning improve query speed?
Ved at opdele data kan MySQL kun søge i den relevante partition, hvilket reducerer mængden af data, som skal scannes.  
Store tabeller bliver lettere at administrere ved at opdele dem i mindre enheder.  
Data placeres i partitioner baseret på en given kolonne, hvor vi kan hente data direkte fra kolonnen.

## Why does MySQL not allow foreign keys in partitioned tables?
MySQL tillader ikke fremmednøgler i partitionerede tabeller, fordi det skaber problemer med at opretholde referentiel integritet på tværs af partitioner.

## What happens when a new year starts?
Når et nyt år starter, skal man manuelt tilføje en ny partition for det kommende år, så data bliver partitioneret korrekt.

---

# Using List Partitioning for Regional Data

## What types of queries does list partitioning optimize?
List partitioning optimerer queries, der er baseret på regioner.

## What if a new region needs to be added?
Hvis man skal tilføje en ny region, kan man bruge `ALTER TABLE` og manuelt tilføje den nye region.

## How does list partitioning compare to range partitioning?
- **List partitioning** er bedst, når vi vil opdele data i kategorier, f.eks. varegrupper eller regioner.  
- **Range partitioning** er bedst, når vi arbejder med tid (f.eks. år, årtier, dage osv.).

---

# 📌 1. Running Queries on Partitioned Data
- **Without partition**
- '-> Table scan on Sales  (cost=0.35 rows=1) (actual time=0.0071..0.0071 rows=0 loops=1)\n'
  
- **With partition**
- '-> Table scan on Sales  (cost=0.85 rows=1) (actual time=0.0263..0.0263 rows=0 loops=1)\n'


---

# 📌 2. Running EXPLAIN ANALYZE

'-> Filter: ((sales.region = \'EU\') and (sales.sale_date between \'2023-01-01\' and \'2023-12-31\'))  (cost=0.35 rows=1) (actual time=0.0271..0.0271 rows=0 loops=1)\n    -> Table scan on Sales  (cost=0.35 rows=1) (actual time=0.0267..0.0267 rows=0 loops=1)\n'  

Expected Outcome:
The query scans the entire table.✅
The rows examined count will be high, especially for large datasets.❓


---

# 📌 3. Running EXPLAIN ANALYZE With Partition Selection

'-> Filter: (sales.sale_date between \'2023-01-01\' and \'2023-12-31\')  (cost=0.35 rows=1) (actual time=0.0206..0.0206 rows=0 loops=1)\n    -> Table scan on Sales  (cost=0.35 rows=1) (actual time=0.0203..0.0203 rows=0 loops=1)\n'

### Expected Improvement:
- The rows examined count should be significantly lower.❓  
- The query execution time should be faster.✅  

---

# 📌 4. Key Metrics to Compare

| Metric            | Without partitioning 🔴 | With partitioning 🟢 |
|-------------------|----------------------|----------------------|
| **Rows examined**  | High (Full scan)     | High (Partition Scan) |
| **Execution Time** | Slower (Full Table Scan) | Faster (Partition Pruning) |
| **Index Usage**    | Didn't use index (Could be full scan) | Can use index (if indexed partitions) |
| **Query complexity** | Higher complexity (Full scan, no pruning) | Lower Complexity (Partition Pruning) |

---

# 📌 5. Viewing Query Execution Plan in MySQL Workbench

## Refleksion over Databaseoptimering

### Samtidighedskontrol: Optimistisk vs. Pessimistisk

Samtidighedskontrol er afgørende i databaser for at sikre dataintegritet, når flere transaktioner udføres samtidigt.  
Optimistisk samtidighedskontrol antager, at konflikter er sjældne og tillader transaktioner at køre uden låsning, men verificerer ved commit, om der er sket konflikter.  
Hvis der opdages en konflikt, rulles transaktionen tilbage.  
Dette er effektivt i miljøer med lav konfliktfrekvens, da det reducerer ventetid for ressourcer.  

Pessimistisk samtidighedskontrol, derimod, låser data, når en transaktion begynder, hvilket forhindrer andre i at ændre de låste data, indtil låsen frigives.  
Dette sikrer dataintegritet i miljøer med høj konfliktfrekvens, men kan føre til øget ventetid og potentiale for deadlocks.  

### Denormalisering og Partitionering

Denormalisering indebærer bevidst at introducere redundans i databasedesign for at forbedre læseydelsen.  
Ved at have duplikerede data kan systemet reducere behovet for komplekse joins, hvilket accelererer læseoperationer.  
Ulempen er, at det kan øge kompleksiteten ved skriveoperationer og vedligeholdelse af dataintegritet.  

Partitionering deler en stor tabel op i mindre, mere håndterbare segmenter.  
Dette kan forbedre ydeevnen ved at reducere mængden af data, der skal scannes under forespørgsler, og ved at fordele data over forskellige lagerenheder.  
Der er forskellige partitioneringsstrategier, såsom **horisontal partitionering** (baseret på rækker) og **vertikal partitionering** (baseret på kolonner).  

### Forespørgselsoptimering

Forespørgselsoptimering fokuserer på at forbedre effektiviteten af databaseforespørgsler.  
Dette kan opnås gennem forskellige teknikker, såsom:  

- **Brug af indekser**: Indekser kan dramatisk reducere søgetiden for forespørgsler ved at give hurtig adgang til data.  
- **Omskrivning af forespørgsler**: Ved at omstrukturere forespørgsler kan man reducere kompleksiteten og forbedre ydeevnen.  
- **Analyse af forespørgselsplaner**: Ved at studere, hvordan databasen planlægger at udføre en forespørgsel, kan man identificere og adressere ineffektiviteter.  

### Refleksion over Databaseoptimering

Gennem arbejdet med ovenstående emner bliver det klart, at databaseoptimering er en balancegang mellem forskellige faktorer.  
For eksempel kan denormalisering forbedre læseydelsen, men det kræver omhyggelig styring for at undgå inkonsistens i data.  
Ligeledes kan valg mellem optimistisk og pessimistisk samtidighedskontrol afhænge af den specifikke applikations behov og det forventede niveau af datakonflikter.  

Implementering af disse teknikker kræver en dyb forståelse af både databasedesign og de specifikke behov i den anvendte applikation.  
Ved at anvende passende optimeringsstrategier kan man opnå betydelige forbedringer i systemets ydeevne og pålidelighed.  
