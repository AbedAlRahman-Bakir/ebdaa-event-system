if (!requireAuth(['admin', 'operator'])) { /* redirected */ }

let selectedDay = null;
let scanner = null;
let isProcessing = false;
const recentCheckins = [];

// ========== Day Selection ==========
document.querySelectorAll('.day-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        selectedDay = parseInt(btn.dataset.day);

        document.querySelectorAll('.day-btn').forEach(b => b.classList.remove('active', 'btn-primary'));
        document.querySelectorAll('.day-btn').forEach(b => b.classList.add('btn-outline-primary'));
        btn.classList.remove('btn-outline-primary');
        btn.classList.add('btn-primary', 'active');

        document.getElementById('no-day-warning').style.display = 'none';
        startScanner();
    });
});

// ========== Scanner ==========
function startScanner() {
    const readerEl = document.getElementById('reader');
    readerEl.style.display = 'block';

    if (scanner) {
        scanner.clear();
    }

    scanner = new Html5QrcodeScanner("reader", {
        fps: 10,
        qrbox: { width: 250, height: 250 },
        rememberLastUsedCamera: true,
    });

    scanner.render(onScanSuccess, onScanError);
}

async function onScanSuccess(qrCode) {
    if (isProcessing) return;
    isProcessing = true;

    // Pause scanner immediately
    scanner.pause(true);

    await processCheckin(qrCode);
}

function onScanError(error) {
    // Ignore scan errors (no QR in frame)
}

function resumeScanner() {
    isProcessing = false;
    document.getElementById('result-container').style.display = 'none';
    if (scanner) {
        scanner.resume();
    }
}

// ========== Manual Input ==========
function manualCheckin() {
    const qr = document.getElementById('manual-qr').value.trim();
    if (!qr) return;
    if (!selectedDay) { showResult('error', 'No Day Selected', 'Please select a day first'); return; }
    processCheckin(qr);
    document.getElementById('manual-qr').value = '';
}

document.getElementById('manual-qr').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') manualCheckin();
});

// ========== Process Check-in ==========
async function processCheckin(qrCode) {
    if (!selectedDay) {
        showResult('error', 'No Day Selected', 'Please select a day first');
        return;
    }

    try {
        const res = await fetch('/attendance/checkin', {
            method: 'POST',
            headers: authHeaders(),
            body: JSON.stringify({ qr_code: qrCode, day: selectedDay }),
        });

        const data = await res.json();

        if (res.status === 201) {
            showResult('success', data.message, `${data.data.user.role.toUpperCase()} — ID: ${data.data.user.id}`);
            addRecent(data.data.user.name, selectedDay, 'success');
        } else if (res.status === 409) {
            showResult('warning', data.message, `Already checked in at ${data.data.checkin_time}`);
            addRecent(data.message, selectedDay, 'warning');
        } else if (res.status === 404) {
            showResult('error', 'Invalid QR Code', 'This badge is not recognized');
            addRecent('Invalid QR scan', selectedDay, 'error');
        } else if (res.status === 401) {
            logout();
        } else {
            showResult('error', 'Error', data.message || 'Something went wrong');
        }
    } catch (err) {
        showResult('error', 'Connection Error', 'Could not reach the server');
    }
}

// ========== Show Result ==========
function showResult(type, title, message) {
    const container = document.getElementById('result-container');
    const card = document.getElementById('result-card');
    const icon = document.getElementById('result-icon');
    const titleEl = document.getElementById('result-title');
    const msgEl = document.getElementById('result-message');

    card.className = 'card result-card shadow-sm';

    if (type === 'success') {
        card.classList.add('result-success');
        icon.className = 'bi bi-check-circle-fill text-success fs-1 d-block mb-2';
    } else if (type === 'warning') {
        card.classList.add('result-warning');
        icon.className = 'bi bi-exclamation-circle-fill text-warning fs-1 d-block mb-2';
    } else {
        card.classList.add('result-error');
        icon.className = 'bi bi-x-circle-fill text-danger fs-1 d-block mb-2';
    }

    titleEl.textContent = title;
    msgEl.textContent = message;
    container.style.display = 'block';
}

// ========== Recent Check-ins List ==========
function addRecent(text, day, type) {
    recentCheckins.unshift({ text, day, type, time: new Date().toLocaleTimeString() });
    if (recentCheckins.length > 10) recentCheckins.pop();

    const list = document.getElementById('recent-list');
    list.innerHTML = recentCheckins.map(item => {
        let badgeClass = 'bg-success';
        if (item.type === 'warning') badgeClass = 'bg-warning text-dark';
        if (item.type === 'error') badgeClass = 'bg-danger';

        return `
            <li class="list-group-item d-flex justify-content-between align-items-center small">
                <span>${item.text}</span>
                <div>
                    <span class="badge bg-secondary me-1">Day ${item.day}</span>
                    <span class="badge ${badgeClass}">${item.time}</span>
                </div>
            </li>`;
    }).join('');
}
