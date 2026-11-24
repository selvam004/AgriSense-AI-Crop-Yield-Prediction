// AgriSense Client Application (Django Edition)

document.addEventListener('DOMContentLoaded', () => {
  // Set default planting date to today
  const dateInput = document.getElementById('date');
  if (dateInput && !dateInput.value) {
    const today = new Date().toISOString().split('T')[0];
    dateInput.value = today;
  }

  // Navigation active link tracking
  const navLinks = document.querySelectorAll('nav a.nav-link');
  navLinks.forEach(link => {
    link.addEventListener('click', function() {
      navLinks.forEach(a => a.classList.remove('active'));
      this.classList.add('active');
    });
  });

  // CSRF helper function for Django
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  // 1. Prediction Form Handler
  const predictForm = document.getElementById('predictForm');
  const predictBtn = document.getElementById('predictBtn');
  const resultPlaceholder = document.getElementById('resultPlaceholder');
  const resultContent = document.getElementById('resultContent');
  const yieldNumber = document.getElementById('yieldNumber');
  const confidenceVal = document.getElementById('confidenceVal');
  const confidenceBar = document.getElementById('confidenceBar');
  const soilStatus = document.getElementById('soilStatus');
  const weatherStatus = document.getElementById('weatherStatus');
  const tipsList = document.getElementById('tipsList');

  if (predictForm) {
    predictForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      const lat = parseFloat(document.getElementById('lat').value);
      const lon = parseFloat(document.getElementById('lon').value);
      const crop = document.getElementById('crop').value;
      const date = document.getElementById('date').value;
      const irrigation = document.getElementById('irrigation').checked;

      // Loading state
      predictBtn.disabled = true;
      predictBtn.querySelector('.btn-text').style.display = 'none';
      predictBtn.querySelector('.btn-spinner').style.display = 'inline';

      try {
        const res = await fetch('/predict', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken') || ''
          },
          body: JSON.stringify({
            latitude: lat,
            longitude: lon,
            crop_type: crop,
            planting_date: date,
            irrigation: irrigation,
            // Flask compatibility alias keys
            lat: lat,
            lon: lon,
            crop: crop,
            date: date
          })
        });

        const data = await res.json();

        if (res.ok && data.predicted_yield !== undefined) {
          resultPlaceholder.style.display = 'none';
          resultContent.style.display = 'block';

          yieldNumber.textContent = data.predicted_yield;
          confidenceVal.textContent = `${data.confidence}%`;
          confidenceBar.style.width = `${data.confidence}%`;

          soilStatus.textContent = data.soil_suitability || '🌱 Ideal soil conditions detected';
          weatherStatus.textContent = data.growth_potential || '🌾 Weather conditions suggest moderate to high growth';

          tipsList.innerHTML = '';
          const tipsArray = data.tips || [];
          tipsArray.forEach(tip => {
            const li = document.createElement('li');
            li.textContent = tip;
            tipsList.appendChild(li);
          });

          // Smooth scroll to results
          document.getElementById('predictionResultCard').scrollIntoView({ behavior: 'smooth' });

          // Refresh history table
          loadHistory();
        } else {
          alert('Error: ' + (data.error || 'Failed to compute prediction.'));
        }
      } catch (err) {
        console.error('Prediction request error:', err);
        alert('Server connection error. Please make sure Django server is running.');
      } finally {
        predictBtn.disabled = false;
        predictBtn.querySelector('.btn-text').style.display = 'inline';
        predictBtn.querySelector('.btn-spinner').style.display = 'none';
      }
    });
  }

  // 2. Field Insights Handler
  const showInsightsBtn = document.getElementById('showInsightsBtn');
  const insightsSpinner = document.getElementById('insightsSpinner');
  const insightsMsg = document.getElementById('insightsMsg');

  if (showInsightsBtn) {
    showInsightsBtn.addEventListener('click', async () => {
      const latVal = document.getElementById('lat').value;
      const lonVal = document.getElementById('lon').value;

      if (!latVal || !lonVal) {
        insightsMsg.textContent = '⚠️ Please enter latitude and longitude in the prediction form above!';
        document.getElementById('lat').focus();
        return;
      }

      insightsMsg.textContent = '';
      showInsightsBtn.disabled = true;
      insightsSpinner.style.display = 'inline';

      try {
        const res = await fetch('/insights', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken') || ''
          },
          body: JSON.stringify({
            latitude: parseFloat(latVal),
            longitude: parseFloat(lonVal),
            lat: parseFloat(latVal),
            lon: parseFloat(lonVal)
          })
        });

        const data = await res.json();

        if (res.ok) {
          // Weather
          if (data.weather) {
            document.getElementById('tempVal').textContent = data.weather.temp || `${data.weather.temp_val}°C`;
            document.getElementById('rainVal').textContent = data.weather.rain || `${data.weather.rainfall}mm`;
            document.getElementById('humidityVal').textContent = data.weather.humidity || `${data.weather.humidity_val}%`;
          }
          // Soil
          if (data.soil) {
            document.getElementById('phVal').textContent = data.soil.ph;
            document.getElementById('carbonVal').textContent = data.soil.carbon || `${data.soil.carbon_val}%`;
            document.getElementById('nitrogenVal').textContent = data.soil.nitrogen || `${data.soil.nitrogen_val} mg/kg`;
          }
          // Irrigation
          if (data.irrigation) {
            document.getElementById('irrigStatusVal').textContent = data.irrigation.status;
            document.getElementById('irrigEffVal').textContent = data.irrigation.efficiency || `${data.irrigation.efficiency_val}%`;
            document.getElementById('waterIndexVal').textContent = data.irrigation.index || `${data.irrigation.index_val}`;
          }
        } else {
          insightsMsg.textContent = '⚠️ ' + (data.error || 'Failed to fetch insights.');
        }
      } catch (err) {
        console.error('Insights fetch failed:', err);
        insightsMsg.textContent = '⚠️ Could not connect to backend service.';
      } finally {
        showInsightsBtn.disabled = false;
        insightsSpinner.style.display = 'none';
      }
    });
  }

  // 3. Database History Refresh Handler
  const refreshHistoryBtn = document.getElementById('refreshHistoryBtn');
  if (refreshHistoryBtn) {
    refreshHistoryBtn.addEventListener('click', () => {
      loadHistory();
    });
  }

  async function loadHistory() {
    try {
      const res = await fetch('/api/history/');
      const data = await res.json();
      const tbody = document.getElementById('historyTableBody');
      if (!tbody || !data.history) return;

      if (data.history.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center">No predictions saved yet.</td></tr>';
        return;
      }

      tbody.innerHTML = '';
      data.history.forEach(item => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>#${item.id}</td>
          <td><strong>${item.crop}</strong></td>
          <td>${item.lat.toFixed(2)}, ${item.lon.toFixed(2)}</td>
          <td><span class="yield-tag">${item.yield} t/ha</span></td>
          <td>${item.confidence}%</td>
          <td>${item.date}</td>
        `;
        tbody.appendChild(tr);
      });
    } catch (e) {
      console.warn('Could not refresh history table:', e);
    }
  }
});

// Quick Coordinate Preset Helper
function setPreset(lat, lon, crop) {
  const latInput = document.getElementById('lat');
  const lonInput = document.getElementById('lon');
  const cropSelect = document.getElementById('crop');

  if (latInput) latInput.value = lat;
  if (lonInput) lonInput.value = lon;
  if (cropSelect) cropSelect.value = crop;

  // Trigger slight visual highlight
  latInput.style.borderColor = '#4CAF50';
  lonInput.style.borderColor = '#4CAF50';
  setTimeout(() => {
    latInput.style.borderColor = '';
    lonInput.style.borderColor = '';
  }, 1000);
}
