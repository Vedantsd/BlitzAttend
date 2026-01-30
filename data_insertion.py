import pandas as pd
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def insert_csv_to_db(csv_file_path):
    df = pd.read_csv(csv_file_path)

    prn_col = [c for c in df.columns if "prn" in c.lower()][0]
    name_col = [c for c in df.columns if "stud" in c.lower()][0]
    batch_col = [c for c in df.columns if "batch" in c.lower()][0]

    df = df[[prn_col, name_col, batch_col]]
    df.columns = ['prn', 'stud_name', 'batch']

    df['prn'] = df['prn'].astype(str)
    df['prn'] = df['prn'].str.replace('.0', '', regex=False)
    df['prn'] = df['prn'].str.strip()
    df = df[df['prn'].str.len() == 12]


    if df.empty:
        print("No valid rows found")
        return

    db = mysql.connector.connect(
        host=os.getenv("host"),
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database")
    )

    cursor = db.cursor()

    query = "INSERT INTO SY_IT (prn, stud_name, batch) VALUES (%s,%s,%s)"

    count = 0

    for _, row in df.iterrows():
        cursor.execute(query, (row['prn'], row['stud_name'], row['batch']))
        count += 1

    db.commit()

    print("Inserted:", count)

    cursor.close()
    db.close()

if __name__ == "__main__":
    insert_csv_to_db("roll_call.csv")
