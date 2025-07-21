// Enhanced email validation
function isValidEmail(email) {
    const re = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return re.test(String(email).toLowerCase());
}
// Helper function to set dropdown values properly
function setDropdownValue(selectElement, value) {
    if (!selectElement || !value) return;
    
    // Try exact match first
    for (let i = 0; i < selectElement.options.length; i++) {
        if (selectElement.options[i].value === value) {
            selectElement.selectedIndex = i;
            return;
        }
    }
    
    // Try case-insensitive match
    const lowerValue = value.toLowerCase();
    for (let i = 0; i < selectElement.options.length; i++) {
        if (selectElement.options[i].value.toLowerCase() === lowerValue) {
            selectElement.selectedIndex = i;
            return;
        }
    }
    
    // If no match found, set the value directly (may not work for all browsers)
    selectElement.value = value;
}
// Phone validation
function isValidPhone(phone) {
  const phoneRegex = /^\+?[1-9]\d{7,14}$/;
  return phoneRegex.test(phone);
}

// Date formatting
function formatIndianDateTime(date) {
    const options = {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true,
        timeZone: 'Asia/Kolkata'
    };
    
    let formatted = date.toLocaleString('en-IN', options);
    formatted = formatted.replace('AM', 'a.m.').replace('PM', 'p.m.');
    return formatted;
}

