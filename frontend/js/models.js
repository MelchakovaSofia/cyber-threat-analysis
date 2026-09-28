let currentUserRole = null;

async function loadUserInfo() {
  try {
    const user = await Api.user();
    currentUserRole = user.role;
    document.getElementById("userInfo").textContent = `${user.login} (${user.role})`;
    
    // Only admins can train models
    if (user.role !== 'admin') {
      document.getElementById('trainBtn').disabled = true;
      document.getElementById('trainBtn').title = 'Тільки адміністратори можуть навчати моделі';
    }
  } catch (e) {
    console.error("Failed to load user info:", e);
  }
}

async function loadModels() {
  try {
    const models = await Api.models();
    const tbody = document.getElementById("modelsTable");
    
    if (models.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7" class="text-center">Моделей не знайдено</td></tr>';
      return;
    }
    
    tbody.innerHTML = models.map(model => `
      <tr class="${model.is_active ? 'table-success' : ''}">
        <td>${model.id}</td>
        <td>${model.model_name}</td>
        <td>${model.version}</td>
        <td>${model.accuracy > 0 ? (model.accuracy * 100).toFixed(2) + '%' : 'N/A'}</td>
        <td>
          ${model.is_active ? 
            '<span class="badge bg-success">Активна</span>' : 
            '<span class="badge bg-secondary">Неактивна</span>'}
        </td>
        <td>${new Date(model.created_at).toLocaleString()}</td>
        <td>
          <div class="btn-group btn-group-sm">
            ${!model.is_active && currentUserRole === 'admin' ? 
              `<button class="btn btn-outline-success" onclick="activateModel(${model.id})">Активувати</button>` : 
              ''}
          </div>
        </td>
      </tr>
    `).join('');
  } catch (e) {
    console.error("Failed to load models:", e);
    document.getElementById("modelsTable").innerHTML = '<tr><td colspan="7" class="text-center text-danger">Помилка завантаження</td></tr>';
  }
}

async function activateModel(modelId) {
  if (!confirm('Ви впевнені, що хочете активувати цю модель?')) return;
  
  try {
    await Api.activateModel(modelId);
    loadModels();
  } catch (e) {
    console.error("Failed to activate model:", e);
    alert('Не вдалося активувати модель: ' + e.message);
  }
}

document.getElementById("startTraining").addEventListener("click", async () => {
  const modelName = document.getElementById("modelName").value;
  const testSize = parseFloat(document.getElementById("testSize").value);
  
  try {
    const btn = document.getElementById("startTraining");
    btn.disabled = true;
    btn.textContent = "Навчання...";
    
    const result = await Api.trainModel(modelName, testSize);
    
    // Close modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('trainModal'));
    modal.hide();
    
    // Show results
    alert(`Модель успішно навчена!\nТочність: ${(result.accuracy * 100).toFixed(2)}%\nPrecision: ${(result.precision * 100).toFixed(2)}%\nRecall: ${(result.recall * 100).toFixed(2)}%\nF1: ${(result.f1 * 100).toFixed(2)}%`);
    
    // Reload models
    loadModels();
  } catch (e) {
    console.error("Training failed:", e);
    alert('Помилка навчання: ' + e.message);
  } finally {
    const btn = document.getElementById("startTraining");
    btn.disabled = false;
    btn.textContent = "Почати навчання";
  }
});

if (requireAuth()) {
  bindLogout();
  bindUserNav().then((user) => {
    if (user) {
      currentUserRole = user.role;
      if (user.role !== "admin") {
        document.getElementById("trainBtn").disabled = true;
        document.getElementById("trainBtn").title = "Тільки адміністратори можуть навчати моделі";
      }
    }
    loadModels();
  });
}