const DEFAULT_API_URL = "http://localhost:8000/api";

function normalizeApiUrl(value) {
  const raw = (value || "").trim();
  if (!raw) return DEFAULT_API_URL;

  try {
    const url = new URL(raw);
    const host = url.hostname;
    const port = url.port || "";

    if (host === "localhost" || host === "127.0.0.1" || host === "0.0.0.0") {
      if (port === "8080" || port === "8081") {
        url.port = "8000";
      }
    }

    if (url.pathname === "/" || url.pathname === "") {
      url.pathname = "/api";
    } else if (url.pathname.endsWith("/health")) {
      url.pathname = url.pathname.replace(/\/health$/i, "/api");
    } else if (!url.pathname.endsWith("/api")) {
      url.pathname = `${url.pathname.replace(/\/+$/, "")}/api`;
    }

    return url.toString().replace(/\/+$/, "");
  } catch (error) {
    return DEFAULT_API_URL;
  }
}

const API_URL = normalizeApiUrl(
  localStorage.getItem("api_url") ||
  window.API_URL ||
  window.VITE_API_URL ||
  DEFAULT_API_URL
);

const Api = {
  token: () => localStorage.getItem("access_token"),
  refreshToken: () => localStorage.getItem("refresh_token"),

  async request(path, options = {}) {
    const headers = options.headers || {};
    if (Api.token()) headers["Authorization"] = `Bearer ${Api.token()}`;
    if (options.body && !(options.body instanceof FormData)) {
      headers["Content-Type"] = "application/json";
    }
    const response = await fetch(`${API_URL}${path}`, { ...options, headers });
    
    // Handle 401 - try token refresh first
    if (response.status === 401) {
      const refreshed = await Api.tryRefreshToken();
      if (refreshed) {
        // Retry the original request with new token
        headers["Authorization"] = `Bearer ${Api.token()}`;
        const retryResponse = await fetch(`${API_URL}${path}`, { ...options, headers });
        if (!retryResponse.ok) {
          const detail = await retryResponse.json().catch(() => ({}));
          throw new Error(detail.detail || `HTTP ${retryResponse.status}`);
        }
        return retryResponse.status === 204 ? null : retryResponse.json();
      } else {
        // Refresh failed, clear storage and redirect
        localStorage.clear();
        window.location.href = "index.html";
        return;
      }
    }
    
    if (!response.ok) {
      const detail = await response.json().catch(() => ({}));
      throw new Error(detail.detail || `HTTP ${response.status}`);
    }
    return response.status === 204 ? null : response.json();
  },

  async tryRefreshToken() {
    try {
      const refreshToken = Api.refreshToken();
      if (!refreshToken) return false;
      
      const response = await fetch(`${API_URL}/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken })
      });
      
      if (response.ok) {
        const data = await response.json();
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("refresh_token", data.refresh_token);
        return true;
      }
      return false;
    } catch (error) {
      console.error("Token refresh failed:", error);
      return false;
    }
  },

  login: (login, password) =>
    Api.request("/auth/login", { method: "POST", body: JSON.stringify({ login, password }) }),
  register: (payload) =>
    Api.request("/auth/register", { method: "POST", body: JSON.stringify(payload) }),
  stats: () => Api.request("/analysis/stats"),
  results: () => Api.request("/analysis/results?limit=20"),
  threat: (id) => Api.request(`/analysis/results/${id}`),
  runAnalysis: () => Api.request("/analysis/run", { method: "POST" }),
  importLogs: (file) => {
    const form = new FormData();
    form.append("file", file);
    return Api.request("/logs/import", { method: "POST", body: form });
  },
  alerts: (status) => Api.request(`/alerts${status ? `?status=${status}` : ''}`),
  updateAlert: (id, status) => Api.request(`/alerts/${id}`, { method: "PATCH", body: JSON.stringify({ status: status }) }),
  models: () => Api.request("/ml/models"),
  trainModel: (modelName, testSize) => 
    Api.request("/ml/train", { 
      method: "POST", 
      body: JSON.stringify({ model_name: modelName, test_size: testSize }) 
    }),
  activateModel: (id) => Api.request(`/ml/models/${id}/activate`, { method: "POST" }),
  user: () => Api.request("/auth/me"),
  logs: (skip = 0, limit = 100) => Api.request(`/logs?skip=${skip}&limit=${limit}`),
  getLog: (id) => Api.request(`/logs/${id}`),
  addLog: (payload) => Api.request("/logs", { method: "POST", body: JSON.stringify(payload) }),
  deleteLog: (id) => Api.request(`/logs/${id}`, { method: "DELETE" }),
  predict: (logIds) =>
    Api.request("/ml/predict", { method: "POST", body: JSON.stringify({ log_ids: logIds || [] }) }),
};
