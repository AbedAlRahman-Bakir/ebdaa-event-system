if (!requireAuth(['admin'])) { /* redirected */ }

let currentPage = 1;
let deleteUserId = null;

// ========== Load Users ==========
async function loadUsers() {
    const search = document.getElementById('search-input').value;
    const role = document.getElementById('role-filter').value;
    const perPage = document.getElementById('per-page').value;

    let url = `/users?page=${currentPage}&per_page=${perPage}`;
    if (role) url += `&role=${role}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;

    const res = await fetch(url, { headers: authHeaders() });
    if (res.status === 401) { logout(); return; }
    const data = await res.json();

    renderTable(data.data);
    renderPagination(data.total, data.page, parseInt(perPage));
    document.getElementById('table-info').textContent = `Showing ${data.data.length} of ${data.total} users`;
}

function renderTable(users) {
    const tbody = document.getElementById('users-table');
    if (users.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted py-4">No users found</td></tr>';
        return;
    }

    tbody.innerHTML = users.map(user => {
        const extra = user.extra_data || {};
        let details = '';
        if (user.role === 'student') {
            details = `${extra.school_name || ''} &middot; ${extra.province || ''}`;
        } else {
            details = `${extra.job_title || ''} &middot; ${extra.email || ''}`;
        }

        return `
            <tr>
                <td>${user.id}</td>
                <td class="fw-medium">${user.name}</td>
                <td><span class="badge ${user.role === 'student' ? 'bg-primary' : 'bg-success'}">${user.role}</span></td>
                <td class="text-muted small">${details}</td>
                <td><code class="small">${user.qr_code ? user.qr_code.substring(0, 12) + '...' : '-'}</code></td>
                <td class="text-end">
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" onclick="editUser(${user.id})" title="Edit">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-outline-secondary" onclick="downloadSingleBadge(${user.id}, '${user.name}')" title="Badge">
                            <i class="bi bi-qr-code"></i>
                        </button>
                        <button class="btn btn-outline-danger" onclick="confirmDelete(${user.id}, '${user.name}')" title="Delete">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>`;
    }).join('');
}

function renderPagination(total, page, perPage) {
    const totalPages = Math.ceil(total / perPage);
    const pagination = document.getElementById('pagination');

    if (totalPages <= 1) { pagination.innerHTML = ''; return; }

    let html = '';
    html += `<li class="page-item ${page === 1 ? 'disabled' : ''}">
        <a class="page-link" href="#" onclick="goToPage(${page - 1})">Prev</a></li>`;

    for (let i = 1; i <= totalPages; i++) {
        html += `<li class="page-item ${i === page ? 'active' : ''}">
            <a class="page-link" href="#" onclick="goToPage(${i})">${i}</a></li>`;
    }

    html += `<li class="page-item ${page === totalPages ? 'disabled' : ''}">
        <a class="page-link" href="#" onclick="goToPage(${page + 1})">Next</a></li>`;

    pagination.innerHTML = html;
}

function goToPage(page) {
    currentPage = page;
    loadUsers();
}

// ========== Create / Edit User ==========
document.getElementById('create-role').addEventListener('change', (e) => {
    document.getElementById('student-fields').style.display = e.target.value === 'student' ? 'block' : 'none';
    document.getElementById('judge-fields').style.display = e.target.value === 'judge' ? 'block' : 'none';
});

async function editUser(id) {
    const res = await fetch(`/users/${id}`, { headers: authHeaders() });
    if (res.status === 401) { logout(); return; }
    const data = await res.json();
    const user = data.data;
    const extra = user.extra_data || {};

    document.getElementById('edit-user-id').value = user.id;
    document.getElementById('create-name').value = user.name;
    document.getElementById('create-role').value = user.role;
    document.getElementById('create-role').dispatchEvent(new Event('change'));
    document.getElementById('createModalTitle').textContent = 'Edit User';

    if (user.role === 'student') {
        document.getElementById('create-school_name').value = extra.school_name || '';
        document.getElementById('create-province').value = extra.province || '';
        document.getElementById('create-project_name').value = extra.project_name || '';
        document.getElementById('create-project_id').value = extra.project_id || '';
        document.getElementById('create-project_sector').value = extra.project_sector || '';
    } else {
        document.getElementById('create-email').value = extra.email || '';
        document.getElementById('create-phone').value = extra.phone || '';
        document.getElementById('create-job_title').value = extra.job_title || '';
    }

    new bootstrap.Modal(document.getElementById('createModal')).show();
}

async function saveUser() {
    const editId = document.getElementById('edit-user-id').value;
    const role = document.getElementById('create-role').value;
    const name = document.getElementById('create-name').value;

    let extra_data = {};
    if (role === 'student') {
        extra_data = {
            school_name: document.getElementById('create-school_name').value,
            province: document.getElementById('create-province').value,
            project_name: document.getElementById('create-project_name').value,
            project_id: document.getElementById('create-project_id').value,
            project_sector: document.getElementById('create-project_sector').value,
        };
    } else {
        extra_data = {
            email: document.getElementById('create-email').value,
            phone: document.getElementById('create-phone').value,
            job_title: document.getElementById('create-job_title').value,
        };
    }

    const payload = { name, role, extra_data };
    const url = editId ? `/users/${editId}` : '/users';
    const method = editId ? 'PUT' : 'POST';

    const res = await fetch(url, {
        method,
        headers: authHeaders(),
        body: JSON.stringify(payload),
    });

    const data = await res.json();

    if (res.ok) {
        bootstrap.Modal.getInstance(document.getElementById('createModal')).hide();
        resetCreateForm();
        loadUsers();
        showToast(data.message, 'success');
    } else {
        document.getElementById('create-alert').innerHTML = `
            <div class="alert alert-danger alert-dismissible fade show small">
                ${data.message || 'Error saving user'}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>`;
    }
}

function resetCreateForm() {
    document.getElementById('edit-user-id').value = '';
    document.getElementById('create-form').reset();
    document.getElementById('student-fields').style.display = 'none';
    document.getElementById('judge-fields').style.display = 'none';
    document.getElementById('create-alert').innerHTML = '';
    document.getElementById('createModalTitle').textContent = 'Add User';
}

document.getElementById('createModal').addEventListener('hidden.bs.modal', resetCreateForm);

// ========== Delete User ==========
function confirmDelete(id, name) {
    deleteUserId = id;
    document.getElementById('delete-user-name').textContent = name;
    new bootstrap.Modal(document.getElementById('deleteModal')).show();
}

document.getElementById('confirm-delete-btn').addEventListener('click', async () => {
    const res = await fetch(`/users/${deleteUserId}`, {
        method: 'DELETE',
        headers: authHeaders(),
    });
    const data = await res.json();

    bootstrap.Modal.getInstance(document.getElementById('deleteModal')).hide();

    if (res.ok) {
        loadUsers();
        showToast(data.message, 'success');
    } else {
        showToast(data.message || 'Error deleting user', 'danger');
    }
});

// ========== Import ==========
async function importUsers() {
    const role = document.getElementById('import-role').value;
    const fileInput = document.getElementById('import-file');
    const file = fileInput.files[0];

    if (!file) {
        document.getElementById('import-alert').innerHTML =
            '<div class="alert alert-warning small">Please select a file</div>';
        return;
    }

    document.getElementById('import-btn').disabled = true;
    document.getElementById('import-btn').textContent = 'Importing...';

    const formData = new FormData();
    formData.append('file', file);

    const res = await fetch(`/users/import?role=${role}`, {
        method: 'POST',
        headers: { 'Authorization': 'Bearer ' + getToken() },
        body: formData,
    });

    const data = await res.json();
    document.getElementById('import-btn').disabled = false;
    document.getElementById('import-btn').innerHTML = '<i class="bi bi-upload me-1"></i>Import';

    if (res.ok) {
        let resultHtml = `<div class="alert alert-success small">Created: ${data.created}, Failed: ${data.failed}</div>`;
        if (data.errors && data.errors.length > 0) {
            resultHtml += '<ul class="list-unstyled small text-danger mb-0">';
            data.errors.forEach(err => {
                resultHtml += `<li>Row ${err.row}: ${JSON.stringify(err.errors)}</li>`;
            });
            resultHtml += '</ul>';
        }
        document.getElementById('import-result').innerHTML = resultHtml;
        document.getElementById('import-result').style.display = 'block';
        loadUsers();
    } else {
        document.getElementById('import-alert').innerHTML =
            `<div class="alert alert-danger small">${data.message}</div>`;
    }
}

// ========== Export / Badges ==========
async function downloadSingleBadge(id, name) {
    const res = await fetch(`/users/${id}/badge`, {
        headers: { 'Authorization': 'Bearer ' + getToken() },
    });
    if (!res.ok) { showToast('Failed to download badge', 'danger'); return; }
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `badge_${name.replace(/ /g, '_')}_${id}.pdf`;
    a.click();
    URL.revokeObjectURL(url);
}

async function downloadBadges(role) {
    const res = await fetch(`/users/badges?role=${role}`, {
        headers: { 'Authorization': 'Bearer ' + getToken() },
    });
    if (!res.ok) { showToast('Failed to download badges', 'danger'); return; }
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `badges_${role}s.pdf`;
    a.click();
    URL.revokeObjectURL(url);
}

async function exportContacts(role) {
    const res = await fetch(`/users/export?role=${role}`, {
        headers: { 'Authorization': 'Bearer ' + getToken() },
    });
    if (!res.ok) { showToast('Failed to export contacts', 'danger'); return; }
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${role}s_contacts.csv`;
    a.click();
    URL.revokeObjectURL(url);
}

// ========== Toast ==========
function showToast(message, type) {
    const toast = document.getElementById('toast');
    const body = document.getElementById('toast-body');
    toast.className = `toast bg-${type} text-white`;
    body.innerHTML = `<i class="bi bi-${type === 'success' ? 'check-circle' : 'x-circle'}"></i> ${message}`;
    new bootstrap.Toast(toast, { delay: 3000 }).show();
}

// ========== Filters ==========
let searchTimeout;
document.getElementById('search-input').addEventListener('input', () => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => { currentPage = 1; loadUsers(); }, 300);
});

document.getElementById('role-filter').addEventListener('change', () => { currentPage = 1; loadUsers(); });
document.getElementById('per-page').addEventListener('change', () => { currentPage = 1; loadUsers(); });

// Initial load
loadUsers();
