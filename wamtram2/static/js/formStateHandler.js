document.addEventListener('DOMContentLoaded', function() {
    // Get the current form
    const form = document.getElementById('dataEntryForm');
    if (!form) return;

    // Get batch_id from global variable
    const batchId = window.BATCH_ID;
    if (!batchId) return;

    const findTurtleUrl = `/wamtram2/find-tagged-turtle/${batchId}/`;

    // Save button event
    const saveButton = document.getElementById('saveFormStateBtn');
    if (saveButton) {
        saveButton.addEventListener('click', function() {
            const formData = new FormData(form);
            const formState = {};
            for (let [key, value] of formData.entries()) {
                formState[key] = value;
            }
            // Also save all .search-field values by id
            form.querySelectorAll('.search-field').forEach(input => {
                formState[input.id] = input.value;
            });
            localStorage.setItem(`formState_${batchId}`, JSON.stringify(formState));
            // Show success message
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert alert-success alert-dismissible fade show';
            alertDiv.role = 'alert';
            alertDiv.innerHTML = `
                Form data saved successfully. 
                <a href="${findTurtleUrl}" class="alert-link">Go to Find Turtle for this batch</a>.
                You can now create a new entry and use this data.
                <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
            `;
            form.insertBefore(alertDiv, form.firstChild);
            setTimeout(() => { alertDiv.remove(); }, 3000);
        });
    }

    // Check if there's saved data and show confirmation dialog
    const savedState = localStorage.getItem(`formState_${batchId}`);
    if (savedState) {
        if (confirm('Would you like to use the previously saved form data?')) {
            const formState = JSON.parse(savedState);
            for (let [key, value] of Object.entries(formState)) {
                // Restore form fields
                const input = form.querySelector(`[name="${key}"]`);
                if (input) {
                    if (input.type === 'checkbox') {
                        input.checked = value === 'on';
                    } else {
                        input.value = value;
                    }
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                }
                // Restore .search-field values by id
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

            // Remove saved state after successful restore
            localStorage.removeItem(`formState_${batchId}`);
        } else {
            // If user chooses not to use saved data, remove it
            localStorage.removeItem(`formState_${batchId}`);
        }
    }

    // Clear saved state after successful form submission
    form.addEventListener('submit', function() {
        localStorage.removeItem(`formState_${batchId}`);
    });
});