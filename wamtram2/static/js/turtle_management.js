document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded');

    const searchButtons = document.querySelectorAll('[id$="SearchBtn"]');
    const searchResultForm = document.getElementById('searchResultForm');
    const noResultsDiv = document.getElementById('noResults');
    const loadingSpinner = document.querySelector('.loading-spinner');
    const loadingOverlay = document.querySelector('.loading-overlay');
    const saveButton = document.getElementById('saveTurtleBtn');

    console.log('Found search buttons:', searchButtons.length);

    const searchTypeMapping = {
        'turtleid': 'turtle_id',
        'flippertag': 'tag_id',
        'pittag': 'pit_tag_id',
        'otheridentification': 'other_id'
    };

    const saveConfirmationModal = new bootstrap.Modal(document.getElementById('saveConfirmationModal'));
    const unsavedChangesModal = new bootstrap.Modal(document.getElementById('unsavedChangesModal'));
    let originalFormData = {};
    let hasUnsavedChanges = false;
    let pendingSearchData = null;

    function saveOriginalFormData() {
        originalFormData = {};
        const formElements = searchResultForm.querySelectorAll('input, select');
        formElements.forEach(element => {
            originalFormData[element.name] = element.value;
        });
    }

    function getFormChanges() {
        const changes = {};
        const currentFormData = {};
        const formElements = searchResultForm.querySelectorAll('input, select');
        
        formElements.forEach(element => {
            const value = element.value;
            if (value !== originalFormData[element.name]) {
                const label = element.previousElementSibling?.textContent || element.name;
                changes[label] = {
                    old: originalFormData[element.name] || '(empty)',
                    new: value || '(empty)'
                };
            }
        });
        
        return changes;
    }

    function showSaveConfirmation(changes) {
        const changesContent = document.getElementById('changesContent');
        if (Object.keys(changes).length === 0) {
            changesContent.innerHTML = '<p>No changes detected.</p>';
            return false;
        }

        let html = '<h6>The following changes will be saved:</h6><ul>';
        for (const [field, values] of Object.entries(changes)) {
            html += `<li>${field}: <br>
                     <span class="text-muted">From: ${values.old}</span><br>
                     <span class="text-success">To: ${values.new}</span></li>`;
        }
        html += '</ul>';
        changesContent.innerHTML = html;
        saveConfirmationModal.show();
        return true;
    }

    async function handleSearch(searchType, searchValue) {
        if (hasUnsavedChanges) {
            pendingSearchData = { searchType, searchValue };
            unsavedChangesModal.show();
            return;
        }
        
        try {
            loadingSpinner.style.display = 'block';
            loadingOverlay.style.display = 'block';

            const formElements = searchResultForm.querySelectorAll('input, select');
            formElements.forEach(element => element.value = '');
            noResultsDiv.style.display = 'none';

            const params = new URLSearchParams();
            params.append(searchType, searchValue);

            console.log('Fetching from:', `/wamtram2/api/turtle-search/?${params.toString()}`);

            const response = await fetch(`/wamtram2/api/turtle-search/?${params.toString()}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();
            console.log('Search response:', data);

            if (data.status === 'success' && data.data.length > 0) {
                const turtle = data.data[0];
                console.log('Received turtle data:', turtle);
                
                searchResultForm.style.display = 'block';
                
                Object.keys(turtle).forEach(key => {
                    const element = searchResultForm.querySelector(`[name="${key}"]`);
                    console.log(`Setting ${key} = ${turtle[key]}, Found element:`, element);
                    if (element) {
                        element.value = turtle[key] || '';
                        console.log(`After setting ${key}, value is:`, element.value);
                    }
                });
                saveOriginalFormData();
                hasUnsavedChanges = false;
            } else {
                noResultsDiv.style.display = 'block';
                searchResultForm.style.display = 'none';
            }
        } catch (error) {
            console.error('Search error:', error);
            showAlert('An error occurred while searching. Please try again.', 'danger');
        } finally {
            loadingSpinner.style.display = 'none';
            loadingOverlay.style.display = 'none';
        }
    }

    async function handleSave() {
        try {
            loadingSpinner.style.display = 'block';
            loadingOverlay.style.display = 'block';

            const formData = {};
            const formElements = searchResultForm.querySelectorAll('input, select');
            formElements.forEach(element => {
                formData[element.name] = element.value;
            });

            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            const response = await fetch('/wamtram2/api/turtle-update/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();
            console.log('Save response:', data);

            if (data.status === 'success') {
                showAlert('Changes saved successfully!', 'success');
            } else {
                showAlert(data.message || 'Error saving changes', 'danger');
            }
        } catch (error) {
            console.error('Save error:', error);
            showAlert('An error occurred while saving. Please try again.', 'danger');
        } finally {
            loadingSpinner.style.display = 'none';
            loadingOverlay.style.display = 'none';
        }
    }

    function showAlert(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} mt-3`;
        alertDiv.textContent = message;
        searchResultForm.parentNode.insertBefore(alertDiv, searchResultForm);
        setTimeout(() => alertDiv.remove(), 3000);
    }

    searchButtons.forEach(button => {
        console.log('Adding click listener to button:', button.id);
        button.addEventListener('click', function() {
            console.log('Button clicked:', this.id);
            const searchInput = this.parentElement.previousElementSibling;
            console.log('Search input:', searchInput.id, 'value:', searchInput.value);
            let searchType = searchInput.id.replace('Search', '').toLowerCase();
            searchType = searchTypeMapping[searchType] || searchType;
            const searchValue = searchInput.value.trim();
            
            if (searchValue) {
                handleSearch(searchType, searchValue);
            }
        });
    });

    if (saveButton) {
        saveButton.addEventListener('click', function() {
            const changes = getFormChanges();
            if (showSaveConfirmation(changes)) {
                handleSave();
            }
        });
    }

    searchResultForm.addEventListener('change', function() {
        hasUnsavedChanges = true;
    });
}); 