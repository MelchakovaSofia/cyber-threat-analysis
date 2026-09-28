let skip = 0;
const LIMIT = 50;

async function loadLogs() {
  const tbody = document.getElementById("logsTable");
  try {
    const logs = await Api.logs(skip, LIMIT);
    if (!logs.length) {
      tbody.innerHTML = '<tr><td colspan="9" class="text-center">Записів не знайдено</td></tr>';
      return;
    }
    tbody.innerHTML = logs
      .map(
        (log) => `<tr>
        <td>${log.id}</td>
        <td>${escapeHtml(log.ip_address)}</td>
        <td>${new Date(log.timestamp).toLocaleString()}</td>
        <td>${escapeHtml(log.protocol)}</td>
        <td>${log.port}</td>
        <td>${log.bytes_sent}</td>
        <td>${log.bytes_received}</td>
        <td>${escapeHtml(log.status)}</td>
        <td>
          <button class="btn btn-sm btn-outline-danger" onclick="deleteLog(${log.id})">Видалити</button>
        </td>
      </tr>`
      )
      .join("");
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="9" class="text-center text-danger">${escapeHtml(e.message)}</td></tr>`;
  }
}

async function deleteLog(id) {
  if (!confirm(`Видалити запис #${id}?`)) return;
  try {
    await Api.deleteLog(id);
    await loadLogs();
  } catch (e) {
    alert(e.message);
  }
}

document.getElementById("prevBtn").addEventListener("click", async () => {
  skip = Math.max(0, skip - LIMIT);
  await loadLogs();
});
document.getElementById("nextBtn").addEventListener("click", async () => {
  skip += LIMIT;
  await loadLogs();
});

document.getElementById("uploadBtn").addEventListener("click", async () => {
  const status = document.getElementById("importStatus");
  const file = document.getElementById("logFile").files[0];
  if (!file) return (status.textContent = "Оберіть файл CSV або JSON");
  try {
    status.textContent = "Завантаження...";
    const result = await Api.importLogs(file);
    status.textContent = `Імпортовано записів: ${result.imported}`;
    skip = 0;
    await loadLogs();
  } catch (e) {
    status.textContent = e.message;
  }
});

if (requireAuth()) {
  bindLogout();
  bindUserNav();
  loadLogs();
}
