document.addEventListener("DOMContentLoaded", () => {
  // --- Form toggle: Add / Update ---
  const addBtn = document.getElementById("addBtn");
  const updateBtn = document.getElementById("updateBtn");
  const form = document.getElementById("add-records-form");

  let formVisible = false;

  if (addBtn && updateBtn && form) {
    form.style.display = "none";

    addBtn.addEventListener("click", () => {
      formVisible = !formVisible;
      form.style.display = formVisible ? "block" : "none";
      if (formVisible) {
        addBtn.classList.add("selected");
        updateBtn.classList.remove("selected");
        startRealTimeUpdates();  // 👉 Start real-time updates when form is shown
      } else {
        addBtn.classList.remove("selected");
        stopRealTimeUpdates();   // 👉 Stop updates when form is hidden
      }
    });

    updateBtn.addEventListener("click", () => {
      formVisible = false;
      form.style.display = "none";
      updateBtn.classList.add("selected");
      addBtn.classList.remove("selected");
      stopRealTimeUpdates();     // 👉 Stop updates when switching to update mode
    });
  }

  // --- Drag and Drop CSV Upload ---
  const dropZone = document.getElementById("drop-zone");
  const fileInput = document.getElementById("file-input");
  const csvUploadBtn = document.getElementById("csv-upload-btn");
  const originalDropZoneContent = dropZone.innerHTML;

  const openFileDialog = () => {
    fileInput.click();
  };

  dropZone.addEventListener("click", openFileDialog);
  csvUploadBtn.addEventListener("click", openFileDialog);

  fileInput.addEventListener("change", (e) => {
    if (fileInput.files.length > 0) {
      handleFile(fileInput.files[0]);
    }
  });

  ["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
    dropZone.addEventListener(eventName, preventDefaults, false);
    document.body.addEventListener(eventName, preventDefaults, false);
  });

  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  ["dragenter", "dragover"].forEach((eventName) => {
    dropZone.addEventListener(
      eventName,
      () => {
        dropZone.classList.add("dragover");
      },
      false
    );
  });

  ["dragleave", "drop"].forEach((eventName) => {
    dropZone.addEventListener(
      eventName,
      () => {
        dropZone.classList.remove("dragover");
      },
      false
    );
  });

  dropZone.addEventListener(
    "drop",
    (e) => {
      const dt = e.dataTransfer;
      const files = dt.files;

      if (files.length > 0) {
        fileInput.files = files;
        handleFile(files[0]);
      }
    },
    false
  );

  function handleFile(file) {
    if (file && file.name.toLowerCase().endsWith(".csv")) {
      dropZone.innerHTML = `
        <div class="file-display">
          <span class="filename" title="${file.name}">${file.name}</span>
          <button type="button" class="clear-selection">&times;</button>
        </div>
      `;

      dropZone
        .querySelector(".clear-selection")
        .addEventListener("click", (e) => {
          e.stopPropagation();
          clearSelection();
        });
    } else {
      alert("Please upload a valid CSV file.");
      clearSelection();
    }
  }

  function clearSelection() {
    fileInput.value = "";
    dropZone.innerHTML = originalDropZoneContent;
  }

  // --- Update Form Dropdown Show ---
  window.showUpdateDropdown = function () {
    document.getElementById("updateForm").style.display = "block";
  };

  // --- Update Redirect ---
  window.goToUpdatePage = function () {
    const select = document.getElementById("accountSelect");
    const contactId = select.value;
    if (contactId) {
      window.location.href = `/setup/update/${contactId}/`;
    }
  };

  // --- REAL-TIME DATE AND TIMESTAMP FUNCTIONALITY ---
  let dateUpdateInterval = null;

  // Update dates immediately
  function updateDates() {
    const accountCreatedInput = document.querySelector(
      'input[name="account_created_date"]'
    );
    const lastUpdatedInput = document.querySelector(
      'input[name="last_updated"]'
    );

    const now = new Date();

    // Format: YYYY-MM-DD
    const dateOnly = now.toISOString().split("T")[0];

    // Format: YYYY-MM-DDTHH:MM
    const pad = (n) => n.toString().padStart(2, "0");
    const datetimeLocal = `${dateOnly}T${pad(now.getHours())}:${pad(
      now.getMinutes()
    )}`;

    if (accountCreatedInput) {
      accountCreatedInput.value = dateOnly;
    }

    if (lastUpdatedInput) {
      lastUpdatedInput.value = datetimeLocal;
    }
  }

  // Start real-time updates (update every second for timestamp)
  function startRealTimeUpdates() {
    // Update immediately
    updateDates();
    
    // Then update every second
    dateUpdateInterval = setInterval(updateDates, 1000);
  }

  // Stop real-time updates
  function stopRealTimeUpdates() {
    if (dateUpdateInterval) {
      clearInterval(dateUpdateInterval);
      dateUpdateInterval = null;
    }
  }

  // Legacy function for backward compatibility
  function autoFillDates() {
    updateDates();
  }

  // Initialize dates if form is visible on page load
  if (formVisible) {
    startRealTimeUpdates();
  }

  // Update dates immediately when page loads (in case form is already visible)
  updateDates();

  // Optional: Also update dates when the form becomes visible or when user focuses on the form
  const formElement = document.getElementById("add-records-form");
  if (formElement) {
    // Update dates when any input in the form gets focus
    formElement.addEventListener('focusin', updateDates);
    
    // Update dates when form becomes visible (using MutationObserver)
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
          const isVisible = formElement.style.display !== 'none';
          if (isVisible && !dateUpdateInterval) {
            startRealTimeUpdates();
          } else if (!isVisible && dateUpdateInterval) {
            stopRealTimeUpdates();
          }
        }
      });
    });
    
    observer.observe(formElement, {
      attributes: true,
      attributeFilter: ['style']
    });
  }

  // Clean up on page unload
  window.addEventListener('beforeunload', stopRealTimeUpdates);
});