document.addEventListener("DOMContentLoaded", () => {
    // Main elements
    const addBtn = document.getElementById("addBtn");
    const updateBtn = document.getElementById("updateBtn");
    const form = document.getElementById("add-records-form"); // This is the contacts form
    const updateForm = document.getElementById("updateForm");
    const addAccountBtn = document.getElementById("addAccountBtn");
    const accountFormWrapper = document.getElementById("accountFormsWrapper");
    const accountFormElement = document.getElementById("add-account-form"); // This is the accounts add form

    // CSV Upload elements - only initialize if user is staff
    const dropZone = document.getElementById("drop-zone");
    const fileInput = document.getElementById("file-input");
    const csvUploadBtn = document.getElementById("csv-upload-btn");
    const originalDropZoneContent = dropZone?.innerHTML || '';

    // State variables
    let formVisible = false;
    let updateDropdownVisible = false;
    let accountFormVisible = false;
    let dateUpdateInterval = null;

    // Account Form Toggle
    if (addAccountBtn) {
        addAccountBtn.addEventListener("click", (e) => {
            e.preventDefault();
            accountFormVisible = !accountFormVisible;

            // Toggle account form visibility
            if (accountFormWrapper) {
                accountFormWrapper.style.display = accountFormVisible ? "block" : "none";

                // Close other forms when opening this one
                if (accountFormVisible) {
                    if (form) form.style.display = "none";
                    if (updateForm) updateForm.style.display = "none";
                    formVisible = false;
                    updateDropdownVisible = false;

                    // Update button states
                    if (addBtn) addBtn.classList.remove("selected");
                    if (updateBtn) updateBtn.classList.remove("selected");

                    updateAccountDates();

                    // Ensure drag and drop zone remains accessible (only for admin users)
                    if (window.userIsStaff && dropZone && dropZone.style.display === "none") {
                        dropZone.style.display = "block";
                    }
                }
            }
        });
    }

    // Contact Form Toggle
    if (addBtn && updateBtn && form && updateForm) {
        form.style.display = "none";
        updateForm.style.display = "none";

        addBtn.addEventListener("click", (e) => {
            e.preventDefault();
            formVisible = !formVisible;
            form.style.display = formVisible ? "block" : "none";
            updateForm.style.display = "none";
            updateDropdownVisible = false;

            if (formVisible) {
                addBtn.classList.add("selected");
                updateBtn.classList.remove("selected");
                if (accountFormWrapper) accountFormWrapper.style.display = "none";
                accountFormVisible = false;
                startRealTimeUpdates();

                // Ensure drag and drop zone is accessible (only for admin users)
                if (window.userIsStaff && dropZone && dropZone.style.display === "none") {
                    dropZone.style.display = "block";
                }

                // --- IMPORTANT CHANGE FOR AUTOFILL ---
                // Attach autofill listener ONLY when the contacts form becomes visible
                setupAutofill(); // Call the setup function here
            } else {
                addBtn.classList.remove("selected");
                stopRealTimeUpdates();
            }
        });

        updateBtn.addEventListener("click", (e) => {
            e.preventDefault();
            updateDropdownVisible = !updateDropdownVisible;
            updateForm.style.display = updateDropdownVisible ? "block" : "none";
            form.style.display = "none";
            formVisible = false;

            if (updateDropdownVisible) {
                updateBtn.classList.add("selected");
                addBtn.classList.remove("selected");
                if (accountFormWrapper) accountFormWrapper.style.display = "none";
                accountFormVisible = false;
                stopRealTimeUpdates();

                // Ensure drag and drop zone is accessible (only for admin users)
                if (window.userIsStaff && dropZone && dropZone.style.display === "none") {
                    dropZone.style.display = "block";
                }
            } else {
                updateBtn.classList.remove("selected");
            }
        });
    }

    // Drag and Drop CSV Upload - Only initialize for admin users
    if (window.userIsStaff && dropZone && fileInput && csvUploadBtn) {
        const openFileDialog = () => fileInput?.click();

        dropZone.addEventListener("click", openFileDialog);
        csvUploadBtn.addEventListener("click", openFileDialog);

        fileInput.addEventListener("change", () => {
            if (fileInput.files.length > 0) handleFile(fileInput.files[0]);
        });

        ["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
            dropZone.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ["dragenter", "dragover"].forEach((eventName) => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.add("dragover");
            });
        });

        ["dragleave", "drop"].forEach((eventName) => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.remove("dragover");
            });
        });

        dropZone.addEventListener("drop", (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;

            if (files.length > 0) {
                fileInput.files = files;
                handleFile(files[0]);
            }
        });

        // Ensure drag and drop zone is initially visible for admin users
        dropZone.style.display = "block";
    }

    function handleFile(file) {
        if (!dropZone || !window.userIsStaff) return;

        if (file && file.name.toLowerCase().endsWith(".csv")) {
            dropZone.innerHTML = `
                <div class="file-display">
                    <span class="filename" title="${file.name}">${file.name}</span>
                    <button type="button" class="clear-selection">&times;</button>
                </div>
            `;

            const clearBtn = dropZone.querySelector(".clear-selection");
            if (clearBtn) {
                clearBtn.addEventListener("click", (e) => {
                    e.stopPropagation();
                    clearSelection();
                });
            }
        } else {
            alert("Please upload a valid CSV file.");
            clearSelection();
        }
    }

    function clearSelection() {
        if (!window.userIsStaff) return;
        if (fileInput) fileInput.value = "";
        if (dropZone) dropZone.innerHTML = originalDropZoneContent;
    }

    // Redirect to update page
    window.goToUpdatePage = function () {
        const select = document.getElementById("accountSelect");
        if (select) {
            const contactId = select.value;
            if (contactId) {
                window.location.href = `/update/${contactId}/`;
            }
        }
    };

    // Update dates (Contacts)
    function updateDates() {
        const accountCreatedInput = document.querySelector('input[name="account_created_date"]');
        const lastUpdatedInput = document.querySelector('input[name="last_updated"]');

        const now = new Date();
        const dateOnly = now.toISOString().split("T")[0];
        const pad = (n) => n.toString().padStart(2, "0");
        const datetimeLocal = `${dateOnly}T${pad(now.getHours())}:${pad(now.getMinutes())}`;

        if (accountCreatedInput) accountCreatedInput.value = dateOnly;
        if (lastUpdatedInput) lastUpdatedInput.value = datetimeLocal;
    }

    // Update dates (Accounts)
    function updateAccountDates() {
        const contactsAccountCreatedDateInput = document.getElementById("account_created_date_input");
        const accountsTimestampInput = document.getElementById("account_timestamp");

        const now = new Date();
        const pad = (n) => n.toString().padStart(2, "0");
        const yyyy_mm_dd = now.toISOString().split("T")[0];
        const hh_mm = `${pad(now.getHours())}:${pad(now.getMinutes())}`;
        const datetimeLocal = `${yyyy_mm_dd}T${hh_mm}`;

        if (contactsAccountCreatedDateInput) contactsAccountCreatedDateInput.value = yyyy_mm_dd;
        if (accountsTimestampInput) accountsTimestampInput.value = datetimeLocal;
    }

    function startRealTimeUpdates() {
        updateDates();
        updateAccountDates();
        dateUpdateInterval = setInterval(() => {
            updateDates();
            updateAccountDates();
        }, 1000);
    }

    function stopRealTimeUpdates() {
        if (dateUpdateInterval) {
            clearInterval(dateUpdateInterval);
            dateUpdateInterval = null;
        }
    }

    // Observe Contacts form for display changes
    const contactsAddForm = document.getElementById("add-records-form");
    if (contactsAddForm) {
        contactsAddForm.addEventListener("focusin", updateDates);

        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === "attributes" && mutation.attributeName === "style") {
                    const isVisible = contactsAddForm.style.display !== "none";
                    if (isVisible && !dateUpdateInterval) startRealTimeUpdates();
                    else if (!isVisible && dateUpdateInterval) stopRealTimeUpdates();
                }
            });
        });

        observer.observe(contactsAddForm, {
            attributes: true,
            attributeFilter: ["style"],
        });
    }

    // Observe Accounts form for display changes
    if (accountFormElement) {
        accountFormElement.addEventListener("focusin", updateAccountDates);

        const accountObserver = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === "attributes" && mutation.attributeName === "style") {
                    const isVisible = accountFormElement.style.display !== "none";
                    if (isVisible && dateUpdateInterval) {
                        // The interval is handled by startRealTimeUpdates, which updateDates/updateAccountDates
                        // are called from. Just ensuring it's running when visible.
                    } else if (!isVisible && dateUpdateInterval) {
                        // Consider if you want to stop it *only* if ALL forms are hidden,
                        // or if each form manages its own. For simplicity, the current startRealTimeUpdates
                        // is global.
                    }
                }
            });
        });

        accountObserver.observe(accountFormElement, {
            attributes: true,
            attributeFilter: ["style"],
        });
    }

    // On page unload
    window.addEventListener("beforeunload", stopRealTimeUpdates);
    // Initial call if the contacts form is visible on load
    if (contactsAddForm && contactsAddForm.style.display !== "none") {
        startRealTimeUpdates();
    }
    // Initial call if the accounts form is visible on load
    if (accountFormElement && accountFormElement.style.display !== "none") {
        startRealTimeUpdates();
    }

    // --- AUTOFILL FUNCTIONALITY: Moved into a function to be called when the form becomes visible ---
    function setupAutofill() {
        const accountNameInput = document.getElementById("account_name_input");

        // IMPORTANT: Remove any existing blur listener to prevent duplicates if called multiple times
        // This is good practice if `setupAutofill` could be called more than once for the same input.
        if (accountNameInput) {
            accountNameInput.removeEventListener("blur", handleAutofillBlur);
            accountNameInput.addEventListener("blur", handleAutofillBlur);
        }
    }

    // Define the event handler as a named function for easy removal
    async function handleAutofillBlur() {
        const accountNameInput = document.getElementById("account_name_input"); // Re-get for safety
        if (!accountNameInput) return; // Should not happen if called correctly

        const name = accountNameInput.value.trim();

        if (name.length > 0) {
            try {
                const response = await fetch(`/get-account/?account_name=${encodeURIComponent(name)}`);

                if (!response.ok) {
                    if (response.status === 404) {
                        console.log("Account not found.");
                    } else if (response.status === 400) {
                        console.log("Multiple accounts found or bad request.");
                    } else {
                        console.error(`HTTP error! status: ${response.status}`);
                    }
                    clearAutofillFields();
                    return;
                }

                const data = await response.json();

                if (data.error) {
                    console.log("Backend error:", data.error);
                    clearAutofillFields();
                } else {
                    document.getElementById("website_input").value = data.website || "";
                    document.getElementById("industry_input").value = data.industry || "";
                    document.getElementById("account_id_input").value = data.account_id || "";
                    document.getElementById("account_owner_input").value = data.account_owner || "";
                    document.getElementById("region_input").value = data.region || "";
                    document.getElementById("salesperson_sf_id_input").value = data.salesperson_sf_id || "";
                }
            } catch (error) {
                console.error("Fetch error:", error);
                clearAutofillFields();
            }
        } else {
            clearAutofillFields();
        }
    }

    function clearAutofillFields() {
        document.getElementById("website_input").value = "";
        document.getElementById("industry_input").value = "";
        document.getElementById("account_id_input").value = "";
        document.getElementById("account_owner_input").value = "";
        document.getElementById("region_input").value = "";
        document.getElementById("salesperson_sf_id_input").value = "";
    }
});