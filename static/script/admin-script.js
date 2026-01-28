function setupPinInputs(selector) {
    const inputs = document.querySelectorAll(selector);
    inputs.forEach((input, index) => {
        input.addEventListener('input', (e) => {
            if (!/^[0-9]$/.test(e.target.value)) {
                e.target.value = '';
                return;
            }
            if (e.target.value && index < inputs.length - 1) {
                inputs[index + 1].focus();
            }
        });

        input.addEventListener('keydown', (e) => {
            if (e.key === 'Backspace' && !input.value && index > 0) {
                inputs[index - 1].focus();
            }
        });
    });
}

setupPinInputs('.add-pin');
setupPinInputs('.change-pin');

function logout() {
    window.location.href = '/logout';
}

function showMessage(message, type) {
    const messageDiv = document.getElementById('message');
    messageDiv.className = type;
    messageDiv.textContent = message;
    setTimeout(() => {
        messageDiv.className = '';
        messageDiv.textContent = '';
    }, 3000);
}

async function loadUsers() {
    try {
        const response = await fetch('/admin/users');
        const users = await response.json();
        
        const tbody = document.getElementById('usersBody');
        if (users.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="no-users">No users found</td></tr>';
            return;
        }

        tbody.innerHTML = users.map(user => `
            <tr>
                <td>${user.id}</td>
                <td>${user.username}</td>
                <td>${user.email}</td>
                <td><span class="badge badge-${user.user_type}">${user.user_type}</span></td>
                <td>${new Date(user.created_at).toLocaleDateString("en-GB")}</td>
                <td>
                    <div class="action-btns">
                        <button class="btn-change" onclick="openChangeModal(${user.id}, '${user.username}')">
                            Change PIN
                        </button>
                        <button class="btn-delete" onclick="deleteUser(${user.id}, '${user.username}')">
                            Delete
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        showMessage('Error loading users', 'error');
    }
}

function openAddModal() {
    document.getElementById('addModal').classList.add('show');
    document.getElementById('add_username').focus();
}

function closeAddModal() {
    document.getElementById('addModal').classList.remove('show');
    document.getElementById('addUserForm').reset();
}

function openChangeModal(userId, username) {
    document.getElementById('change_user_id').value = userId;
    document.getElementById('change_username').value = username;
    document.getElementById('changeModal').classList.add('show');
    document.querySelector('.change-pin').focus();
}

function closeChangeModal() {
    document.getElementById('changeModal').classList.remove('show');
    document.getElementById('changePasswordForm').reset();
}

async function addUser(event) {
    event.preventDefault();
    
    const username = document.getElementById('add_username').value;
    const email = document.getElementById('add_email').value;
    const userType = document.getElementById('add_user_type').value;
    const pinInputs = document.querySelectorAll('.add-pin');
    const pin = Array.from(pinInputs).map(input => input.value).join('');

    if (pin.length !== 4) {
        showMessage('Please enter a 4-digit PIN', 'error');
        return;
    }

    try {
        const response = await fetch('/admin/add-user', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, user_type: userType, pin })
        });

        const data = await response.json();

        if (response.ok) {
            showMessage(data.message, 'success');
            closeAddModal();
            loadUsers();
        } else {
            showMessage(data.message, 'error');
        }
    } catch (error) {
        showMessage('Error adding user', 'error');
    }
}

async function changePassword(event) {
    event.preventDefault();
    
    const userId = document.getElementById('change_user_id').value;
    const pinInputs = document.querySelectorAll('.change-pin');
    const pin = Array.from(pinInputs).map(input => input.value).join('');

    if (pin.length !== 4) {
        showMessage('Please enter a 4-digit PIN', 'error');
        return;
    }

    try {
        const response = await fetch('/admin/change-password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, new_pin: pin })
        });

        const data = await response.json();

        if (response.ok) {
            showMessage(data.message, 'success');
            closeChangeModal();
        } else {
            showMessage(data.message, 'error');
        }
    } catch (error) {
        showMessage('Error changing password', 'error');
    }
}

async function deleteUser(userId, username) {
    if (!confirm(`Are you sure you want to delete user "${username}"?`)) {
        return;
    }

    try {
        const response = await fetch('/admin/delete-user', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId })
        });

        const data = await response.json();

        if (response.ok) {
            showMessage(data.message, 'success');
            loadUsers();
        } else {
            showMessage(data.message, 'error');
        }
    } catch (error) {
        showMessage('Error deleting user', 'error');
    }
}

window.addEventListener('load', loadUsers);