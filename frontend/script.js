document.addEventListener("DOMContentLoaded", () => {
  const API_BASE_URL = window.location.origin; // Same origin as frontend

  const keysTableBody = document.getElementById("keys-table-body");
  const modelSelect = document.getElementById("project-model");
  const createKeyModal = document.getElementById("create-key-modal");
  const showKeyModal = document.getElementById("show-key-modal");

  // --- Dynamic Model Loading ---
  const populateModelsDropdown = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/models`);
      const models = await response.json();

      modelSelect.innerHTML =
        '<option value="" disabled selected>Select a model...</option>'; // Reset
      models.forEach((modelName) => {
        const option = document.createElement("option");
        option.value = modelName;
        option.textContent = modelName;
        modelSelect.appendChild(option);
      });
    } catch (error) {
      console.error("Failed to load Ollama models:", error);
      modelSelect.innerHTML =
        '<option value="" disabled selected>Error loading models</option>';
    }
  };

  // --- Key Management ---
  const fetchKeys = async () => {
    const response = await fetch(`${API_BASE_URL}/api/keys`);
    const keys = await response.json();
    keysTableBody.innerHTML = "";
    keys.forEach((key) => {
      const row = document.createElement("tr");
      row.innerHTML = `
                <td>${key.name}</td>
                <td><code>${key.secret_key_display}</code></td>
                <td>${new Date(key.created_at).toLocaleDateString()}</td>
                <td>${key.project_access}</td>
                <td><button class="delete-btn" data-key-id="${
                  key.id
                }" title="Delete key">🗑️</button></td>
            `;
      keysTableBody.appendChild(row);
    });
  };

  const deleteKey = async (keyId) => {
    if (
      !confirm(
        "Are you sure you want to delete this API key? This action cannot be undone."
      )
    ) {
      return;
    }
    try {
      const response = await fetch(`${API_BASE_URL}/api/keys/${keyId}`, {
        method: "DELETE",
      });
      if (response.ok) {
        fetchKeys(); // Refresh the list
      } else {
        alert("Failed to delete the key.");
      }
    } catch (error) {
      console.error("Error deleting key:", error);
    }
  };

  // --- Event Listeners ---
  document
    .getElementById("show-create-modal-btn")
    .addEventListener("click", () => {
      document.getElementById("create-key-form").reset();
      populateModelsDropdown(); // Refresh model list every time modal opens
      createKeyModal.classList.remove("hidden");
    });

  document
    .getElementById("cancel-btn")
    .addEventListener("click", () => createKeyModal.classList.add("hidden"));

  document
    .getElementById("create-key-form")
    .addEventListener("submit", async (e) => {
      e.preventDefault();
      const response = await fetch(`${API_BASE_URL}/api/keys`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: document.getElementById("key-name").value,
          model_name: modelSelect.value,
        }),
      });

      if (response.ok) {
        const newKey = await response.json();
        document.getElementById("generated-key-input").value =
          newKey.secret_key;
        createKeyModal.classList.add("hidden");
        showKeyModal.classList.remove("hidden");
        fetchKeys();
      } else {
        alert("Failed to create key. Make sure a model is selected.");
      }
    });

  document.getElementById("copy-key-btn").addEventListener("click", (e) => {
    const input = document.getElementById("generated-key-input");
    input.select();
    navigator.clipboard.writeText(input.value);
    e.target.textContent = "Copied!";
    setTimeout(() => {
      e.target.textContent = "Copy";
    }, 2000);
  });

  document
    .getElementById("done-btn")
    .addEventListener("click", () => showKeyModal.classList.add("hidden"));

  keysTableBody.addEventListener("click", (e) => {
    if (e.target.classList.contains("delete-btn")) {
      const keyId = e.target.getAttribute("data-key-id");
      deleteKey(keyId);
    }
  });

  // Initial Load
  fetchKeys();
});
