$(document).ready(function () {

  var settings = {
    "async": true,
    "crossDomain": true,
    "url": "common",
    "method": "GET",
    "headers": {
      "cache-control": "no-cache"
    }
  }

  $.ajax(settings).done(function (response) {
    console.log(response);

    function renderCount(selector, count, limit) {
      var $el = $(selector);
      if (!$el.length) return;

      if (limit !== undefined && limit !== null && limit !== '' && !isNaN(limit)) {
        $el.text(count + ' / ' + limit);
      } else {
        $el.text(count);
      }
    }

    // Base counts
    renderCount('#patientcount', response.patient);
    renderCount('#doctorcount', response.doctor, $('#doctorcount').data('limit'));
    renderCount('#appointmentcount', response.appointment);
    renderCount('#medicationcount', response.medication);
    renderCount('#departmentcount', response.department, $('#departmentcount').data('limit'));
    renderCount('#nursecount', response.nurse);
    renderCount('#roomcount', response.room, $('#roomcount').data('limit'));
    renderCount('#proccount', response.procedure);
    renderCount('#prescribescount', response.prescribes);
    renderCount('#undergoescount', response.undergoes);

    // Compact analytics chart (single dataset)
    var ctx = document.getElementById('dashboard-analytics');
    if (ctx && window.Chart) {
      // Destroy any previous chart on this canvas to avoid stacking
      if (window.dashboardAnalyticsChart) {
        window.dashboardAnalyticsChart.destroy();
      }

      var labels = ['Patients', 'Doctors', 'Appointments', 'Rooms', 'Prescriptions', 'Undergoes'];
      var values = [
        response.patient || 0,
        response.doctor || 0,
        response.appointment || 0,
        response.room || 0,
        response.prescribes || 0,
        response.undergoes || 0
      ];

      window.dashboardAnalyticsChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [{
            label: 'Current counts',
            data: values,
            borderColor: '#10b981',
            backgroundColor: 'rgba(16, 185, 129, 0.15)',
            tension: 0.35,
            fill: true,
            pointRadius: 4,
            pointHoverRadius: 5
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: {
            mode: 'index',
            intersect: false
          },
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              backgroundColor: '#0f172a',
              titleColor: '#f9fafb',
              bodyColor: '#e5e7eb'
            }
          },
          scales: {
            x: {
              grid: {
                display: false
              }
            },
            y: {
              beginAtZero: true,
              ticks: {
                precision: 0
              }
            }
          }
        }
      });
    }
  });


})
