const ctx = document.getElementById('performanceChart').getContext('2d');

new Chart(ctx, {
    type: 'line',
    data: {
        labels: labels.map(id => `ID ${id}`),
        datasets: [
            {
                label: 'Attendance (%)',
                data: attendanceData,
                borderWidth: 2,
                borderColor: '#007bff',
                fill: false,
                tension: 0.2
            },
            {
                label: 'Internal Marks (%)',
                data: marksData,
                borderWidth: 2,
                borderColor: '#28a745',
                fill: false,
                tension: 0.2
            },
            {
                label: 'Predicted Result',
                data: predictionData,
                borderWidth: 2,
                borderColor: '#ffc107',
                fill: false,
                tension: 0.2
            }
        ]
    },
    options: {
        responsive: true,
        plugins: {
            title: {
                display: true,
                text: 'Performance Overview'
            },
            legend: {
                position: 'bottom'
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                max: 100
            }
        }
    }
});
