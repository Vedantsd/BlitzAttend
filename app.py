from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import json
import db_helper
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('secret_key')

class_name = ""
batch_name = ""


@app.route('/login')
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/validate', methods=['POST'])
def validate():
    try:
        data = request.json
        username = data.get('username')
        pin = data.get('pin')
    
        if not username or not pin:
            return jsonify({
                'success': False,
                'message': 'Username and PIN are required'
            }), 400

        user = db_helper.validate_user(username, pin)

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['user_type'] = user['user_type']
            session['email'] = user['email']

            if user['user_type'] == 'admin' : 
                redirect_url = '/admin-dashboard' 
            else :
                redirect_url = '/user-dashboard'

            return jsonify({
                'success': True,
                'message': 'Login successful',
                'redirect': redirect_url,
                'user_type': user['user_type']
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid username or PIN'
            }), 401

    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'An error occurred during login'
        }), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        if session.get('user_type') != 'admin':
            return redirect('/user-dashboard')
        return f(*args, **kwargs)
    return decorated_function


@app.route('/class-details')
@login_required
def class_selection(): 
    classes = db_helper.get_all_class_names()
    class_list = {}

    for i in classes : 
        try : 
            class_list[i] = db_helper.get_batches_for_class(i)
        except : 
            class_list[i] = ()


    return render_template('index.html', classes=class_list, class_json=json.dumps(class_list))

@app.route('/load-courses', methods=["POST"])
@login_required   
def load_courses(): 
    global class_name, batch_name

    class_name = request.form.get("select-class")
    batch_name = request.form.get("select-batch")
    courses = db_helper.get_courses(class_name)

    classes = db_helper.get_all_class_names()
    class_list = {}

    for i in classes : 
        try : 
            class_list[i] = db_helper.get_batches_for_class(i)
        except : 
            class_list[i] = ()

    return render_template('index.html', classes=class_list, courses=courses, class_name=class_name, batch_name=batch_name)

@app.route('/attendance', methods=["POST"])
@login_required
def attendance(): 
    course_name = request.form.get('select-course')
    students = db_helper.get_data(class_name, batch_name)
    return render_template('attend.html', data=students, course=course_name)


@app.route('/submit-attendance', methods=["POST"])
@login_required
def display_attendance(): 
    attendance_data = request.form.get("attendance")
    course_name = request.form.get("course-name")
    attendance_list = json.loads(attendance_data)

    course_code = db_helper.get_course_code(class_name, course_name)[0]
    db_helper.add_attendance(attendance_list, coursecode=course_code)
    return "Attendance complete"


@app.route('/user-dashboard')
@login_required
def dashboard():
    classes = db_helper.get_all_class_names()
    user_info = {
        'username': session.get('username'),
        'user_type': session.get('user_type'),
        'email': session.get('email')
    }
    return render_template('user-dashboard.html', classes=classes, user=user_info)


@app.route('/get_batches/<class_name>')
@login_required
def get_batches(class_name):
    try:
        batches = db_helper.get_batches_for_class(class_name)
        return jsonify(batches)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/get_courses/<class_name>')
@login_required
def get_courses_api(class_name):
    try:
        courses_data = db_helper.get_courses(class_name)
        courses = [row[0] for row in courses_data]
        return jsonify(courses)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/get_attendance_data', methods=['POST'])
@login_required
def get_attendance_data():
    try:
        data = request.json
        class_name = data.get('class_name')
        batch = data.get('batch')
        course = data.get('course')

        if not class_name or not course:
            return jsonify({'error': 'Class and course are required'}), 400

        course_code = db_helper.get_course_code(class_name, course)[0]

        students_data = db_helper.get_data(class_name, batch)

        attendance_records = db_helper.get_attendance(course_code)

        unique_dates = set()
        attendance_dict = {}
        
        for record in attendance_records:
            unique_dates.add(record[1])
            prn = record[2]
            if prn not in attendance_dict:
                attendance_dict[prn] = 0
            if record[3] == 1:  
                attendance_dict[prn] += 1

        total_classes = len(unique_dates)

        students = []
        total_attendance = 0
        
        for student in students_data:
            rollno, prn, name, batch = student
            attended = attendance_dict.get(prn, 0)
            
            students.append({
                'rollno': rollno,
                'prn': prn,
                'name': name,
                'batch': batch,
                'attended': attended
            })
            
            if total_classes > 0:
                total_attendance += (attended / total_classes) * 100

        avg_attendance = round(total_attendance / len(students), 1) if students else 0

        return jsonify({
            'students': students,
            'total_students': len(students),
            'total_classes': total_classes,
            'avg_attendance': avg_attendance
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/admin-dashboard')
@admin_required
def admin_dashboard():
    user_info = {
        'username': session.get('username'),
        'user_type': session.get('user_type'),
        'email': session.get('email')
    }
    return render_template('admin.html', user=user_info)

@app.route('/admin/users')
@admin_required
def get_all_users():
    try:
        users = db_helper.get_all_users()
        return jsonify(users)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/add-user', methods=['POST'])
@admin_required
def add_user():
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        user_type = data.get('user_type')
        pin = data.get('pin')

        if not all([username, email, user_type, pin]):
            return jsonify({'success': False, 'message': 'All fields are required'}), 400

        if len(pin) != 4 or not pin.isdigit():
            return jsonify({'success': False, 'message': 'PIN must be 4 digits'}), 400

        success = db_helper.create_user(username, email, user_type, pin)

        if success:
            return jsonify({'success': True, 'message': 'User added successfully'})
        else:
            return jsonify({'success': False, 'message': 'Username already exists'}), 400

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/admin/change-password', methods=['POST'])
@admin_required
def admin_change_password():
    try:
        data = request.json
        user_id = data.get('user_id')
        new_pin = data.get('new_pin')

        if not user_id or not new_pin:
            return jsonify({'success': False, 'message': 'User ID and PIN are required'}), 400

        if len(new_pin) != 4 or not new_pin.isdigit():
            return jsonify({'success': False, 'message': 'PIN must be 4 digits'}), 400

        success = db_helper.update_user_pin_by_id(user_id, new_pin)

        if success:
            return jsonify({'success': True, 'message': 'Password updated successfully'})
        else:
            return jsonify({'success': False, 'message': 'User not found'}), 404

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/admin/delete-user', methods=['POST'])
@admin_required
def delete_user():
    try:
        data = request.json
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({'success': False, 'message': 'User ID is required'}), 400

        if int(user_id) == session.get('user_id'):
            return jsonify({'success': False, 'message': 'Cannot delete your own account'}), 400

        success = db_helper.delete_user(user_id)

        if success:
            return jsonify({'success': True, 'message': 'User deleted successfully'})
        else:
            return jsonify({'success': False, 'message': 'User not found'}), 404

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/dashboard')
@login_required
def view_dashboard():
    classes = db_helper.get_all_class_names()
    user_info = {
        'username': session.get('username'),
        'user_type': session.get('user_type'),
        'email': session.get('email')
    }
    return render_template('dashboard.html', classes=classes, user=user_info)

if __name__ == "__main__" : 
    app.run(debug=True)