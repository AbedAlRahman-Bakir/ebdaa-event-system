// Check admin access
if (!requireAuth(['admin'])) {
    // redirected
}

let attendanceChart = null;
let rateChart = null;

async function loadDashboard() {
    await Promise.all([loadStats(), loadAttendance(), loadSlots()]);
    document.getElementById('last-updated').textContent = 'Updated: ' + new Date().toLocaleTimeString();
}

// ========== Stats ==========
async function loadStats() {
    const res = await fetch('/dashboard/stats', { headers: authHeaders() });
    if (res.status === 401) { logout(); return; }
    const data = await res.json();
    const stats = data.data;

    document.getElementById('stat-students').textContent = stats.total_students;
    document.getElementById('stat-judges').textContent = stats.total_judges;
    document.getElementById('stat-visitors').textContent = stats.total_visitors;
    document.getElementById('stat-checkins').textContent = stats.total_attendance_logs;
}

// ========== Attendance Chart ==========
async function loadAttendance() {
    const res = await fetch('/dashboard/attendance', { headers: authHeaders() });
    if (res.status === 401) { logout(); return; }
    const data = await res.json();
    const att = data.data;

    const days = ['1', '2', '3', '4', '5', '6'];
    const studentData = days.map(d => (att.heatmap.student && att.heatmap.student[d]) || 0);
    const judgeData = days.map(d => (att.heatmap.judge && att.heatmap.judge[d]) || 0);
    const rate = att.cumulative_rate;

    // Attendance bar chart
    if (attendanceChart) {
        attendanceChart.data.datasets[0].data = studentData;
        attendanceChart.data.datasets[1].data = judgeData;
        attendanceChart.update();
    } else {
        const ctx = document.getElementById('attendanceChart').getContext('2d');
        attendanceChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: days.map(d => 'Day ' + d),
                datasets: [
                    {
                        label: 'Students',
                        data: studentData,
                        backgroundColor: 'rgba(37, 99, 235, 0.7)',
                        borderRadius: 4,
                    },
                    {
                        label: 'Judges',
                        data: judgeData,
                        backgroundColor: 'rgba(16, 185, 129, 0.7)',
                        borderRadius: 4,
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'top' } },
                scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } },
            }
        });
    }

    // Rate doughnut chart
    if (rateChart) {
        rateChart.data.datasets[0].data = [rate, 100 - rate];
        rateChart.options.plugins.centerText = rate;
        rateChart.update();
    } else {
        const rateCtx = document.getElementById('rateChart').getContext('2d');
        rateChart = new Chart(rateCtx, {
            type: 'doughnut',
            data: {
                labels: ['Present', 'Absent'],
                datasets: [{
                    data: [rate, 100 - rate],
                    backgroundColor: ['rgba(37, 99, 235, 0.8)', 'rgba(229, 231, 235, 1)'],
                    borderWidth: 0,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: true },
                }
            },
            plugins: [{
                id: 'centerText',
                afterDraw(chart) {
                    const { ctx, width, height } = chart;
                    ctx.save();
                    ctx.font = 'bold 24px sans-serif';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillStyle = '#1a1a2e';
                    ctx.fillText(rate + '%', width / 2, height / 2);
                    ctx.restore();
                }
            }]
        });
    }
}

// ========== Slot Utilization ==========
async function loadSlots() {
    const res = await fetch('/dashboard/slots', { headers: authHeaders() });
    if (res.status === 401) { logout(); return; }
    const data = await res.json();
    const slots = data.data;

    const tbody = document.getElementById('slots-table');
    tbody.innerHTML = '';

    Object.keys(slots).sort().forEach(day => {
        slots[day].forEach(slot => {
            const pct = slot.utilization;
            let barColor = 'bg-success';
            if (pct > 80) barColor = 'bg-danger';
            else if (pct > 50) barColor = 'bg-warning';

            tbody.innerHTML += `
                <tr>
                    <td>Day ${day}</td>
                    <td>${slot.start_time} - ${slot.end_time}</td>
                    <td>${slot.booked}</td>
                    <td>${slot.capacity}</td>
                    <td style="min-width:150px;">
                        <div class="progress" style="height:20px;">
                            <div class="progress-bar ${barColor}" style="width:${pct}%">${pct}%</div>
                        </div>
                    </td>
                </tr>`;
        });
    });
}

// Load on page ready and refresh every 30 seconds
loadDashboard();
setInterval(loadDashboard, 30000);
