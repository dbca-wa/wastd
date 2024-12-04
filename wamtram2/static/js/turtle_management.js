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

    const saveConfirmationModalElement = document.getElementById('saveConfirmationModal');
    const unsavedChangesModalElement = document.getElementById('unsavedChangesModal');
    
    const saveConfirmationModal = saveConfirmationModalElement ? 
        new bootstrap.Modal(saveConfirmationModalElement) : null;
    const unsavedChangesModal = unsavedChangesModalElement ? 
        new bootstrap.Modal(unsavedChangesModalElement) : null;

    let originalFormData = {};
    let hasUnsavedChanges = false;
    let pendingSearchData = null;

    function clearForm() {
        if (searchResultForm) {
            const formElements = searchResultForm.querySelectorAll('input, select');
            formElements.forEach(element => {
                element.value = '';
            });
            
            const containers = [
                'tagContainer',
                'pitTagContainer',
                'identificationContainer',
                'observationContainer',
                'sampleContainer',
                'documentContainer'
            ];
            
            containers.forEach(containerId => {
                const container = document.getElementById(containerId);
                if (container) {
                    container.innerHTML = '';
                }
            });

            searchResultForm.style.display = 'none';
            if (noResultsDiv) {
                noResultsDiv.style.display = 'none';
            }
        }
    }

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
        if (!saveConfirmationModal) {
            console.error('Save confirmation modal not found');
            return false;
        }

        const changesContent = document.getElementById('changesContent');
        if (!changesContent) {
            console.error('Changes content element not found');
            return false;
        }

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
        if (hasUnsavedChanges && unsavedChangesModal) {
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
                
                populateBasicInfo(turtle);
                
                populateTagInfo(turtle);
                
                populatePitTagInfo(turtle);
                
                populateIdentificationInfo(turtle);
                
                populateObservationInfo(turtle);
                
                populateSampleInfo(turtle);
                
                populateDocumentInfo(turtle);
                
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

    function populateBasicInfo(turtle) {
        const basicInfoFields = {
            'turtle_id': turtle.turtle_id,
            'species': turtle.species,
            'turtle_name': turtle.turtle_name,
            'sex': turtle.sex,
            'cause_of_death': turtle.cause_of_death,
            'turtle_status': turtle.turtle_status,
            'date_entered': turtle.date_entered,
            'comments': turtle.comments,
            'location': turtle.location
        };

        Object.entries(basicInfoFields).forEach(([field, value]) => {
            const element = searchResultForm.querySelector(`[name="${field}"]`);
            if (element) {
                element.value = value || '';
            }
        });
    }

    function populateTagInfo(turtle) {
        const tagContainer = document.getElementById('tagContainer');
        tagContainer.innerHTML = '';

        if (!turtle.tags || turtle.tags.length === 0) {
            tagContainer.innerHTML = '<p class="text-muted">No tags found</p>';
            return;
        }

        turtle.tags.forEach(tag => {
            const tagHtml = `
                <div class="card mb-3 tag-card">
                    <div class="card-body">
                        <div class="form-row">
                            <div class="col-md-3">
                                <div class="form-group">
                                    <label>Tag ID</label>
                                    <input type="text" class="form-control" name="tag_id" value="${tag.tag_id}">
                                </div>
                            </div>
                            <div class="col-md-2">
                                <div class="form-group">
                                    <label>Side</label>
                                    <input type="text" class="form-control" name="side" value="${tag.side || ''}">
                                </div>
                            </div>
                            <div class="col-md-2">
                                <div class="form-group">
                                    <label>Status</label>
                                    <input type="text" class="form-control" name="tag_status" value="${tag.tag_status || ''}">
                                </div>
                            </div>
                            <div class="col-md-2">
                                <div class="form-group">
                                    <label>Issue Location</label>
                                    <input type="text" class="form-control" name="issue_location" value="${tag.issue_location || ''}">
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="form-group">
                                    <label>Comments</label>
                                    <input type="text" class="form-control" name="comments" value="${tag.comments || ''}">
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            tagContainer.insertAdjacentHTML('beforeend', tagHtml);
        });
    }

    function populatePitTagInfo(turtle) {
        const pitTagContainer = document.getElementById('pitTagContainer');
        pitTagContainer.innerHTML = '';

        if (!turtle.pit_tags || turtle.pit_tags.length === 0) {
            pitTagContainer.innerHTML = '<p class="text-muted">No PIT tags found</p>';
            return;
        }

        turtle.pit_tags.forEach(tag => {
            const pitTagHtml = `
                <div class="card mb-3 pit-tag-card">
                    <div class="card-body">
                        <div class="form-row">
                            <div class="col-md-3">
                                <div class="form-group">
                                    <label>PIT Tag ID</label>
                                    <input type="text" class="form-control" name="pit_tag_id" value="${tag.pit_tag_id}">
                                </div>
                            </div>
                            <div class="col-md-2">
                                <div class="form-group">
                                    <label>Status</label>
                                    <input type="text" class="form-control" name="pit_tag_status" value="${tag.pit_tag_status || ''}">
                                </div>
                            </div>
                            <div class="col-md-2">
                                <div class="form-group">
                                    <label>Issue Location</label>
                                    <input type="text" class="form-control" name="issue_location" value="${tag.issue_location || ''}">
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="form-group">
                                    <label>Comments</label>
                                    <input type="text" class="form-control" name="comments" value="${tag.comments || ''}">
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            pitTagContainer.insertAdjacentHTML('beforeend', pitTagHtml);
        });
    }

    function populateIdentificationInfo(turtle) {
        const identificationContainer = document.getElementById('identificationContainer');
        identificationContainer.innerHTML = '';

        if (!turtle.identifications || turtle.identifications.length === 0) {
            identificationContainer.innerHTML = '<p class="text-muted">No other identifications found</p>';
            return;
        }

        turtle.identifications.forEach(ident => {
            const identHtml = `
                <div class="card mb-3 identification-card">
                    <div class="card-body">
                        <div class="form-row">
                            <div class="col-md-3">
                                <div class="form-group">
                                    <label>Type</label>
                                    <input type="text" class="form-control" name="identification_type" value="${ident.identification_type}" readonly>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="form-group">
                                    <label>Identifier</label>
                                    <input type="text" class="form-control" name="identifier" value="${ident.identifier || ''}" readonly>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="form-group">
                                    <label>Comments</label>
                                    <input type="text" class="form-control" name="identification_comments" value="${ident.comments || ''}" readonly>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            identificationContainer.insertAdjacentHTML('beforeend', identHtml);
        });
    }

    function populateObservationInfo(turtle) {
        const observationContainer = document.getElementById('observationContainer');
        observationContainer.innerHTML = '';

        if (!turtle.observations || turtle.observations.length === 0) {
            observationContainer.innerHTML = '<p class="text-muted">No observations found</p>';
            return;
        }

        turtle.observations.forEach(obs => {
            const obsHtml = `
                <div class="card mb-3 observation-card">
                    <div class="card-body">
                        <div class="form-row">
                            <div class="col-md-1">
                                <div class="form-group">
                                    <label>Observation ID</label>
                                    <a href="/wamtram2/curation/observations-management/${obs.observation_id}/"class="form-control"target="_blank">${obs.observation_id}</a>
                                </div>
                            </div>
                            <div class="col-md-2">
                                <div class="form-group">
                                    <label>Date/Time</label>
                                    <input type="datetime-local" class="form-control" name="observation_datetime" value="${obs.date_time}" >
                                </div>
                            </div>
                            <div class="col-md-2">
                                <div class="form-group">
                                    <label>Status</label>
                                    <input type="text" class="form-control" name="observation_status" value="${obs.observation_status || ''}" >
                                </div>
                            </div>
                            <div class="col-md-2">
                                <div class="form-group">
                                    <label>Alive</label>
                                    <input type="text" class="form-control" name="alive" value="${obs.alive || ''}" >
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="form-group">
                                    <label>Place</label>
                                    <input type="text" class="form-control" name="place" value="${obs.place || ''}" >
                                </div>
                            </div>
                            <div class="col-md-2">
                                <div class="form-group">
                                    <label>Activity</label>
                                    <input type="text" class="form-control" name="activity" value="${obs.activity || ''}" >
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            observationContainer.insertAdjacentHTML('beforeend', obsHtml);
        });
    }

    function populateSampleInfo(turtle) {
        const sampleContainer = document.getElementById('sampleContainer');
        sampleContainer.innerHTML = '';

        if (!turtle.samples || turtle.samples.length === 0) {
            sampleContainer.innerHTML = '<p class="text-muted">No samples found</p>';
            return;
        }

        turtle.samples.forEach(sample => {
            const sampleHtml = `
                <div class="card mb-3 sample-card">
                    <div class="card-body">
                        <div class="form-row">
                            <div class="col-md-3">
                                <div class="form-group">
                                    <label>Tissue Type</label>
                                    <input type="text" class="form-control" name="tissue_type" value="${sample.tissue_type}" >
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="form-group">
                                    <label>Observation ID</label>
                                    <input type="text" class="form-control" name="observation_id" value="${sample.observation_id || ''}" >
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="form-group">
                                    <label>Sample Label</label>
                                    <input type="text" class="form-control" name="sample_label" value="${sample.label || ''}" >
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="form-group">
                                    <label>Comments</label>
                                    <input type="text" class="form-control" name="sample_comments" value="${sample.comments || ''}" >
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            sampleContainer.insertAdjacentHTML('beforeend', sampleHtml);
        });
    }

    function populateDocumentInfo(turtle) {
        const documentContainer = document.getElementById('documentContainer');
        documentContainer.innerHTML = '';

        if (!turtle.documents || turtle.documents.length === 0) {
            documentContainer.innerHTML = '<p class="text-muted">No documents found</p>';
            return;
        }

        turtle.documents.forEach(doc => {
            const docHtml = `
                <div class="card mb-3 document-card">
                    <div class="card-body">
                        <div class="form-row">
                            <div class="col-md-3">
                                <div class="form-group">
                                    <label>Document Type</label>
                                    <input type="text" class="form-control" name="document_type" value="${doc.document_type}" >
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="form-group">
                                    <label>File Name</label>
                                    <input type="text" class="form-control" name="file_name" value="${doc.file_name || ''}" >
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="form-group">
                                    <label>Person</label>
                                    <input type="text" class="form-control" name="person_id" value="${doc.person_id || ''}" >
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="form-group">
                                    <label>Comments</label>
                                    <input type="text" class="form-control" name="document_comments" value="${doc.comments || ''}" >
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            documentContainer.insertAdjacentHTML('beforeend', docHtml);
        });
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
            if (!csrfToken) {
                throw new Error('CSRF token not found');
            }
    

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
                document.getElementById('confirmSaveBtn')?.addEventListener('click', function() {
                    saveConfirmationModal?.hide();
                    handleSave();
                });
            }
        });
    }

    if (searchResultForm) {
        searchResultForm.addEventListener('change', function() {
            hasUnsavedChanges = true;
        });
    }

    document.getElementById('discardChangesBtn')?.addEventListener('click', function() {
        unsavedChangesModal?.hide();
        hasUnsavedChanges = false;
        if (pendingSearchData) {
            const { searchType, searchValue } = pendingSearchData;
            pendingSearchData = null;
            handleSearch(searchType, searchValue);
        }
    });

    clearForm();
});
