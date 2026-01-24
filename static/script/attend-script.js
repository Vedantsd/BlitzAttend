let index = 0

function renderStudents () {
    const s = students[index];
    document.getElementById("rollno").innerText = s[0];
    document.getElementById("name").innerText = s[2];
    document.getElementById("prn").innerText = s[1];
    document.getElementById("batch").innerText = s[3];
}

function markAttendance(status) {
    students[index].push(status);
    index++;

    if (index >= students.length) {
        document.getElementById("attendance").value = JSON.stringify(students);
        document.getElementById("form").submit();
        return;
    }

    renderStudents();
}

window.onload = renderStudents;