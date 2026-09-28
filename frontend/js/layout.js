function requireAuth() {
  if (!localStorage.getItem("access_token")) {
    window.location.href = "index.html";
    return false;
  }
  return true;
}

async function bindUserNav() {
  const el = document.getElementById("userInfo");
  if (!el) return null;
  try {
    const user = await Api.user();
    el.textContent = `${user.login} (${user.role})`;
    return user;
  } catch (e) {
    console.error("Failed to load user info:", e);
    return null;
  }
}

function bindLogout() {
  const btn = document.getElementById("logoutBtn");
  if (!btn) return;
  btn.addEventListener("click", () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    window.location.href = "index.html";
  });
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}
