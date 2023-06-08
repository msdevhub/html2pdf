import pymysql
from datetime import datetime
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def log_to_database(params):
    try:
        connection = pymysql.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )

        if connection.open:
            cursor = connection.cursor()
            
            # Create table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    start_date DATE NOT NULL,
                    end_date DATE NOT NULL,
                    total_amount FLOAT NOT NULL,
                    start_address VARCHAR(255) NOT NULL,
                    end_address VARCHAR(255) NOT NULL,
                    mileage_range VARCHAR(255) NOT NULL,
                    amount_range VARCHAR(255) NOT NULL,
                    city VARCHAR(255) NOT NULL,
                    model VARCHAR(255) NOT NULL,
                    phone_number VARCHAR(255) NOT NULL,
                    pdf_file_name VARCHAR(255) NOT NULL,
                    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    generation_time FLOAT NOT NULL
                )
            """)
            
            # Insert the order data
            query = """
                INSERT INTO orders (
                    start_date, end_date, total_amount, start_address,
                    end_address, mileage_range, amount_range, city, model,
                    phone_number, pdf_file_name, generation_time
                ) VALUES (
                    %(start_date)s, %(end_date)s, %(total_amount)s, %(start_address)s,
                    %(end_address)s, %(mileage_range)s, %(amount_range)s, %(city)s,
                    %(model)s, %(phone_number)s, %(pdf_file_name)s, %(generation_time)s
                )
            """
            
            cursor.execute(query, params)

            connection.commit()
            cursor.close()
            connection.close()
    except pymysql.Error as e:
        print("Error while connecting to MySQL", e)
