const error = document.getElementById("error");
const success = document.getElementById("success");

function showError(message) {
  success.classList.add("d-none");
  error.textContent = message;
  error.classList.remove("d-none");
}

document.getElementById("tabLogin").addEventListener("click", () => {
  document.getElementById("loginForm").classList.remove("d-none");
  document.getElementById("registerForm").classList.add("d-none");
  document.getElementById("tabLogin").classList.add("active");
  document.getElementById("tabRegister").classList.remove("active");
});

document.getElementById("tabRegister").addEventListener("click", () => {
  document.getElementById("registerForm").classList.remove("d-none");
  document.getElementById("loginForm").classList.add("d-none");
  document.getElementById("tabRegister").classList.add("active");
  document.getElementById("tabLogin").classList.remove("active");
});

document.getElementById("loginForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  error.classList.add("d-none");
  try {
    const data = await Api.login(
      document.getElementById("login").value,
      document.getElementById("password").value
    );
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    window.location.href = "dashboard.html";
  } catch (e) {
    showError(e.message);
  }
});

document.getElementById("registerForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  error.classList.add("d-none");
  success.classList.add("d-none");
  try {
    await Api.register({
      login: document.getElementById("regLogin").value,
      email: document.getElementById("regEmail").value,
      password: document.getElementById("regPassword").value,
      role: document.getElementById("regRole").value,
    });
    success.textContent = "Обліковий запис створено. Увійдіть.";
    success.classList.remove("d-none");
    document.getElementById("tabLogin").click();
  } catch (e) {
    showError(e.message);
  }
});

if (localStorage.getItem("access_token")) {
  window.location.href = "dashboard.html";
}
