const classSelect = document.getElementById('select-class');
const batchSelect = document.getElementById('select-batch');
const courseSelect = document.getElementById('select-course');
const mainDiv = document.querySelector('.main');

classSelect.addEventListener('change', async function() {
    const className = this.value;
    
    if (!className) {
        batchSelect.disabled = true;
        courseSelect.disabled = true;
        batchSelect.innerHTML = '<option value="">-- Select a Batch --</option>';
        courseSelect.innerHTML = '<option value="">-- Select a Course --</option>';
        mainDiv.innerHTML = '<div class="loading">Please select class, batch, and course to view attendance</div>';
        return;
    }

    try {
        const batchResponse = await fetch(`/get_batches/${className}`);
        const batches = await batchResponse.json();
        
        batchSelect.innerHTML = '<option value="">-- All Batches --</option>';
        batches.forEach(batch => {
            batchSelect.innerHTML += `<option value="${batch}">${batch}</option>`;
        });
        batchSelect.disabled = false;

        const courseResponse = await fetch(`/get_courses/${className}`);
        const courses = await courseResponse.json();
        
        courseSelect.innerHTML = '<option value="">-- Select a Course --</option>';
        courses.forEach(course => {
            courseSelect.innerHTML += `<option value="${course}">${course}</option>`;
        });
        courseSelect.disabled = false;

    } catch (error) {
        mainDiv.innerHTML = `<div class="error">Error loading data: ${error.message}</div>`;
    }
});

batchSelect.addEventListener('change', loadAttendance);
courseSelect.addEventListener('change', loadAttendance);

async function loadAttendance() {
    const className = classSelect.value;
    const batch = batchSelect.value;
    const course = courseSelect.value;

    if (!className || !course) {
        return;
    }

    mainDiv.innerHTML = '<div class="loading">Loading attendance data...</div>';

    try {
        const response = await fetch(`/get_attendance_data`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                class_name: className,
                batch: batch,
                course: course
            })
        });

        const data = await response.json();

        if (data.error) {
            mainDiv.innerHTML = `<div class="error">${data.error}</div>`;
            return;
        }

        displayAttendance(data);

    } catch (error) {
        mainDiv.innerHTML = `<div class="error">Error loading attendance: ${error.message}</div>`;
    }
}

function displayAttendance(data) {
    if (!data.students || data.students.length === 0) {
        mainDiv.innerHTML = '<div class="no-data">No students found for this selection</div>';
        return;
    }

    let html = '<div class="stats">';
    html += `<div class="stat-card"><h3>${data.total_students}</h3><p>Total Students</p></div>`;
    html += `<div class="stat-card"><h3>${data.total_classes}</h3><p>Total Classes</p></div>`;
    html += `<div class="stat-card"><h3>${data.avg_attendance}%</h3><p>Average Attendance</p></div>`;
    html += '</div>';

    html += '<table>';
    html += '<thead><tr>';
    html += '<th>Roll No</th><th>PRN</th><th>Name</th><th>Batch</th>';
    html += '<th>Classes Attended</th><th>Attendance %</th><th>Status</th>';
    html += '</tr></thead><tbody>';

    data.students.forEach(student => {
        const attendancePercent = data.total_classes > 0 
            ? ((student.attended / data.total_classes) * 100).toFixed(1)
            : 0;
        const statusClass = attendancePercent >= 75 ? 'status-present' : 'status-absent';
        const status = attendancePercent >= 75 ? 'Good' : 'Low';

        html += '<tr>';
        html += `<td>${student.rollno}</td>`;
        html += `<td>${student.prn}</td>`;
        html += `<td>${student.name}</td>`;
        html += `<td>${student.batch}</td>`;
        html += `<td>${student.attended} / ${data.total_classes}</td>`;
        html += `<td>${attendancePercent}%</td>`;
        html += `<td class="${statusClass}">${status}</td>`;
        html += '</tr>';
    });

    html += '</tbody></table>';
    mainDiv.innerHTML = html;
}