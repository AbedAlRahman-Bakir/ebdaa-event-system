const slotsContainer = document.getElementById('slots-container');
const slotsList = document.getElementById('slots-list');
const slotInput = document.getElementById('time_slot_id');
const submitBtn = document.getElementById('submit-btn');
const alertContainer = document.getElementById('alert-container');
let allSlots = [];
let selectedDay = null;

// Fetch all slots on page load
fetch('/visitors/slots')
    .then(res => res.json())
    .then(data => { allSlots = data.data; });

// Day selection
document.querySelectorAll('.day-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        selectedDay = btn.dataset.day;

        // Toggle active state
        document.querySelectorAll('.day-btn').forEach(b => b.classList.remove('active', 'btn-primary'));
        document.querySelectorAll('.day-btn').forEach(b => b.classList.add('btn-outline-primary'));
        btn.classList.remove('btn-outline-primary');
        btn.classList.add('btn-primary', 'active');

        // Show slots for selected day
        renderSlots(selectedDay);
    });
});

function renderSlots(day) {
    const daySlots = allSlots.filter(s => s.day === parseInt(day));
    slotsList.innerHTML = '';
    slotInput.value = '';
    submitBtn.disabled = true;

    if (daySlots.length === 0) {
        slotsList.innerHTML = '<p class="text-muted small">No slots available for this day.</p>';
        slotsContainer.style.display = 'block';
        return;
    }

    daySlots.forEach(slot => {
        const available = slot.capacity - slot.booked_count;
        const isFull = available <= 0;
        const card = document.createElement('div');
        card.className = `border rounded-3 p-3 d-flex justify-content-between align-items-center slot-card ${isFull ? 'opacity-50' : ''}`;
        card.style.cursor = isFull ? 'not-allowed' : 'pointer';
        card.innerHTML = `
            <div>
                <i class="bi bi-clock me-2"></i>
                <strong>${slot.start_time} - ${slot.end_time}</strong>
            </div>
            <div>
                <span class="badge ${isFull ? 'bg-danger' : 'bg-success'}">${isFull ? 'Full' : available + ' spots left'}</span>
            </div>
        `;

        if (!isFull) {
            card.addEventListener('click', () => {
                document.querySelectorAll('.slot-card').forEach(c => c.classList.remove('border-primary', 'bg-primary', 'bg-opacity-10'));
                card.classList.add('border-primary', 'bg-primary', 'bg-opacity-10');
                slotInput.value = slot.id;
                submitBtn.disabled = false;
            });
        }

        slotsList.appendChild(card);
    });

    slotsContainer.style.display = 'block';
}

// Form submission
document.getElementById('register-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    alertContainer.innerHTML = '';
    submitBtn.disabled = true;
    submitBtn.textContent = 'Registering...';

    const payload = {
        name: document.getElementById('name').value,
        email: document.getElementById('email').value,
        phone: document.getElementById('phone').value,
        city: document.getElementById('city').value,
        type: document.getElementById('type').value,
        group_size: parseInt(document.getElementById('group_size').value),
        time_slot_id: parseInt(slotInput.value),
    };

    try {
        const res = await fetch('/visitors/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });

        const data = await res.json();

        if (res.ok) {
            document.getElementById('success-message').textContent = data.message;
            new bootstrap.Modal(document.getElementById('successModal')).show();
            document.getElementById('register-form').reset();
            slotsContainer.style.display = 'none';
            document.querySelectorAll('.day-btn').forEach(b => {
                b.classList.remove('active', 'btn-primary');
                b.classList.add('btn-outline-primary');
            });
        } else {
            showAlert(data.message || 'Registration failed', 'danger');
            submitBtn.disabled = false;
        }
    } catch (err) {
        showAlert('Something went wrong. Please try again.', 'danger');
        submitBtn.disabled = false;
    }

    submitBtn.textContent = 'Register';
});

function showAlert(message, type) {
    alertContainer.innerHTML = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>`;
}
