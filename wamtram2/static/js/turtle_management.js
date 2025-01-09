document.addEventListener('DOMContentLoaded', function() {

    const searchButtons = document.querySelectorAll('[id$="SearchBtn"]');
    const searchResultForm = document.getElementById('searchResultForm');
    const noResultsDiv = document.getElementById('noResults');
    const loadingSpinner = document.querySelector('.loading-spinner');
    const loadingOverlay = document.querySelector('.loading-overlay');
    const saveButton = document.getElementById('saveTurtleBtn');

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
    let deletedTags = [];
    let deletedPitTags = [];
    let deletedIdentifications = [];
    let deletedSamples = [];
    let deletedDocuments = [];

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

            const response = await fetch(`/wamtram2/api/turtle-search/?${params.toString()}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();

            if (data.status === 'success' && data.data.length > 0) {
                const turtle = data.data[0];
                
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

        turtle.tags.forEach(async tag => {
            const tagHtml = `
                <div class="card mb-3 tag-card" data-tag-id="${tag.tag_id}">
                    <div class="card-body">
                        <div class="form-row">
                            <div class="col-md-2">
                                <div class="form-group">
                                    <label>Tag ID</label>
                                    <input type="text" class="form-control" name="tag_id" value="${tag.tag_id}" readonly>
                                </div>
                            </div>
                            <div class="col-md-2">
                                <div class="form-group">
                                    <label>Side</label>
                                    <select class="form-control" name="side">
                                        <option value="L" ${tag.side === 'L' ? 'selected' : ''}>L</option>
                                        <option value="R" ${tag.side === 'R' ? 'selected' : ''}>R</option>
                                    </select>
                                </div>
                            </div>
                            <div class="col-md-2">
                                <div class="form-group">
                                    <label>Status</label>
                                    <select class="form-control" name="tag_status">
                                        <!-- Will be populated by JavaScript -->
                                    </select>
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
                            <div class="col-md-1">
                                <div class="form-group">
                                    <label>&nbsp;</label>
                                    <button type="button" class="btn btn-danger btn-block delete-tag">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            tagContainer.insertAdjacentHTML('beforeend', tagHtml);
    
            const statusSelect = tagContainer.lastElementChild.querySelector('[name="tag_status"]');
            populateTagStatus(statusSelect, tag.tag_status);
        });
    }

    function populatePitTagInfo(turtle) {
        const container = document.getElementById('pitTagContainer');
        container.innerHTML = '';

        if (!turtle.pit_tags || turtle.pit_tags.length === 0) {
            container.innerHTML = '<p class="text-muted">No PIT tags found</p>';
            return;
        }

        turtle.pit_tags.forEach(tag => {
            const tagHtml = `
                <div class="card mb-3 tag-card" data-tag-id="${tag.pit_tag_id}">
                    <div class="card-body">
                        <div class="form-row">
                            <div class="col-md-3">
                                <div class="form-group">
                                    <label>PIT Tag ID</label>
                                    <input type="text" class="form-control" name="pit_tag_id" value="${tag.pit_tag_id}" readonly>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="form-group">
                                    <label>Status</label>
                                    <select class="form-control" name="pit_tag_status">
                                    </select>
                                </div>
                            </div>
                            <div class="col-md-5">
                                <div class="form-group">
                                    <label>Comments</label>
                                    <input type="text" class="form-control" name="comments" value="${tag.comments || ''}">
                                </div>
                            </div>
                            <div class="col-md-1">
                                <div class="form-group">
                                    <label>&nbsp;</label>
                                    <button type="button" class="btn btn-danger btn-block delete-pit-tag">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            container.insertAdjacentHTML('beforeend', tagHtml);
            
            const statusSelect = container.lastElementChild.querySelector('[name="pit_tag_status"]');
            populateTagStatus(statusSelect);
            statusSelect.value = tag.pit_tag_status;
        });
    }

    function populateIdentificationInfo(turtle) {
        const container = document.getElementById('identificationContainer');
        container.innerHTML = '';

        if (!turtle.identifications || turtle.identifications.length === 0) {
            container.innerHTML = '<p class="text-muted">No identifications found</p>';
            return;
        }

        turtle.identifications.forEach(ident => {
            const identHtml = `
                <div class="card mb-3 identification-card" data-identification-type="${ident.identification_type}">
                    <div class="card-body">
                        <div class="form-row">
                            <div class="col-md-3">
                                <div class="form-group">
                                    <label>Type</label>
                                    <select class="form-control" name="identification_type">
                                    </select>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="form-group">
                                    <label>Identifier</label>
                                    <input type="text" class="form-control" name="identifier" value="${ident.identifier || ''}">
                                </div>
                            </div>
                            <div class="col-md-5">
                                <div class="form-group">
                                    <label>Comments</label>
                                    <input type="text" class="form-control" name="comments" value="${ident.comments || ''}">
                                </div>
                            </div>
                            <div class="col-md-1">
                                <div class="form-group">
                                    <label>&nbsp;</label>
                                    <button type="button" class="btn btn-danger btn-block delete-identification">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            container.insertAdjacentHTML('beforeend', identHtml);
            
            const typeSelect = container.lastElementChild.querySelector('[name="identification_type"]');
            populateIdentificationTypes(typeSelect, ident.identification_type);
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
                                    <label>Observation</label>
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
        const container = document.getElementById('sampleContainer');
        container.innerHTML = '';

        if (!turtle.samples || turtle.samples.length === 0) {
            container.innerHTML = '<p class="text-muted">No samples found</p>';
            return;
        }

        turtle.samples.forEach(sample => {
            const template = document.getElementById('sampleTemplate');
            const clone = template.content.cloneNode(true);
            
            // Load tissue types
            const tissueTypeSelect = clone.querySelector('[name="tissue_type"]');
            const tissueTypes = JSON.parse(document.getElementById('tissue-types-data').textContent);
            tissueTypes.forEach(type => {
                const option = document.createElement('option');
                option.value = type.tissue_type;
                option.textContent = type.description;
                if (type.tissue_type === sample.tissue_type) {
                    option.selected = true;
                }
                tissueTypeSelect.appendChild(option);
            });
            
            // Fill other fields
            clone.querySelector('[name="sample_label"]').value = sample.sample_label || '';
            clone.querySelector('[name="observation_id"]').value = sample.observation_id || '';
            clone.querySelector('[name="comments"]').value = sample.comments || '';
            
            container.appendChild(clone);
        });
    }

    function populateDocumentInfo(turtle) {
        const container = document.getElementById('documentContainer');
        container.innerHTML = '';

        if (!turtle.documents || turtle.documents.length === 0) {
            container.innerHTML = '<p class="text-muted">No documents found</p>';
            return;
        }

        turtle.documents.forEach(doc => {
            const documentHtml = `
                <div class="card mb-3 document-card" data-document-id="${doc.document_id || ''}">
                    <div class="card-body">
                        <div class="form-row">
                            <div class="col-md-3">
                                <div class="form-group">
                                    <label>File Type</label>
                                    <select class="form-control" name="document_type">
                                    </select>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="form-group">
                                    <label>File Name</label>
                                    <input type="text" class="form-control" name="file_name" value="${doc.file_name || ''}">
                                </div>
                            </div>
                            <div class="col-md-2">
                                <div class="form-group">
                                    <label>Person</label>
                                    <input type="text" class="form-control" name="person_name" value="${doc.person_name || ''}">
                                    <input type="hidden" name="person_id" value="${doc.person_id || ''}">
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="form-group">
                                    <label>Comments</label>
                                    <input type="text" class="form-control" name="comments" value="${doc.comments || ''}">
                                </div>
                            </div>
                            <div class="col-md-1">
                                <div class="form-group">
                                    <label>&nbsp;</label>
                                    <button type="button" class="btn btn-danger btn-block delete-document">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            container.insertAdjacentHTML('beforeend', documentHtml);
            
            // Get the document type select box from the recently added document card
            const documentTypeSelect = container.lastElementChild.querySelector('[name="document_type"]');
            const documentTypesData = document.getElementById('document-types-data');
            
            if (documentTypesData) {
                const documentTypes = JSON.parse(documentTypesData.textContent);
                documentTypes.forEach(type => {
                    const option = document.createElement('option');
                    option.value = type.document_type;
                    option.textContent = type.description;
                    if (type.document_type === doc.document_type) {
                        option.selected = true;
                    }
                    documentTypeSelect.appendChild(option);
                });
            }
        });
    }

    async function handleSave() {
        try {
            loadingSpinner.style.display = 'block';
            loadingOverlay.style.display = 'block';

            const formData = {
                basic: {},
                flipperTags: [],
                pitTags: [],
                identifications: []
            };

            // Collect basic information
            searchResultForm.querySelectorAll('input, select').forEach(element => {
                if (!element.closest('.tag-card, .pit-tag-card, .identification-card')) {
                    formData.basic[element.name] = element.value;
                }
            });

            // Collect flipper tags
            document.querySelectorAll('.tag-card').forEach(card => {
                const tagData = {};
                card.querySelectorAll('input, select').forEach(element => {
                    if (element.name === 'tag_status') {
                        tagData[element.name] = element.value;
                    } else {
                        tagData[element.name] = element.value;
                    }
                });
                formData.flipperTags.push(tagData);
            });

            // Collect PIT tags
            document.querySelectorAll('.pit-tag-card').forEach(card => {
                const tagData = {};
                card.querySelectorAll('input, select').forEach(element => {
                    tagData[element.name] = element.value;
                });
                formData.pitTags.push(tagData);
            });

            // Collect identifications
            document.querySelectorAll('.identification-card').forEach(card => {
                const identData = {};
                card.querySelectorAll('input, select').forEach(element => {
                    identData[element.name] = element.value;
                });
                formData.identifications.push(identData);
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

            if (data.status === 'success') {
                showAlert('Changes saved successfully!', 'success');
                hasUnsavedChanges = false;
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
        button.addEventListener('click', function() {
            const searchInput = this.parentElement.previousElementSibling;
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

    // Load tag statuses from template data
    function loadTagStatuses() {
        const tagStatusesScript = document.getElementById('tag-statuses-data');
        if (tagStatusesScript) {
            try {
                return JSON.parse(tagStatusesScript.textContent);
            } catch (e) {
                console.error('Error parsing tag statuses:', e);
                return [];
            }
        }
        return [];
    }

    // Populate tag status select
    function populateTagStatus(selectElement, currentStatus = '') {
        const statuses = loadTagStatuses();
        selectElement.innerHTML = '<option value="">Select Status</option>';
        statuses.forEach(status => {
            const option = document.createElement('option');
            option.value = status.tag_status; 
            option.textContent = status.description; 
            if (status.tag_status === currentStatus) {  
                option.selected = true;
            }
            selectElement.appendChild(option);
        });
    }

    // Initialize all existing tag status selects
    document.querySelectorAll('[name="tag_status"]').forEach(select => {
        populateTagStatus(select);
    });

    // Handle saving flipper tags
    async function handleSaveFlipperTags() {
        const formData = {
            turtle_id: document.querySelector('[name="turtle_id"]').value,
            flipperTags: [],
            deletedTags: deletedTags 
        };

        // Collect flipper tags data
        document.querySelectorAll('.tag-card:not(.to-be-deleted)').forEach(card => {
            const tagData = {};
            card.querySelectorAll('input, select').forEach(element => {
                tagData[element.name] = element.value;
            });
            formData.flipperTags.push(tagData);
        });

        try {
            const response = await fetch('/wamtram2/api/flipper-tags-update/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (data.status === 'success') {
                // Clear deleted tags list after successful save
                deletedTags = [];
                // Remove deleted tag cards
                document.querySelectorAll('.tag-card.to-be-deleted').forEach(card => {
                    card.remove();
                });
                showAlert('Flipper tags updated successfully!', 'success');
            } else {
                // Restore deleted tags if save fails
                document.querySelectorAll('.tag-card.to-be-deleted').forEach(card => {
                    card.classList.remove('to-be-deleted');
                    card.style.opacity = '1';
                });
                showAlert(data.message || 'Error updating flipper tags', 'danger');
            }
        } catch (error) {
            console.error('Save error:', error);
            // Restore deleted tags if save fails
            document.querySelectorAll('.tag-card.to-be-deleted').forEach(card => {
                card.classList.remove('to-be-deleted');
                card.style.opacity = '1';
            });
            showAlert('An error occurred while updating flipper tags', 'danger');
        }
    }

    // Add event listener for save button
    document.getElementById('saveFlipperTagsBtn')?.addEventListener('click', handleSaveFlipperTags);

    // Track changes specifically for flipper tags
    document.getElementById('tagContainer')?.addEventListener('change', function(e) {
        if (e.target.closest('.tag-card')) {
            e.target.closest('.tag-card').dataset.hasChanges = 'true';
        }
    });

    // Modified add flipper tag button handler
    document.getElementById('addFlipperTagBtn')?.addEventListener('click', function() {
        const template = document.getElementById('flipperTagTemplate');
        const container = document.getElementById('tagContainer');
        const clone = template.content.cloneNode(true);
        
        // Populate tag status select for the new tag
        const statusSelect = clone.querySelector('[name="tag_status"]');
        populateTagStatus(statusSelect);
        
        // Add delete button event listener
        clone.querySelector('.delete-tag').addEventListener('click', function() {
            this.closest('.tag-card').remove();
        });
        
        container.appendChild(clone);
    });


    // Add new identification button handler
    document.getElementById('addIdentificationBtn')?.addEventListener('click', function() {
        const template = document.getElementById('identificationTemplate');
        const container = document.getElementById('identificationContainer');
        const clone = template.content.cloneNode(true);
        
        // Add delete button event listener
        clone.querySelector('.delete-identification').addEventListener('click', function() {
            this.closest('.identification-card').remove();
        });
        
        container.appendChild(clone);
    });

    // Handle delete button click event
    function handleDeleteTag(event) {
        const tagCard = event.target.closest('.tag-card');
        if (!tagCard) return;

        if (confirm('Are you sure you want to delete this tag?')) {
            const tagId = tagCard.dataset.tagId;
            if (tagId) {
                deletedTags.push(tagId);
            }
            tagCard.classList.add('to-be-deleted');
            tagCard.style.opacity = '0.5';
        }
    }

    // Add event listener for all delete buttons
    document.addEventListener('click', function(e) {
        if (e.target.closest('.delete-tag')) {
            handleDeleteTag(e);
        }
    });

    clearForm();

    // Add getCsrfToken function
    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    // Add new PIT Tag
    document.getElementById('addPitTagBtn')?.addEventListener('click', function() {
        const template = document.getElementById('pitTagTemplate');
        const container = document.getElementById('pitTagContainer');
        const clone = template.content.cloneNode(true);
        
        const statusSelect = clone.querySelector('[name="pit_tag_status"]');
        populateTagStatus(statusSelect);
        
        container.appendChild(clone);
    });

    // Handle delete button click event
    document.addEventListener('click', function(e) {
        if (e.target.closest('.delete-pit-tag')) {
            const tagCard = e.target.closest('.tag-card');
            if (tagCard && confirm('Are you sure you want to delete this PIT tag?')) {
                const tagId = tagCard.dataset.tagId;
                if (tagId) {
                    deletedPitTags.push(tagId);
                }
                tagCard.classList.add('to-be-deleted');
                tagCard.style.opacity = '0.5';
            }
        } else if (e.target.closest('.delete-identification')) {
            const identCard = e.target.closest('.identification-card');
            if (identCard && confirm('Are you sure you want to delete this identification?')) {
                const identId = identCard.dataset.identificationId;
                if (identId) {
                    deletedIdentifications.push(identId);
                }
                identCard.classList.add('to-be-deleted');
                identCard.style.opacity = '0.5';
            }
        }
    });

    // Save PIT Tags
    document.getElementById('savePitTagsBtn')?.addEventListener('click', async function() {
        const formData = {
            turtle_id: document.querySelector('[name="turtle_id"]').value,
            pitTags: [],
            deletedTags: deletedPitTags
        };

        document.querySelectorAll('#pitTagContainer .tag-card:not(.to-be-deleted)').forEach(card => {
            const tagData = {};
            card.querySelectorAll('input, select').forEach(element => {
                tagData[element.name] = element.value;
            });
            formData.pitTags.push(tagData);
        });

        try {
            const response = await fetch('/wamtram2/api/pit-tags-update/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (data.status === 'success') {
                deletedPitTags = [];
                document.querySelectorAll('#pitTagContainer .tag-card.to-be-deleted').forEach(card => {
                    card.remove();
                });
                showAlert('PIT tags updated successfully!', 'success');
            } else {
                document.querySelectorAll('#pitTagContainer .tag-card.to-be-deleted').forEach(card => {
                    card.classList.remove('to-be-deleted');
                    card.style.opacity = '1';
                });
                showAlert(data.message || 'Error updating PIT tags', 'danger');
            }
        } catch (error) {
            console.error('Save error:', error);
            document.querySelectorAll('#pitTagContainer .tag-card.to-be-deleted').forEach(card => {
                card.classList.remove('to-be-deleted');
                card.style.opacity = '1';
            });
            showAlert('An error occurred while updating PIT tags', 'danger');
        }
    });
    
    // Save Identifications
    document.getElementById('saveIdentificationBtn')?.addEventListener('click', async function() {
        const formData = {
            turtle_id: document.querySelector('[name="turtle_id"]').value,
            identifications: [],
            deletedIdentifications: deletedIdentifications
        };

        document.querySelectorAll('#identificationContainer .identification-card:not(.to-be-deleted)').forEach(card => {
            const identData = {};
            card.querySelectorAll('input, select').forEach(element => {
                identData[element.name] = element.value;
            });
            formData.identifications.push(identData);
        });

        try {
            const response = await fetch('/wamtram2/api/identifications-update/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (data.status === 'success') {
                deletedIdentifications = [];
                document.querySelectorAll('#identificationContainer .identification-card.to-be-deleted').forEach(card => {
                    card.remove();
                });
                showAlert('Identifications updated successfully!', 'success');
            } else {
                document.querySelectorAll('#identificationContainer .identification-card.to-be-deleted').forEach(card => {
                    card.classList.remove('to-be-deleted');
                    card.style.opacity = '1';
                });
                showAlert(data.message || 'Error updating identifications', 'danger');
            }
        } catch (error) {
            console.error('Save error:', error);
            document.querySelectorAll('#identificationContainer .identification-card.to-be-deleted').forEach(card => {
                card.classList.remove('to-be-deleted');
                card.style.opacity = '1';
            });
            showAlert('An error occurred while updating identifications', 'danger');
        }
    });

    // Load PIT tag statuses
    function loadPitTagStatuses() {
        const pitTagStatusesData = document.getElementById('pit-tag-statuses-data');
        if (!pitTagStatusesData) return [];
        return JSON.parse(pitTagStatusesData.textContent);
    }

    // Populate PIT tag status dropdown
    function populateTagStatus(selectElement, currentStatus = '') {
        const statuses = loadPitTagStatuses();
        selectElement.innerHTML = '<option value="">Select Status</option>';
        statuses.forEach(status => {
            const option = document.createElement('option');
            option.value = status.pit_tag_status;
            option.textContent = status.description;
            if (status.pit_tag_status === currentStatus) {
                option.selected = true;
            }
            selectElement.appendChild(option);
        });
    }

    // Load Identification Types
    function loadIdentificationTypes() {
        const identificationTypesData = document.getElementById('identification-types-data');
        if (!identificationTypesData) return [];
        return JSON.parse(identificationTypesData.textContent);
    }

    // Populate Identification Types dropdown
    function populateIdentificationTypes(selectElement, currentType = '') {
        const types = loadIdentificationTypes();
        selectElement.innerHTML = '<option value="">Select Type</option>';
        types.forEach(type => {
            const option = document.createElement('option');
            option.value = type.identification_type;
            option.textContent = type.description;
            if (type.identification_type === currentType) {
                option.selected = true;
            }
            selectElement.appendChild(option);
        });
    }

    // Add Sample button click handler
    document.getElementById('addSampleBtn')?.addEventListener('click', function() {
        const template = document.getElementById('sampleTemplate');
        const container = document.getElementById('sampleContainer');
        const clone = template.content.cloneNode(true);
        
        // 填充组织类型下拉框
        const tissueTypeSelect = clone.querySelector('[name="tissue_type"]');
        const tissueTypes = JSON.parse(document.getElementById('tissue-types-data').textContent);
        tissueTypes.forEach(type => {
            const option = document.createElement('option');
            option.value = type.tissue_type;
            option.textContent = type.description;
            tissueTypeSelect.appendChild(option);
        });
        
        // 添加删除按钮事件监听器
        clone.querySelector('.delete-sample').addEventListener('click', function() {
            this.closest('.sample-card').remove();
        });
        
        container.appendChild(clone);
    });

    // Add Document button click handler
    document.getElementById('addDocumentBtn')?.addEventListener('click', function() {
        const template = document.getElementById('documentTemplate');
        const container = document.getElementById('documentContainer');
        const clone = template.content.cloneNode(true);
        
        // 填充文档类型下拉框
        const documentTypeSelect = clone.querySelector('[name="document_type"]');
        const documentTypes = JSON.parse(document.getElementById('document-types-data').textContent);
        documentTypes.forEach(type => {
            const option = document.createElement('option');
            option.value = type.document_type;
            option.textContent = type.description;
            documentTypeSelect.appendChild(option);
        });
        
        // 添加删除按钮事件监听器
        clone.querySelector('.delete-document').addEventListener('click', function() {
            this.closest('.document-card').remove();
        });
        
        container.appendChild(clone);
    });

    // Save Samples
    document.getElementById('saveSamplesBtn')?.addEventListener('click', async function() {
        const formData = {
            turtle_id: document.querySelector('[name="turtle_id"]').value,
            samples: [],
            deletedSamples: deletedSamples || []
        };

        // Collect all non-deleted sample data
        document.querySelectorAll('#sampleContainer .sample-card:not(.to-be-deleted)').forEach(card => {
            const sampleData = {};
            card.querySelectorAll('input').forEach(element => {
                sampleData[element.name] = element.value;
            });
            formData.samples.push(sampleData);
        });

        try {
            const response = await fetch('/wamtram2/api/samples-update/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (data.status === 'success') {
                deletedSamples = [];
                document.querySelectorAll('#sampleContainer .sample-card.to-be-deleted').forEach(card => {
                    card.remove();
                });
                showAlert('Samples updated successfully!', 'success');
            } else {
                document.querySelectorAll('#sampleContainer .sample-card.to-be-deleted').forEach(card => {
                    card.classList.remove('to-be-deleted');
                    card.style.opacity = '1';
                });
                showAlert(data.message || 'Error updating samples', 'danger');
            }
        } catch (error) {
            console.error('Save error:', error);
            document.querySelectorAll('#sampleContainer .sample-card.to-be-deleted').forEach(card => {
                card.classList.remove('to-be-deleted');
                card.style.opacity = '1';
            });
            showAlert('An error occurred while updating samples', 'danger');
        }
    });

    // Add sample deletion handler
    document.addEventListener('click', function(e) {
        if (e.target.closest('.delete-sample')) {
            const sampleCard = e.target.closest('.sample-card');
            if (sampleCard && confirm('Are you sure you want to delete this sample?')) {
                const sampleId = sampleCard.dataset.sampleId;
                if (sampleId) {
                    deletedSamples = deletedSamples || [];
                    deletedSamples.push(sampleId);
                }
                sampleCard.classList.add('to-be-deleted');
                sampleCard.style.opacity = '0.5';
            }
        }
    });

    // Save Documents
    document.getElementById('saveDocumentsBtn')?.addEventListener('click', async function() {
        const formData = {
            turtle_id: document.querySelector('[name="turtle_id"]').value,
            documents: [],
            deletedDocuments: deletedDocuments || []
        };

        // Collect all non-deleted document data
        document.querySelectorAll('#documentContainer .document-card:not(.to-be-deleted)').forEach(card => {
            const documentData = {};
            card.querySelectorAll('input').forEach(element => {
                documentData[element.name] = element.value;
            });
            formData.documents.push(documentData);
        });

        try {
            const response = await fetch('/wamtram2/api/documents-update/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (data.status === 'success') {
                deletedDocuments = [];
                document.querySelectorAll('#documentContainer .document-card.to-be-deleted').forEach(card => {
                    card.remove();
                });
                showAlert('Documents updated successfully!', 'success');
            } else {
                document.querySelectorAll('#documentContainer .document-card.to-be-deleted').forEach(card => {
                    card.classList.remove('to-be-deleted');
                    card.style.opacity = '1';
                });
                showAlert(data.message || 'Error updating documents', 'danger');
            }
        } catch (error) {
            console.error('Save error:', error);
            document.querySelectorAll('#documentContainer .document-card.to-be-deleted').forEach(card => {
                card.classList.remove('to-be-deleted');
                card.style.opacity = '1';
            });
            showAlert('An error occurred while updating documents', 'danger');
        }
    });

    // Add document deletion handler
    document.addEventListener('click', function(e) {
        if (e.target.closest('.delete-document')) {
            const documentCard = e.target.closest('.document-card');
            if (documentCard && confirm('Are you sure you want to delete this document?')) {
                const documentId = documentCard.dataset.documentId;
                if (documentId) {
                    deletedDocuments = deletedDocuments || [];
                    deletedDocuments.push(documentId);
                }
                documentCard.classList.add('to-be-deleted');
                documentCard.style.opacity = '0.5';
            }
        }
    });

    // Load tissue types
    function loadTissueTypes() {
        return JSON.parse(document.getElementById('tissue-types-data').textContent);
    }

    // Load document types
    function loadDocumentTypes() {
        return JSON.parse(document.getElementById('document-types-data').textContent);
    }

});
