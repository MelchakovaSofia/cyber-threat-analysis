async function loadProfile() {
  const user = await Api.user();
  document.getElementById("login").textContent = user.login;
  document.getElementById("email").textContent = user.email;
  document.getElementById("role").textContent = user.role;
  document.getElementById("created").textContent = new Date(user.created_at).toLocaleString();
}

if (requireAuth()) {
  bindLogout();
  bindUserNav();
  loadProfile().catch((e) => {
    document.getElementById("profileError").textContent = e.message;
  });
}
