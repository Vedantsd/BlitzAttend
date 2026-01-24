import mysql.connector
from datetime import date
from dotenv import load_dotenv
import os

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



def add_attendance(data, course_code) :

    today = date.today()
    formatted_date = f"{today.day}-{today.month}-{today.year}"
    sql = f"insert into attendance_records (course_code, att_date, prn, att_status) values (%s, %s, %s, %s)"

    for row in data : 
        values = (course_code, formatted_date, row[1], row[4])
        cursor.execute(sql, values)

    db.commit()

def get_attendance(course_code) : 
    sql = f"select * from attendance_records where course_code = {course_code}"
    cursor.execute(sql)
    return cursor.fetchall()

def get_name_prn(class_name) : 
    sql = f"select stud_name, prn from '{class_name}'"
    cursor.execute(sql)
    return cursor.fetchall()