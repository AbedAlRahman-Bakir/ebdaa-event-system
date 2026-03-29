if (!requireAuth(['admin'])) { /* redirected */ }

let currentPage = 1;

async function loadAttendance() {
    const day = document.getElementById('day-filter').value;
    const role = document.getElementById('role-filter').value;
    const perPage = document.getElementById('per-page').value;

    let url = `/attendance?page=${currentPage}&per_page=${perPage}`;
    if (day) url += `&day=${day}`;
    if (role) url += `&role=${role}`;

    const res = await fetch(url, { headers: authHeaders() });
    if (res.status === 401) { logout(); return; }
    const data = await res.json();

    renderTable(data.data);
    renderPagination(data.total, data.page, parseInt(perPage));
    document.getElementById('table-info').textContent = `${data.total} records`;
    document.getElementById('page-info').textContent = `Showing ${data.data.length} of ${data.total}`;
}

function renderTable(logs) {
    const tbody = document.getElementById('attendance-table');
    if (logs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted py-4">No attendance records found</td></tr>';
        return;
    }

    tbody.innerHTML = logs.map(log => {
        const time = new Date(log.checkin_time).toLocaleString();
        const roleBadge = log.user_role === 'student' ? 'bg-primary' : 'bg-success';
        return `
            <tr>
                <td>${log.id}</td>
                <td class="fw-medium">${log.user_name}</td>
                <td><span class="badge ${roleBadge}">${log.user_role}</span></td>
                <td><span class="badge bg-secondary">Day ${log.day}</span></td>
                <td class="text-muted small">${time}</td>
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
    loadAttendance();
}

// Filters
document.getElementById('day-filter').addEventListener('change', () => { currentPage = 1; loadAttendance(); });
document.getElementById('role-filter').addEventListener('change', () => { currentPage = 1; loadAttendance(); });
document.getElementById('per-page').addEventListener('change', () => { currentPage = 1; loadAttendance(); });

// Initial load
loadAttendance();
