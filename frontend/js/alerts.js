let currentFilter = 'all';

async function loadUserInfo() {
  try {
    const user = await Api.user();
    document.getElementById("userInfo").textContent = `${user.login} (${user.role})`;
  } catch (e) {
    console.error("Failed to load user info:", e);
  }
}

async function loadAlerts(status = null) {
  try {
    const alerts = await Api.alerts(status);
    const tbody = document.getElementById("alertsTable");
    
    if (alerts.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" class="text-center">Попереджень не знайдено</td></tr>';
      return;
    }
    
    tbody.innerHTML = alerts.map(alert => `
      <tr>
        <td>${alert.id}</td>
        <td>${alert.message}</td>
        <td><span class="badge bg-${getLevelClass(alert.level)}">${alert.level}</span></td>
        <td><span class="badge bg-${getStatusClass(alert.status)}">${alert.status}</span></td>
        <td>${new Date(alert.created_at).toLocaleString()}</td>
        <td>
          <div class="btn-group btn-group-sm">
            ${alert.status !== 'resolved' ? 
              `<button class="btn btn-outline-success" onclick="updateAlertStatus(${alert.id}, 'resolved')">Вирішити</button>` : 
              ''}
            ${alert.status === 'new' ? 
              `<button class="btn btn-outline-warning" onclick="updateAlertStatus(${alert.id}, 'in_progress')">В процесі</button>` : 
              ''}
          </div>
        </td>
      </tr>
    `).join('');
  } catch (e) {
    console.error("Failed to load alerts:", e);
    document.getElementById("alertsTable").innerHTML = '<tr><td colspan="6" class="text-center text-danger">Помилка завантаження</td></tr>';
  }
}

function getLevelClass(level) {
  const classes = {
    'critical': 'danger',
    'warning': 'warning',
    'info': 'info'
  };
  return classes[level] || 'secondary';
}

function getStatusClass(status) {
  const classes = {
    'new': 'danger',
    'in_progress': 'warning',
    'resolved': 'success'
  };
  return classes[status] || 'secondary';
}

function filterAlerts(status) {
  currentFilter = status;
  
  // Update button states
  document.querySelectorAll('.btn-group .btn').forEach(btn => {
    btn.classList.remove('active');
    if (btn.textContent.toLowerCase().includes(status === 'all' ? 'всі' : 
        status === 'new' ? 'нові' : 
        status === 'in_progress' ? 'процесі' : 'вирішені')) {
      btn.classList.add('active');
    }
  });
  
  // Load alerts with filter
  loadAlerts(status === 'all' ? null : status);
}

async function updateAlertStatus(alertId, newStatus) {
  try {
    await Api.updateAlert(alertId, newStatus);
    loadAlerts(currentFilter === 'all' ? null : currentFilter);
  } catch (e) {
    console.error("Failed to update alert status:", e);
    alert('Не вдалося оновити статус: ' + e.message);
  }
}

if (requireAuth()) {
  bindLogout();
  bindUserNav();
  loadAlerts();
}