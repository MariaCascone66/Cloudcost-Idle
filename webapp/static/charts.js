async function updateChart() {
    const res = await fetch('/data');
    const data = await res.json();
  
    chart.data.datasets[0].data = [data.cpu, data.ram];
    chart.update();
  
    document.getElementById('co2').innerText = `Stima CO₂: ${data.co2} kg`;
  }
  
  const ctx = document.getElementById('usageChart').getContext('2d');
  const chart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['CPU (%)', 'RAM (MB)'],
      datasets: [{
        label: 'Utilizzo Risorse',
        backgroundColor: ['#3e95cd', '#8e5ea2'],
        data: [0, 0]
      }]
    },
    options: {
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });
  
  setInterval(updateChart, 3000);
  