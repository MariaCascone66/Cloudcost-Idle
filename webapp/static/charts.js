function drawChart(data) {
    const ctx = document.getElementById('usageChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['CPU %', 'RAM (MB)', 'CO2 (kg)'],
            datasets: [{
                label: 'Estimated Resource Usage',
                data: [data.cpu, data.ram, data.co2_estimate],
                backgroundColor: ['#4CAF50', '#2196F3', '#FFC107']
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}
