document.addEventListener('DOMContentLoaded', function() {
    // Get the current form
    const form = document.getElementById('dataEntryForm');
    if (!form) return;

    // Get batch_id from global variable
    const batchId = window.BATCH_ID;
    if (!batchId) return;

    const findTurtleUrl = `/wamtram2/find-tagged-turtle/${batchId}/`;

    // Auto-save form state to localStorage
    function saveFormState() {
        const formData = new FormData(form);
        const formState = {};

        for (let [key, value] of formData.entries()) {
            formState[key] = value;
        }

        // Also save all .search-field values by id
        form.querySelectorAll('.search-field').forEach(input => {
            formState[input.id] = input.value;
        });

        localStorage.setItem(
            `formState_${batchId}`,
            JSON.stringify(formState)
        );
    }

    // Debounced auto-save while typing
    let saveTimeout;

    form.addEventListener('input', function () {
        clearTimeout(saveTimeout);

        saveTimeout = setTimeout(() => {
            saveFormState();
        }, 1000);
    });

    // Auto-save immediately for dropdowns, checkboxes, etc.
    form.addEventListener('change', function () {
        saveFormState();
    });

        // Check if there is saved form data and show confirmation dialog ONLY ONCE per batch
    const storageKey = `formState_${batchId}`;              // Key for saved form data
    const promptKey = `formState_prompted_${batchId}`;      // Key to track if prompt was already shown

    const savedState = localStorage.getItem(storageKey);
    const alreadyPrompted = localStorage.getItem(promptKey);

    // Only prompt user once
    if (savedState && !alreadyPrompted) {

        // Mark as prompted to avoid repeated popups
        localStorage.setItem(promptKey, "true");

        if (confirm('Would you like to use the previously saved form data?')) {

            const formState = JSON.parse(savedState);

            for (let [key, value] of Object.entries(formState)) {
                // Restore normal form fields
                const input = form.querySelector(`[name="${key}"]`);
                if (input) {
                    if (input.type === 'checkbox') {
                        input.checked = value === 'on';
                    } else {
                        input.value = value;
                    }
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                }

                // Restore search-field values by id
                const searchInput = form.querySelector(`#${key}.search-field`);
                if (searchInput) {
                    searchInput.value = value;
                    searchInput.dispatchEvent(new Event('input', { bubbles: true }));
                }
            }

            // Show restore message
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert alert-info alert-dismissible fade show';
            alertDiv.role = 'alert';
            alertDiv.innerHTML = `
                Previous form data has been restored.
                <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
            `;
            form.insertBefore(alertDiv, form.firstChild);
            setTimeout(() => { alertDiv.remove(); }, 3000);

            // Remove saved data after restore
            localStorage.removeItem(storageKey);

        } else {
            // If user declines, clear stored data
            localStorage.removeItem(storageKey);
        }
    }

    // Clear saved state after successful form submission
    form.addEventListener('submit', function() {
        localStorage.removeItem(`formState_${batchId}`);
        localStorage.removeItem(`formState_prompted_${batchId}`); // Reset prompt flag
    });
});