from flask import Flask, render_template
import json

app = Flask(__name__)



# Dummy data
class_list = {"CSE-A" : ["A1", "A2", "A3"], 
              "CSE-B" : ["B1", "B2", "B3"], 
              "CSE-C" : ["C1", "C2", "C3"], 
              "IT-A" : ["A1", "A2", "A3"]}

courses = ["TOC", "Maths", "ADV", "DBMS"]



@app.route('/')
def class_selection(): 
    return render_template('index.html', classes=class_list, courses=courses, class_json=json.dumps(class_list))

@app.route('/attendance', methods=["POST"])
def attendance(): 
    return render_template('attend.html')



if __name__ == "__main__" : 
    app.run(debug=True)