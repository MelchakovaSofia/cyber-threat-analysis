const CARDS = [
  ["analyzed_events", "Проаналізовано подій"],
  ["detected_threats", "Виявлено загроз"],
  ["open_alerts", "Відкриті попередження"],
  ["risk_level", "Рівень ризику"],
];

const charts = {};

function renderBar(id, labels, values, label) {
  const ctx = document.getElementById(id);
  if (!ctx) return;
  if (charts[id]) charts[id].destroy();
  charts[id] = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [{ label, data: values, backgroundColor: "#3d7ea6" }],
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true } },
    },
  });
}

async function loadStats() {
  const stats = await Api.stats();
  document.getElementById("stats").innerHTML = CARDS.map(
    ([key, label]) => `
      <div class="col-6 col-lg-3">
        <div class="card h-100"><div class="card-body">
          <div class="text-muted small">${label}</div>
          <div class="stat-value">${stats[key]}</div>
        </div></div>
      </div>`
  ).join("");

  const hours = [...Array(24).keys()];
  const byHour = Object.fromEntries(
    (stats.activity_by_hour || []).map((item) => [Number(item.hour), item.count])
  );
  renderBar(
    "activityChart",
    hours.map((h) => `${h}:00`),
    hours.map((h) => byHour[h] || 0),
    "Події"
  );

  const types = stats.threats_by_type || [];
  renderBar(
    "typeChart",
    types.map((item) => item.threat_type),
    types.map((item) => item.count),
    "Загрози"
  );

  const ips = stats.top_ips || [];
  renderBar(
    "ipChart",
    ips.map((item) => item.ip_address),
    ips.map((item) => item.count),
    "Запити"
  );
}

async function loadThreats() {
  const threats = await Api.results();
  document.getElementById("threats").innerHTML = threats.length
    ? threats
        .map(
          (t) => `<tr>
        <td>${t.id}</td><td>${t.log_id}</td><td>${escapeHtml(t.threat_type)}</td>
        <td>${t.probability.toFixed(4)}</td><td><span class="badge bg-${getSeverityClass(t.severity)}">${escapeHtml(t.severity)}</span></td>
        <td>${new Date(t.created_at).toLocaleString()}</td>
        <td><button class="btn btn-sm btn-outline-primary" onclick="viewThreatDetails(${t.id})">Деталі</button></td>
      </tr>`
        )
        .join("")
    : '<tr><td colspan="7" class="text-center">Загроз не знайдено</td></tr>';
}

function getSeverityClass(severity) {
  const classes = { critical: "danger", high: "warning", medium: "info", low: "secondary" };
  return classes[severity] || "secondary";
}

function viewThreatDetails(threatId) {
  localStorage.setItem("current_threat_id", threatId);
  window.location.href = `incident-details.html?id=${threatId}`;
}

document.getElementById("uploadBtn").addEventListener("click", async () => {
  const status = document.getElementById("importStatus");
  const file = document.getElementById("logFile").files[0];
  if (!file) return (status.textContent = "Оберіть файл");
  try {
    status.textContent = "Завантаження...";
    const result = await Api.importLogs(file);
    status.textContent = `Імпортовано записів: ${result.imported}`;
    status.className = "small text-success mt-2";
    await loadStats();
  } catch (e) {
    status.textContent = e.message;
    status.className = "small text-danger mt-2";
  }
});

document.getElementById("analyzeBtn").addEventListener("click", async () => {
  const status = document.getElementById("importStatus");
  try {
    status.textContent = "Аналіз...";
    const result = await Api.runAnalysis();
    status.textContent = `Проаналізовано: ${result.analysed}, загроз: ${result.threats}`;
    status.className = "small text-success mt-2";
    await Promise.all([loadStats(), loadThreats()]);
  } catch (e) {
    status.textContent = e.message;
    status.className = "small text-danger mt-2";
  }
});

if (requireAuth()) {
  bindLogout();
  bindUserNav();
  loadStats().catch((e) => console.error(e));
  loadThreats().catch((e) => console.error(e));
}
