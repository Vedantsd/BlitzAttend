function renderStudents() {
    const studentsList = document.getElementById("students-list");
    studentsList.innerHTML = '';

    students.forEach((student, index) => {
        const studentItem = document.createElement('div');
        studentItem.className = 'student-item';

        const studentInfo = document.createElement('div');
        studentInfo.className = 'student-info';

        const rollno = document.createElement('div');
        rollno.className = 'student-rollno';
        rollno.textContent = student[0];

        const name = document.createElement('div');
        name.className = 'student-name';
        name.textContent = student[2];

        const details = document.createElement('div');
        details.className = 'student-details';
        details.textContent = `PRN: ${student[1]} | Batch: ${student[3]}`;

        studentInfo.appendChild(rollno);
        studentInfo.appendChild(name);
        studentInfo.appendChild(details);

        const checkboxContainer = document.createElement('div');
        checkboxContainer.className = 'checkbox-container';

        const label = document.createElement('label');
        label.textContent = 'Present';
        label.setAttribute('for', `checkbox-${index}`);

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = `checkbox-${index}`;
        checkbox.setAttribute('data-index', index);
        checkbox.addEventListener('change', handleCheckboxChange);

        checkboxContainer.appendChild(label);
        checkboxContainer.appendChild(checkbox);

        studentItem.appendChild(studentInfo);
        studentItem.appendChild(checkboxContainer);

        studentsList.appendChild(studentItem);
    });
}

function handleCheckboxChange(event) {
    const index = parseInt(event.target.getAttribute('data-index'));
    const isChecked = event.target.checked;
    
    if (!students[index][4]) {
        students[index].push(isChecked ? 1 : 0);
    } else {
        students[index][4] = isChecked ? 1 : 0;
    }
}

function submitAttendance() {
    students.forEach((student, index) => {
        if (student.length < 5) {
            student.push(0); 
        }
    });

    document.getElementById("attendance").value = JSON.stringify(students);
    document.getElementById("form").submit();
}

window.onload = renderStudents;