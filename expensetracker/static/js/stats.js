const ctx = document.getElementById('myChart');

// Define the initial chart data
const initialChartData = {
  labels: [],
  datasets: [{
    label: 'Expenses',
    data: [],
    backgroundColor: 'rgba(54, 162, 235, 0.5)', // Set the bar color
    borderColor: 'rgba(54, 162, 235, 1)', // Set the border color
    borderWidth: 1
  }]
};

// Create the chart with initial data
const chart = new Chart(ctx, {
  type: 'bar',
  data: initialChartData,
  options: {
    responsive: true,
    scales: {
      y: {
        beginAtZero: true
      }
    }
  }
});

// Function to update the chart data
function updateChartData(data) {
  chart.data.labels = Object.keys(data);
  chart.data.datasets[0].data = Object.values(data);
  chart.update();
}

// Make an AJAX request to fetch the expense category summary data
fetch('expense_category_summary')
  .then(response => response.json())
  .then(data => updateChartData(data.expense_category_data))
  .catch(error => console.log(error));