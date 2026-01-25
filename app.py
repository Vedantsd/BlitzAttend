from flask import Flask, render_template, request
import json
import db_helper

app = Flask(__name__)

class_name = ""
batch_name = ""

# Dummy data
class_list = {"CSE-A" : ["A1", "A2", "A3"], 
              "CSE-B" : ["B1", "B2", "B3"], 
              "CSE-C" : ["C1", "C2", "C3"], 
              "SY_IT" : ["A1", "A2", "A3"]}




@app.route('/')
def class_selection(): 
    return render_template('index.html', classes=class_list, class_json=json.dumps(class_list))

@app.route('/load-courses', methods=["POST"])   
def load_courses(): 
    global class_name, batch_name

    class_name = request.form.get("select-class")
    batch_name = request.form.get("select-batch")
    courses = db_helper.get_courses(class_name)

    return render_template('index.html', classes=class_list, courses=courses, class_name=class_name, batch_name=batch_name)

@app.route('/attendance', methods=["POST"])
def attendance(): 
    course_name = request.form.get('select-course')
    students = db_helper.get_data(class_name, batch_name)
    return render_template('attend.html', data=students, course=course_name)


@app.route('/submit-attendance', methods=["POST"])
def display_attendance(): 
    attendance_data = request.form.get("attendance")
    course_name = request.form.get("course-name")
    attendance_list = json.loads(attendance_data)

    course_code = db_helper.get_course_code(class_name, course_name)[0]
    db_helper.add_attendance(attendance_list, coursecode=course_code)
    return "Attendance complete"

if __name__ == "__main__" : 
    app.run(debug=True)