// Toast notification system
function showToast(message, type = 'success') {
    const maxToasts = 3;
    const containerId = 'toast-container';

    let container = document.getElementById(containerId);
    if (!container) {
        container = document.createElement('div');
        container.id = containerId;
        container.style.position = 'fixed';
        container.style.top = '20px';
        container.style.right = '20px';
        container.style.zIndex = '9999';
        container.style.display = 'flex';
        container.style.flexDirection = 'column';
        container.style.gap = '10px';
        document.body.appendChild(container);
    }

    while (container.children.length >= maxToasts) {
        container.removeChild(container.firstChild);
    }

    const toast = document.createElement('div');
    toast.className = `message-toast ${type} visible`;
    toast.style.background = type === 'error' ? '#f44336' : (type === 'warning' ? '#ff9800' : '#4CAF50');
    toast.style.color = 'white';
    toast.style.padding = '12px 18px';
    toast.style.borderRadius = '6px';
    toast.style.boxShadow = '0 2px 8px rgba(0,0,0,0.15)';
    toast.style.transition = 'opacity 0.3s ease';
    toast.innerHTML = `
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <span style="flex: 1;">${message}</span>
            <button class="toast-close" style="margin-left: 12px; background: transparent; border: none; color: white; font-size: 16px; cursor: pointer;">&times;</button>
        </div>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 5000);

    toast.querySelector('.toast-close').addEventListener('click', () => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    });

    return toast;
}

window.showToast = showToast;

// Main DOMContentLoaded handler
document.addEventListener("DOMContentLoaded", () => {
    // Element references
    const unifiedAddBtn = document.getElementById("unifiedAddBtn");
    const unifiedUpdateBtn = document.getElementById("unifiedUpdateBtn");
    const unifiedAddForm = document.getElementById("unified-add-form");
    const unifiedUpdateForm = document.getElementById("unified-update-form");
    const unifiedSearchInput = document.getElementById("unified_search");
    const unifiedDropdown = document.getElementById("unified_dropdown");
    const emailInput = document.getElementById("unified_email");
    const phoneInput = document.getElementById("unified_mobile");
    // Inside DOMContentLoaded — near other DOM declarations
const mobileInput = document.getElementById("unified_mobile");
const altInput = document.getElementById("unified_altphone");

// Initialize intl-tel-input
const itiMobile = window.intlTelInput(mobileInput, {
    initialCountry: "auto",
    geoIpLookup: callback => {
        fetch("https://ipapi.co/json")
            .then(res => res.json())
            .then(data => callback(data.country_code))
            .catch(() => callback("us"));
    },
    utilsScript: "https://cdn.jsdelivr.net/npm/intl-tel-input@18.1.1/build/js/utils.js"
});

const itiAlt = window.intlTelInput(altInput, {
    initialCountry: "auto",
    geoIpLookup: callback => {
        fetch("https://ipapi.co/json")
            .then(res => res.json())
            .then(data => callback(data.country_code))
            .catch(() => callback("us"));
    },
    utilsScript: "https://cdn.jsdelivr.net/npm/intl-tel-input@18.1.1/build/js/utils.js"
});

    const dropZone = document.getElementById("drop-zone");
    const fileInput = document.getElementById("file-input");
    const csvUploadBtn = document.getElementById("csv-upload-btn");
    const originalDropZoneContent = dropZone?.innerHTML || '';

    let dateUpdateInterval = null;

    // Form submission with validation
    if (unifiedAddForm) {
        unifiedAddForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            
            const email = emailInput ? emailInput.value.trim() : '';
            const phone = phoneInput ? phoneInput.value.trim() : '';

            // Validate at least one contact method
            if (!email && !phone) {
                showToast("Please enter either an email address or phone number", "error");
                if (emailInput) emailInput.focus();
                return false;
            }

            // Validate email if provided
            if (email && !isValidEmail(email)) {
                showToast("Please enter a valid email address", "error");
                if (emailInput) emailInput.focus();
                return false;
            }

            // Validate phone if provided
            if (phone && !isValidPhone(phone)) {
                showToast("Please enter a valid phone number (at least 8 digits)", "error");
                if (phoneInput) phoneInput.focus();
                return false;
            }
            // ✅ Convert to full intl format
if (itiMobile.isValidNumber()) phoneInput.value = itiMobile.getNumber();
if (itiAlt.isValidNumber()) altInput.value = itiAlt.getNumber();

        
            // Submit form if validation passes
            try {
                const response = await fetch(unifiedAddForm.action, {
                    method: 'POST',
                    body: new FormData(unifiedAddForm),
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                });
                
                const result = await response.json();
                showToast(result.message, result.status);
                
                if (result.status === 'success') {
                    unifiedAddForm.reset();
                    updateDates(); // Reset timestamps
                }
            } catch (error) {
                console.error('Error:', error);
                showToast("Error submitting form", "error");
            }
        });
    }

    

    // Real-time validation feedback
    if (emailInput) {
        emailInput.addEventListener('blur', () => {
            const email = emailInput.value.trim();
            if (email && !isValidEmail(email)) {
                emailInput.classList.add('invalid-field');
            } else {
                emailInput.classList.remove('invalid-field');
            }
        });

        emailInput.addEventListener('input', () => {
            const email = emailInput.value.trim();
            if (email && isValidEmail(email)) {
                emailInput.classList.remove('invalid-field');
            }
        });
    }

    if (phoneInput) {
        phoneInput.addEventListener('blur', () => {
            const phone = phoneInput.value.trim();
            if (phone && !isValidPhone(phone)) {
                phoneInput.classList.add('invalid-field');
            } else {
                phoneInput.classList.remove('invalid-field');
            }
        });

        phoneInput.addEventListener('input', () => {
            const phone = phoneInput.value.trim();
            if (phone && isValidPhone(phone)) {
                phoneInput.classList.remove('invalid-field');
            }
        });
    }

    // Form toggling
    if (unifiedAddBtn) {
        unifiedAddBtn.addEventListener("click", (e) => {
            e.preventDefault();
            const isCurrentlyVisible = !unifiedAddForm.classList.contains("hidden-form");
            closeAllForms();

            if (!isCurrentlyVisible) {
                unifiedAddForm.classList.remove("hidden-form");
                unifiedAddBtn.classList.add("selected");
                startRealTimeUpdates();
                setupUnifiedAutofill();
                enableUnifiedAutocomplete();
            }
        });
    }

    if (unifiedUpdateBtn) {
    unifiedUpdateBtn.addEventListener("click", (e) => {
        e.preventDefault();
        const updateSection = document.getElementById("unified-update-section");
        const isCurrentlyVisible = !updateSection.classList.contains("hidden-form");

        if (isCurrentlyVisible) {
            updateSection.classList.add("hidden-form");
            unifiedUpdateBtn.classList.remove("selected");
        } else {
            closeAllForms();
            updateSection.classList.remove("hidden-form");
            unifiedUpdateBtn.classList.add("selected");
            stopRealTimeUpdates();
        }
    });
}


    function closeAllForms() {
        if (unifiedAddForm) unifiedAddForm.classList.add("hidden-form");
        if (unifiedUpdateForm) unifiedUpdateForm.classList.add("hidden-form");
        
        if (unifiedAddBtn) unifiedAddBtn.classList.remove("selected");
        if (unifiedUpdateBtn) unifiedUpdateBtn.classList.remove("selected");
        
        stopRealTimeUpdates();
    }

    // Search functionality
    if (unifiedSearchInput && unifiedDropdown) {
        unifiedSearchInput.addEventListener("input", async () => {
            const query = unifiedSearchInput.value.trim();
            if (query.length < 2) {
                unifiedDropdown.innerHTML = "";
                unifiedDropdown.style.display = "none";
                return;
            }

            try {
                const [contactsRes, accountsRes] = await Promise.all([
                    fetch(`/api/search-contacts/?q=${encodeURIComponent(query)}`),
                    fetch(`/api/search-accounts/?q=${encodeURIComponent(query)}`)
                ]);

                const contacts = await contactsRes.json();
                const accounts = await accountsRes.json();

                unifiedDropdown.innerHTML = "";

                contacts.results.forEach(contact => {
                    const option = document.createElement("div");
                    option.className = "autocomplete-option";
                    const fullName = contact.full_name || `${contact.first_name || ""} ${contact.last_name || ""}`.trim();
                    option.textContent = `${contact.account_name} - ${fullName}`;
                    option.dataset.type = "contact";
                    option.dataset.id = contact.id;
                    unifiedDropdown.appendChild(option);
                });

                // Deduplicate by account_name
const seenAccountNames = new Set();

accounts.results.forEach(account => {
    const name = account.account_name?.trim();
    if (!name || seenAccountNames.has(name.toLowerCase())) return;

    seenAccountNames.add(name.toLowerCase());

    const option = document.createElement("div");
    option.className = "autocomplete-option";
    option.textContent = `${name} - -`;
    option.dataset.type = "account";
    option.dataset.id = account.id;
    unifiedDropdown.appendChild(option);
});


                unifiedDropdown.style.display = unifiedDropdown.children.length > 0 ? "block" : "none";
            } catch (error) {
                console.error("Search error:", error);
            }
        });

        unifiedDropdown.addEventListener("click", (e) => {
            const option = e.target.closest(".autocomplete-option");
            if (!option) return;

            const recordType = option.dataset.type;
            const recordId = option.dataset.id;

            if (recordType === "contact") {
                window.location.href = `/update/${recordId}/?source=contacts`;
            } else if (recordType === "account") {
                window.location.href = `/update-record/${recordId}/?source=accounts`;
            }
        });

        document.addEventListener("click", (e) => {
            if (!unifiedSearchInput.contains(e.target) && !unifiedDropdown.contains(e.target)) {
                unifiedDropdown.style.display = "none";
            }
        });
    }

    // CSV Upload Handling
    const openFileDialog = () => fileInput?.click();

    if (dropZone) dropZone.addEventListener("click", openFileDialog);
    if (csvUploadBtn) csvUploadBtn.addEventListener("click", openFileDialog);

    if (fileInput) {
        fileInput.addEventListener("change", () => {
            if (fileInput.files.length > 0) handleFile(fileInput.files[0]);
        });
    }

    if (dropZone) {
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
    }

    function handleFile(file) {
        if (!dropZone) return;

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
            showToast("Please upload a valid CSV file", "error");
            clearSelection();
        }
    }

    function clearSelection() {
        if (fileInput) fileInput.value = "";
        if (dropZone) dropZone.innerHTML = originalDropZoneContent;
    }

    // Date handling
    function updateDates() {
        const createdDateInput = document.getElementById('unified_created_date');
        const timestampInput = document.getElementById('unified_created_date_iso');

        const now = new Date();
        
        if (createdDateInput) {
            createdDateInput.value = formatIndianDateTime(now);
        }
        
        if (timestampInput) {
            timestampInput.value = now.toISOString();
        }
    }

    function startRealTimeUpdates() {
        if (unifiedAddForm && !unifiedAddForm.classList.contains("hidden-form")) {
            updateDates();
            if (!dateUpdateInterval) {
                dateUpdateInterval = setInterval(updateDates, 1000);
            }
        }
    }

    function stopRealTimeUpdates() {
        if (dateUpdateInterval) {
            clearInterval(dateUpdateInterval);
            dateUpdateInterval = null;
        }
    }

    async function handleUnifiedAutofillBlur() {
    const accountNameInput = document.getElementById("unified_account_name");
    if (!accountNameInput) return;

    const name = accountNameInput.value.trim();
    if (name.length === 0) {
        clearUnifiedAutofillFields();
        return;
    }

    try {
        const response = await fetch(`/api/get-account/?account_name=${encodeURIComponent(name)}`);
        if (!response.ok) {
            clearUnifiedAutofillFields();
            return;
        }

        const result = await response.json();
        const data = result.data;
        console.log("Autofilled from API:", data); // Debug log

        if (data.error) {
            clearUnifiedAutofillFields();
        } else {
            const regionInput = document.getElementById("unified_region");
            const zoneInput = document.getElementById("unified_zone");
            const ownerInput = document.getElementById("unified_owner");
            const industryInput = document.getElementById("unified_industry");
            
            // Use the helper function to set dropdown values
            setDropdownValue(regionInput, data.region);
            setDropdownValue(zoneInput, data.zone);
            setDropdownValue(ownerInput, data.account_owner);
            setDropdownValue(industryInput, data.industry);
        }
    } catch (error) {
        console.error("Fetch error for Account Autofill:", error);
        clearUnifiedAutofillFields();
    }
}
    // Autofill functionality
    function setupUnifiedAutofill() {
        const accountNameInput = document.getElementById("unified_account_name");
        if (accountNameInput) {
            accountNameInput.removeEventListener("blur", handleUnifiedAutofillBlur);
            accountNameInput.addEventListener("blur", handleUnifiedAutofillBlur);
        }
    }

    
    function clearUnifiedAutofillFields() {
        const fieldsToClean = [
            "unified_account_id", "unified_phone", "unified_industry",
            "unified_website", "unified_owner", "unified_zone"
        ];

        fieldsToClean.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) field.value = "";
        });

        const regionInput = document.getElementById("unified_region");
        if (regionInput) regionInput.value = "";
    }

    // Autocomplete functionality
    function enableUnifiedAutocomplete() {
        const input = document.getElementById("unified_account_name");
        if (!input) return;

        const suggestionBox = createSuggestionBox(input);

        input.addEventListener("input", async () => {
            const query = input.value.trim();
            if (query.length < 1) {
                suggestionBox.innerHTML = "";
                suggestionBox.style.display = "none";
                return;
            }

            try {
                const response = await fetch(`/api/autocomplete-accounts/?q=${encodeURIComponent(query)}`);
                const suggestions = await response.json();

                suggestionBox.innerHTML = "";

                suggestions.forEach(s => {
                    const div = document.createElement("div");
                    div.className = "autocomplete-suggestion";
                    div.textContent = s.text;
                    div.dataset.region = s.region || "";
                    div.dataset.zone = s.zone || "";
                    div.dataset.owner = s.account_owner || "";
                    div.dataset.industry = s.industry || "";
                    
                    div.addEventListener("click", () => {
    input.value = s.text;

    const regionInput = document.getElementById("unified_region");
    const zoneInput = document.getElementById("unified_zone");
    const industryInput = document.getElementById("unified_industry");
    const ownerInput = document.getElementById("unified_owner");

    setDropdownValue(regionInput, div.dataset.region);
    setDropdownValue(zoneInput, div.dataset.zone);
    setDropdownValue(ownerInput, div.dataset.owner);
    setDropdownValue(industryInput, div.dataset.industry);

    suggestionBox.innerHTML = "";
    suggestionBox.style.display = "none";

    // ✅ Explicitly call autofill to trigger backend fetch and fill
    handleUnifiedAutofillBlur();
});

                    suggestionBox.appendChild(div);
                });

                suggestionBox.style.display = suggestions.length > 0 ? "block" : "none";
            } catch (error) {
                console.error("Autocomplete error:", error);
            }
        });

        document.addEventListener("click", (e) => {
            if (!suggestionBox.contains(e.target) && e.target !== input) {
                suggestionBox.innerHTML = "";
                suggestionBox.style.display = "none";
            }
        });
    }

    function createSuggestionBox(inputEl) {
        let box = inputEl.nextElementSibling;
        if (box && box.classList.contains("autocomplete-box")) return box;

        box = document.createElement("div");
        box.className = "autocomplete-box";
        box.style.position = "absolute";
        box.style.zIndex = "999";
        box.style.background = "white";
        box.style.border = "1px solid #ccc";
        box.style.width = inputEl.offsetWidth + "px";
        box.style.maxHeight = "200px";
        box.style.overflowY = "auto";
        box.style.boxShadow = "0 4px 6px rgba(0,0,0,0.1)";
        box.style.display = "none";
        box.style.cursor = "pointer";

        inputEl.parentElement.appendChild(box);
        return box;
    }

    // Initialize
    closeAllForms();
    if (dropZone) {
        dropZone.style.display = "block";
    }

    // Set initial timestamp
    updateDates();
    // Set initial timestamp


// Show a toast on initial load
showToast("Welcome! Ready to get started.", "success");

// Stop timestamp update when leaving
window.addEventListener("beforeunload", stopRealTimeUpdates);

});
// GeoNames API configuration
const GEONAMES_USERNAME = 'ananyarohatgi'; // Your username
const GEONAMES_ENDPOINT = 'https://secure.geonames.org'; // Using HTTPS

// Initialize Select2 for both mailing and contact location dropdowns
function initializeLocationDropdowns() {
    // Initialize mailing address dropdowns (your existing code)
    initializeMailingDropdowns();
    
    // Initialize contact location dropdowns
    initializeContactDropdowns();
}
// Initialize Select2 for both mailing and contact location dropdowns
function initializeLocationDropdowns() {
    // Initialize mailing address dropdowns
    initializeMailingDropdowns();
    
    // Initialize contact location dropdowns
    initializeContactDropdowns();
}

function initializeMailingDropdowns() {
    // Country dropdown - now stores and displays full country name
    $('#unified_mailing_country').select2({
        placeholder: 'Select Country',
        allowClear: true,
        ajax: {
            url: `${GEONAMES_ENDPOINT}/countryInfoJSON`,
            dataType: 'json',
            delay: 250,
            data: function(params) {
                return {
                    q: params.term,
                    username: GEONAMES_USERNAME,
                    style: 'full'
                };
            },
            processResults: function(data, params) {
                try {
                    if (!data || !data.geonames) {
                        console.error('Invalid GeoNames country data:', data);
                        return { results: [] };
                    }
                    
                    const countries = data.geonames.map(country => ({
                        id: country.countryName, // Store full name as ID
                        text: country.countryName,
                        code: country.countryCode // Store code separately
                    }));
                    
                    return { results: countries };
                } catch (error) {
                    console.error('Error processing countries:', error);
                    return { results: [] };
                }
            },
            cache: true,
            transport: function(params, success, failure) {
                const $request = $.ajax(params);
                
                $request.then(success).fail(function(jqXHR, textStatus, error) {
                    console.error('GeoNames country request failed:', textStatus, error);
                    showToast('Failed to load countries. Please try again.', 'error');
                    failure(jqXHR, textStatus, error);
                });
                
                return $request;
            }
        },
        minimumInputLength: 2,
        escapeMarkup: function(markup) { return markup; },
        templateResult: formatLocationResult,
        templateSelection: formatLocationSelection
    });

    // State dropdown - depends on country
    $('#unified_mailing_state').select2({
        placeholder: 'Select State',
        allowClear: true,
        ajax: {
            url: `${GEONAMES_ENDPOINT}/searchJSON`,
            dataType: 'json',
            delay: 250,
            data: function(params) {
                const countryElement = $('#unified_mailing_country');
                const countryData = countryElement.select2('data')[0];
                const countryCode = countryData ? countryData.code : null;
                
                return {
                    q: params.term,
                    username: GEONAMES_USERNAME,
                    featureCode: 'ADM1',
                    country: countryCode,
                    maxRows: 6
                };
            },
            processResults: function(data, params) {
                try {
                    if (!data || !data.geonames) {
                        console.error('Invalid GeoNames state data:', data);
                        return { results: [] };
                    }
                    
                    const states = data.geonames.map(state => ({
                        id: state.name,
                        text: state.name,
                        countryCode: state.countryCode
                    }));
                    
                    return { results: states };
                } catch (error) {
                    console.error('Error processing states:', error);
                    return { results: [] };
                }
            },
            cache: true,
            transport: function(params, success, failure) {
                if (!params.data.country) {
                    showToast('Please select a country first', 'warning');
                    return { results: [] };
                }
                
                const $request = $.ajax(params);
                
                $request.then(success).fail(function(jqXHR, textStatus, error) {
                    console.error('GeoNames state request failed:', textStatus, error);
                    showToast('Failed to load states. Please try again.', 'error');
                    failure(jqXHR, textStatus, error);
                });
                
                return $request;
            }
        },
        minimumInputLength: 1,
        escapeMarkup: function(markup) { return markup; },
        templateResult: formatLocationResult,
        templateSelection: formatLocationSelection
    });

    // City dropdown - depends on country and state
    $('#unified_mailing_city').select2({
        placeholder: 'Select City',
        allowClear: true,
        ajax: {
            url: `${GEONAMES_ENDPOINT}/searchJSON`,
            dataType: 'json',
            delay: 250,
            data: function(params) {
                const countryElement = $('#unified_mailing_country');
                const countryData = countryElement.select2('data')[0];
                const countryCode = countryData ? countryData.code : null;
                const state = $('#unified_mailing_state').val();
                
                let searchParams = {
                    q: params.term,
                    username: GEONAMES_USERNAME,
                    featureClass: 'P',
                    country: countryCode,
                    maxRows: 6
                };
                
                if (state && state.trim() !== '') {
                    searchParams.adminName1 = state;
                }
                
                return searchParams;
            },
            processResults: function(data, params) {
                try {
                    if (!data || !data.geonames) {
                        console.error('Invalid GeoNames city data:', data);
                        return { results: [] };
                    }
                    
                    const cities = data.geonames.map(city => ({
                        id: city.name,
                        text: city.name,
                        countryCode: city.countryCode,
                        adminName1: city.adminName1
                    }));
                    
                    return { results: cities };
                } catch (error) {
                    console.error('Error processing cities:', error);
                    return { results: [] };
                }
            },
            cache: true,
            transport: function(params, success, failure) {
                if (!params.data.country) {
                    showToast('Please select a country first', 'warning');
                    return failure('Country required');
                }
                
                const $request = $.ajax(params);
                
                $request.then(success).fail(function(jqXHR, textStatus, error) {
                    console.error('GeoNames city request failed:', textStatus, error);
                    console.error('Request URL:', params.url);
                    console.error('Request data:', params.data);
                    showToast('Failed to load cities. Please try again.', 'error');
                    failure(jqXHR, textStatus, error);
                });
                
                return $request;
            }
        },
        minimumInputLength: 1,
        escapeMarkup: function(markup) { return markup; },
        templateResult: formatLocationResult,
        templateSelection: formatLocationSelection
    });

    // Reset dependent dropdowns when parent changes
    $('#unified_mailing_country').on('change', function() {
        $('#unified_mailing_state').val(null).trigger('change');
        $('#unified_mailing_city').val(null).trigger('change');
    });

    $('#unified_mailing_state').on('change', function() {
        $('#unified_mailing_city').val(null).trigger('change');
    });
}

function initializeContactDropdowns() {
    // Contact Country dropdown - now stores and displays full country name
    $('#unified_contacts_country').select2({
        placeholder: 'Select Country',
        allowClear: true,
        ajax: {
            url: `${GEONAMES_ENDPOINT}/countryInfoJSON`,
            dataType: 'json',
            delay: 250,
            data: function(params) {
                return {
                    q: params.term,
                    username: GEONAMES_USERNAME,
                    style: 'full'
                };
            },
            processResults: function(data, params) {
                try {
                    if (!data || !data.geonames) {
                        console.error('Invalid GeoNames country data:', data);
                        return { results: [] };
                    }
                    
                    const countries = data.geonames.map(country => ({
                        id: country.countryName, // Store full name as ID
                        text: country.countryName,
                        code: country.countryCode // Store code separately
                    }));
                    
                    return { results: countries };
                } catch (error) {
                    console.error('Error processing countries:', error);
                    return { results: [] };
                }
            },
            cache: true,
            transport: function(params, success, failure) {
                const $request = $.ajax(params);
                
                $request.then(success).fail(function(jqXHR, textStatus, error) {
                    console.error('GeoNames country request failed:', textStatus, error);
                    showToast('Failed to load countries. Please try again.', 'error');
                    failure(jqXHR, textStatus, error);
                });
                
                return $request;
            }
        },
        minimumInputLength: 1,
        escapeMarkup: function(markup) { return markup; },
        templateResult: formatLocationResult,
        templateSelection: formatLocationSelection
    });

    // Contact State dropdown - depends on country
    $('#unified_contacts_state').select2({
        placeholder: 'Select State',
        allowClear: true,
        ajax: {
            url: `${GEONAMES_ENDPOINT}/searchJSON`,
            dataType: 'json',
            delay: 250,
            data: function(params) {
                const countryElement = $('#unified_contacts_country');
                const countryData = countryElement.select2('data')[0];
                const countryCode = countryData ? countryData.code : null;
                
                return {
                    q: params.term,
                    username: GEONAMES_USERNAME,
                    featureCode: 'ADM1',
                    country: countryCode,
                    maxRows: 6
                };
            },
            processResults: function(data, params) {
                try {
                    if (!data || !data.geonames) {
                        console.error('Invalid GeoNames state data:', data);
                        return { results: [] };
                    }
                    
                    const states = data.geonames.map(state => ({
                        id: state.name,
                        text: state.name,
                        countryCode: state.countryCode
                    }));
                    
                    return { results: states };
                } catch (error) {
                    console.error('Error processing states:', error);
                    return { results: [] };
                }
            },
            cache: true,
            transport: function(params, success, failure) {
                if (!params.data.country) {
                    showToast('Please select a country first', 'warning');
                    return { results: [] };
                }
                
                const $request = $.ajax(params);
                
                $request.then(success).fail(function(jqXHR, textStatus, error) {
                    console.error('GeoNames state request failed:', textStatus, error);
                    showToast('Failed to load states. Please try again.', 'error');
                    failure(jqXHR, textStatus, error);
                });
                
                return $request;
            }
        },
        minimumInputLength: 1,
        escapeMarkup: function(markup) { return markup; },
        templateResult: formatLocationResult,
        templateSelection: formatLocationSelection
    });

    // Contact City dropdown - depends on country and state
    $('#contacts_city').select2({
        placeholder: 'Select City',
        allowClear: true,
        ajax: {
            url: `${GEONAMES_ENDPOINT}/searchJSON`,
            dataType: 'json',
            delay: 250,
            data: function(params) {
                const countryElement = $('#unified_contacts_country');
                const countryData = countryElement.select2('data')[0];
                const countryCode = countryData ? countryData.code : null;
                
                return {
                    q: params.term,
                    username: GEONAMES_USERNAME,
                    featureClass: 'P',
                    country: countryCode,
                    maxRows: 6
                };
            },
            processResults: function(data, params) {
                try {
                    if (!data || !data.geonames) {
                        console.error('Invalid GeoNames city data:', data);
                        return { results: [] };
                    }
                    
                    const cities = data.geonames.map(city => ({
                        id: city.name,
                        text: city.name,
                        countryCode: city.countryCode,
                        adminName1: city.adminName1
                    }));
                    
                    return { results: cities };
                } catch (error) {
                    console.error('Error processing cities:', error);
                    return { results: [] };
                }
            },
            cache: true,
            transport: function(params, success, failure) {
                if (!params.data.country) {
                    showToast('Please select a country first', 'warning');
                    return { results: [] };
                }
                
                const $request = $.ajax(params);
                
                $request.then(success).fail(function(jqXHR, textStatus, error) {
                    console.error('GeoNames city request failed:', textStatus, error);
                    showToast('Failed to load cities. Please try again.', 'error');
                    failure(jqXHR, textStatus, error);
                });
                
                return $request;
            }
        },
        minimumInputLength: 1,
        escapeMarkup: function(markup) { return markup; },
        templateResult: formatLocationResult,
        templateSelection: formatLocationSelection
    });

    // Reset dependent dropdowns when parent changes for contact fields
    $('#unified_contacts_country').on('change', function() {
        $('#unified_contacts_state').val(null).trigger('change');
        $('#contacts_city').val(null).trigger('change');
    });

    $('#unified_contacts_state').on('change', function() {
        $('#contacts_city').val(null).trigger('change');
    });
}

// Helper functions for Select2 templates
function formatLocationResult(location) {
    if (!location.id) return location.text;
    
    let text = location.text;
    if (location.countryCode) {
        text += ` (${location.countryCode})`;
    }
    if (location.adminName1) {
        text += `, ${location.adminName1}`;
    }
    
    return $('<span>').text(text);
}

function formatLocationSelection(location) {
    if (location && location.text) {
        return location.text;
    }
    return location;
}

// Call this function in your DOMContentLoaded handler
document.addEventListener("DOMContentLoaded", function() {
    try {
        initializeLocationDropdowns();
    } catch (error) {
        console.error('Error initializing location dropdowns:', error);
        showToast('Failed to initialize location search. Please refresh the page.', 'error');
    }
});