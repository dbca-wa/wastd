document.addEventListener('DOMContentLoaded', function() {
    // Get the current form
    const form = document.getElementById('dataEntryForm');
    if (!form) return;

    // Get batch_id from current URL
    const urlParams = new URLSearchParams(window.location.search);
    const batchId = urlParams.get('batch_id');
    if (!batchId) return;

    // Create and add save button
    const saveButton = document.createElement('button');
    saveButton.type = 'button';
    saveButton.className = 'btn btn-info';
    saveButton.innerHTML = '<i class="fas fa-save"></i> Save Form State';
    saveButton.style.marginRight = '10px';
    
    // Add button next to the Review button
    const reviewBtn = document.getElementById('reviewBtn');
    if (reviewBtn) {
        reviewBtn.parentNode.insertBefore(saveButton, reviewBtn);
    }

    // Save form state to sessionStorage
    function saveFormState() {
        const formData = new FormData(form);
        const formState = {};
        for (let [key, value] of formData.entries()) {
            formState[key] = value;
        }
        sessionStorage.setItem(`formState_${batchId}`, JSON.stringify(formState));
        
        // Show success message
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-success alert-dismissible fade show';
        alertDiv.role = 'alert';
        alertDiv.innerHTML = `
            Form state saved successfully. You can now switch to another URL.
            <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span>
            </button>
        `;
        form.insertBefore(alertDiv, form.firstChild);
        
        // Auto dismiss alert after 3 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 3000);
    }

    // Restore form state from sessionStorage
    function restoreFormState() {
        const savedState = sessionStorage.getItem(`formState_${batchId}`);
        if (savedState) {
            const formState = JSON.parse(savedState);
            for (let [key, value] of Object.entries(formState)) {
                const input = form.querySelector(`[name="${key}"]`);
                if (input) {
                    if (input.type === 'checkbox') {
                        input.checked = value === 'on';
                    } else {
                        input.value = value;
                    }
                    // Trigger change event to update related UI
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }
            
            // Show restore message
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert alert-info alert-dismissible fade show';
            alertDiv.role = 'alert';
            alertDiv.innerHTML = `
                Previous form state has been restored.
                <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
            `;
            form.insertBefore(alertDiv, form.firstChild);
            
            // Auto dismiss alert after 3 seconds
            setTimeout(() => {
                alertDiv.remove();
            }, 3000);
        }
    }

    // Add click event listener to save button
    saveButton.addEventListener('click', saveFormState);

    // Restore form state on page load
    restoreFormState();

    // Clear saved state after successful form submission
    form.addEventListener('submit', function() {
        sessionStorage.removeItem(`formState_${batchId}`);
    });
}); 