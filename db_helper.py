import mysql.connector
from datetime import date
from dotenv import load_dotenv
import os
import hashlib

load_dotenv()

db = mysql.connector.connect (
    host = os.getenv("host"), 
    user = os.getenv("user"), 
    password = os.getenv("password"), 
    database = os.getenv("database")
)

cursor = db.cursor()

def get_data(class_name, batch_name) : 
    sql = ""
    if not batch_name: 
        sql = f"select * from {class_name}"
    else: 
        sql = f"select * from {class_name} where batch = '{batch_name}'"

    cursor.execute(sql)
    return cursor.fetchall()

def get_course_code(class_name, course_name) : 
    sql = f"Select course_code from courses where class_name = '{class_name}' and course_name = '{course_name}'"
    cursor.execute(sql)
    data = cursor.fetchall()
    return data[0]

def get_courses(class_name) : 
    sql = f"select course_name from courses where class_name = '{class_name}'"
    cursor.execute(sql)
    return cursor.fetchall()

def add_attendance(data, coursecode) :
    today = date.today()
    formatted_date = f"{today.day}-{today.month}-{today.year}"
    sql = f"insert into attendance_records (course_code, att_date, prn, att_status) values (%s, %s, %s, %s)"

    for row in data : 
        values = (coursecode, formatted_date, row[1], row[4])
        cursor.execute(sql, values)

    db.commit()

def get_attendance(course_code) : 
    sql = f"select * from attendance_records where course_code = '{course_code}'"
    cursor.execute(sql)
    return cursor.fetchall()

def get_name_prn(class_name) : 
    sql = f"select stud_name, prn from {class_name}"
    cursor.execute(sql)
    return cursor.fetchall()

def get_all_class_names():
    sql = "SELECT DISTINCT class_name FROM courses ORDER BY class_name"
    cursor.execute(sql)
    classes = [row[0] for row in cursor.fetchall()]
    return classes

def get_batches_for_class(class_name):
    sql = f"SELECT DISTINCT batch FROM {class_name} ORDER BY batch"
    cursor.execute(sql)
    batches = [row[0] for row in cursor.fetchall()]
    return batches

def hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()

def validate_user(username, pin):
    sql = "SELECT id, username, email, user_type, password FROM User WHERE username = %s"
    cursor.execute(sql, (username,))
    result = cursor.fetchone()

    if result:
        user_id, db_username, email, user_type, stored_password = result
        hashed_pin = hash_pin(pin)
        if hashed_pin == stored_password:
            return {
                'id': user_id,
                'username': db_username,
                'email': email,
                'user_type': user_type
            }
    
    return None

def create_user(username, email, user_type, pin):
    hashed_pin = hash_pin(pin)
    sql = "INSERT INTO User (username, email, user_type, password) VALUES (%s, %s, %s, %s)"
    
    try:
        cursor.execute(sql, (username, email, user_type, hashed_pin))
        db.commit()
        return True
    except mysql.connector.IntegrityError:
        return False

def update_user_pin(username, new_pin):
    hashed_pin = hash_pin(new_pin)
    sql = "UPDATE User SET password = %s WHERE username = %s"
    cursor.execute(sql, (hashed_pin, username))
    db.commit()
    return cursor.rowcount > 0

def update_user_pin_by_id(user_id, new_pin):
    hashed_pin = hash_pin(new_pin)
    sql = "UPDATE User SET password = %s WHERE id = %s"
    cursor.execute(sql, (hashed_pin, user_id))
    db.commit()
    return cursor.rowcount > 0

def get_all_users():
    sql = "SELECT id, username, email, user_type, created_at FROM User ORDER BY id"
    cursor.execute(sql)
    users = []
    for row in cursor.fetchall():
        users.append({
            'id': row[0],
            'username': row[1],
            'email': row[2],
            'user_type': row[3],
            'created_at': row[4].isoformat() if row[4] else None
        })
    return users

def delete_user(user_id):
    sql = "DELETE FROM User WHERE id = %s"
    cursor.execute(sql, (user_id,))
    db.commit()
    return cursor.rowcount > 0