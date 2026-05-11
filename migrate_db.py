import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="LEKHAN@2121",
    database="agrosmart"
)
cursor = db.cursor()

try:
    # Drop and recreate bookings table with proper schema
    cursor.execute("DROP TABLE IF EXISTS bookings")

    cursor.execute("""
        CREATE TABLE bookings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            machine_id INT,
            user_id INT,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            status ENUM('pending', 'approved', 'rejected', 'cancelled', 'completed') DEFAULT 'pending',
            total_cost DECIMAL(10,2),
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (machine_id) REFERENCES machinery(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    db.commit()
    print("Bookings table recreated with proper schema!")

except Exception as e:
    print("Migration error:", e)
    db.rollback()

finally:
    cursor.close()
    db.close()