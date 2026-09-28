const input = document.getElementById("apiUrl");
input.value = normalizeApiUrl(localStorage.getItem("api_url") || DEFAULT_API_URL);

document.getElementById("saveBtn").addEventListener("click", () => {
  const value = normalizeApiUrl(input.value.trim());
  if (!value) return;
  localStorage.setItem("api_url", value);
  input.value = value;
  document.getElementById("saved").classList.remove("d-none");
});

document.getElementById("resetBtn").addEventListener("click", () => {
  localStorage.removeItem("api_url");
  input.value = DEFAULT_API_URL;
});

async function ping() {
  const status = document.getElementById("health");
  try {
    const apiBase = normalizeApiUrl(localStorage.getItem("api_url") || DEFAULT_API_URL);
    const response = await fetch(`${apiBase.replace(/\/api\/?$/, "")}/health`);
    const data = await response.json();
    status.textContent = `API: ${data.status} (${data.environment})`;
  } catch (e) {
    status.textContent = "API недоступний: " + e.message;
  }
}

if (requireAuth()) {
  bindLogout();
  bindUserNav();
  ping();
}
