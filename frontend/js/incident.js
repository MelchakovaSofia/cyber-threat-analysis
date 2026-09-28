async function loadIncident() {
  const id = localStorage.getItem("current_threat_id") || new URLSearchParams(location.search).get("id");
  const box = document.getElementById("incident");
  if (!id) {
    box.innerHTML = '<div class="alert alert-warning">Інцидент не вибрано. Поверніться на dashboard.</div>';
    return;
  }
  try {
    const data = await Api.threat(id);
    const t = data.threat;
    const log = data.log;
    box.innerHTML = `
      <div class="row g-3">
        <div class="col-md-6">
          <div class="card h-100"><div class="card-body">
            <h2 class="h6">Загроза #${t.id}</h2>
            <dl class="row mb-0">
              <dt class="col-sm-4">Тип</dt><dd class="col-sm-8">${escapeHtml(t.threat_type)}</dd>
              <dt class="col-sm-4">Ймовірність</dt><dd class="col-sm-8">${t.probability.toFixed(4)}</dd>
              <dt class="col-sm-4">Рівень</dt><dd class="col-sm-8">${escapeHtml(t.severity)}</dd>
              <dt class="col-sm-4">Опис</dt><dd class="col-sm-8">${escapeHtml(t.description)}</dd>
              <dt class="col-sm-4">Час</dt><dd class="col-sm-8">${new Date(t.created_at).toLocaleString()}</dd>
            </dl>
          </div></div>
        </div>
        <div class="col-md-6">
          <div class="card h-100"><div class="card-body">
            <h2 class="h6">Пов’язаний лог</h2>
            ${
              log
                ? `<dl class="row mb-0">
              <dt class="col-sm-4">ID</dt><dd class="col-sm-8">${log.id}</dd>
              <dt class="col-sm-4">IP</dt><dd class="col-sm-8">${escapeHtml(log.ip_address)}</dd>
              <dt class="col-sm-4">Час</dt><dd class="col-sm-8">${new Date(log.timestamp).toLocaleString()}</dd>
              <dt class="col-sm-4">Протокол</dt><dd class="col-sm-8">${escapeHtml(log.protocol)}</dd>
              <dt class="col-sm-4">Порт</dt><dd class="col-sm-8">${log.port}</dd>
              <dt class="col-sm-4">Байти</dt><dd class="col-sm-8">${log.bytes_sent} / ${log.bytes_received}</dd>
              <dt class="col-sm-4">Статус</dt><dd class="col-sm-8">${escapeHtml(log.status)}</dd>
            </dl>`
                : "<p class='text-muted mb-0'>Лог видалено або недоступний.</p>"
            }
          </div></div>
        </div>
      </div>`;
  } catch (e) {
    box.innerHTML = `<div class="alert alert-danger">${escapeHtml(e.message)}</div>`;
  }
}

if (requireAuth()) {
  bindLogout();
  bindUserNav();
  loadIncident();
}
