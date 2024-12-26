// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

// Pie Chart Example
var ctx = document.getElementById("myPieChart");
var myPieChart = new Chart(ctx, {
  type: 'doughnut',
  data: {
    labels: ["up", "down", "unknown", "pending", "denied", "rejected"],
    datasets: [{
      data: [hosts_status_collect[0], hosts_status_collect[1], hosts_status_collect[2], hosts_status_collect[3], hosts_status_collect[4], hosts_status_collect[5]],
      backgroundColor: ['#4e73df', '#1cc88a', '#36b9cc', '#858796', '#f6c23e', '#e74a3b'],
      hoverBackgroundColor: ['#4e73df', '#1cc88a', '#36b9cc', '#858796', '#f6c23e', '#e74a3b'],
      hoverBorderColor: "rgba(234, 236, 244, 1)",
    }],
  },
  options: {
    maintainAspectRatio: false,
    tooltips: {
      backgroundColor: "rgb(255,255,255)",
      bodyFontColor: "#858796",
      borderColor: '#dddfeb',
      borderWidth: 1,
      xPadding: 15,
      yPadding: 15,
      displayColors: false,
      caretPadding: 10,
    },
    legend: {
      display: false
    },
    cutoutPercentage: 80,
  },
});
