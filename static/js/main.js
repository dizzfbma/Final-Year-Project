// static/js/main.js - Unified Script for Table + Charts Refresh

let anomalyChart, commandChart;

async function fetchAndUpdate() {
    const res = await fetch('/api/events');
    const data = await res.json();

    updateTable(data);
    updateCharts(data);
}

function updateTable(events) {
    const tbody = document.getElementById('eventTable');
    tbody.innerHTML = '';

    events.forEach(evt => {
        const row = document.createElement('tr');
        if (evt.is_anomaly) row.classList.add('anomaly');

        row.innerHTML = `
            <td>${evt.timestamp}</td>
            <td>${evt.src_ip}</td>
            <td>${evt.username}</td>
            <td>${evt.password}</td>
            <td>${evt.commands}</td>
            <td>${evt.is_anomaly ? 'Yes' : 'No'}</td>
        `;
        tbody.appendChild(row);
    });
}

function updateCharts(events) {
    let anomalies = 0, normals = 0;
    const commandCount = {};

    events.forEach(evt => {
        if (evt.is_anomaly) anomalies++; else normals++;
        const cmd = evt.commands || evt.input || "";
        if (cmd) commandCount[cmd] = (commandCount[cmd] || 0) + 1;
    });

    // Update Anomaly Chart
    if (anomalyChart) anomalyChart.destroy();
    anomalyChart = new Chart(document.getElementById('anomalyChart'), {
        type: 'doughnut',
        data: {
            labels: ['Anomalies', 'Normal'],
            datasets: [{
                data: [anomalies, normals],
                backgroundColor: ['#e74c3c', '#2ecc71']
            }]
        },
        options: {
            plugins: { title: { display: true, text: 'Anomaly vs Normal Events' } }
        }
    });

    // Update Command Chart
    if (commandChart) commandChart.destroy();
    commandChart = new Chart(document.getElementById('commandChart'), {
        type: 'bar',
        data: {
            labels: Object.keys(commandCount),
            datasets: [{
                label: 'Command Frequency',
                data: Object.values(commandCount),
                backgroundColor: '#2980b9'
            }]
        },
        options: {
            plugins: { title: { display: true, text: 'Command Usage Frequency' } },
            scales: { x: { ticks: { autoSkip: false } } }
        }
    });
}

// Initial call
fetchAndUpdate();

// Refresh every 10 seconds
setInterval(fetchAndUpdate, 10000);