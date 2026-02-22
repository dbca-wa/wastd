// Track modified fields globally
let modifiedFields = new Map();

// Initialize change tracking for all form fields
function initializeChangeTracking() {
    $('input, select, textarea').each(function() {
        const $field = $(this);
        const initialValue = $field.val();
        $field.data('original-value', initialValue);
        
        if ($field.hasClass('select2-hidden-accessible')) {
            $field.on('select2:select select2:unselect', function() {
                handleFieldChange($field);
            });
        } else {
            $field.on('change', function() {
                handleFieldChange($field);
            });
        }
    });
}

function handleFieldChange($field) {
    const fieldName = $field.attr('name');
    if (!fieldName) return;
    
    const $label = $(`label[for="${fieldName}"]`).length ? 
                $(`label[for="${fieldName}"]`) : 
                $field.closest('.form-group').find('label');
    
    const originalValue = $field.data('original-value');
    const currentValue = $field.val();
    
    let displayOriginalValue = originalValue;
    let displayCurrentValue = currentValue;
    
    if ($field.hasClass('select2-hidden-accessible')) {
        const $select = $field;
        displayOriginalValue = $select.find(`option[value="${originalValue}"]`).text() || originalValue;
        displayCurrentValue = $select.find('option:selected').text() || currentValue;
    }
    
    if (originalValue !== currentValue) {
        $label.css('background-color', '#fff3cd');
        modifiedFields.set(fieldName, {
            label: $label.text().trim(),
            originalValue: displayOriginalValue || 'empty',
            currentValue: displayCurrentValue || 'empty'
        });
    } else {
        $label.css('background-color', '');
        modifiedFields.delete(fieldName);
    }
}

// Get formatted changes message
function getChangesMessage() {
    if (modifiedFields.size === 0) {
        return 'No changes detected. Do you still want to save?';
    }
    
    let message = 'Save the following changes?\n\n';
    modifiedFields.forEach((change, fieldName) => {
        message += `${change.label}:\n`;
        message += `- From: ${change.originalValue}\n`;
        message += `- To: ${change.currentValue}\n\n`;
    });
    
    return message;
}

// Reset all change tracking
function resetChangeTracking() {
    // Clear all highlights
    $('label').css('background-color', '');
    // Clear tracked changes
    modifiedFields.clear();
    // Update all original values
    $('input, select, textarea').each(function() {
        $(this).data('original-value', $(this).val());
    });
}


// Document ready handler
$(document).ready(function() {
    // Initialize search selects
    initializeSearchSelects();
    
    // Initialize basic dropdowns
    initializeBasicSelects();
    
    // If initialData is defined, set initial form values
    if (typeof initialData !== 'undefined' && initialData) {
        setInitialFormValues();
    }

    // Bind save button click event
    $('#saveButton').on('click', function(e) {
        e.preventDefault();
        handleSave();
    });
});

// Handle save action
function handleSave() {
    // Get changes message and show confirmation dialog
    const confirmMessage = getChangesMessage();
    if (!confirm(confirmMessage)) {
        return;
    }

    showLoading();

    const formData = {
        basic_info: getBasicInfo(),
        tag_info: getTagInfo(),
        measurements: getMeasurements(),
        damage_records: getDamageRecords(),
        recorded_identifications: getIdentifications(),
        location: getLocationInfo()
    };

    // Get CSRF token from the template
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch(submitUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.status === 'success') {
            showSuccessMessage('Save successful!');
            // Reset change tracking after successful save
            resetChangeTracking();
            
            if (data.observation_id) {
                history.pushState({}, '', `/wamtram2/curation/observations-management/${data.observation_id}/`);
            }
        } else {
            showErrorMessage(data.message || 'Save failed, please try again');
        }
    })
    .catch(error => {
        hideLoading();
        showErrorMessage('Error occurred during save: ' + error.message);
    });
}

// Show loading overlay and spinner
function showLoading() {
    $('.loading-spinner').show();
    $('.loading-overlay').show();
}

// Hide loading overlay and spinner
function hideLoading() {
    $('.loading-spinner').hide();
    $('.loading-overlay').hide();
}

// Show success message
function showSuccessMessage(message) {
    const alertHtml = `
        <div class="alert alert-success alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span>
            </button>
        </div>
    `;
    $('#messageContainer').html(alertHtml);
    
    setTimeout(() => {
        $('.alert').alert('close');
    }, 3000);
}

// Show error message
function showErrorMessage(message) {
    const alertHtml = `
        <div class="alert alert-danger alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span>
            </button>
        </div>
    `;
    $('#messageContainer').html(alertHtml);
    
    setTimeout(() => {
        $('.alert').alert('close');
    }, 5000);
}

// Get basic information from form
function getBasicInfo() {
    const observationDateTime = $('[name="observation_date"]').val();
    
    function getSelect2Value(selectName) {
        const $select = $(`select[name="${selectName}"]`);
        const data = $select.select2('data')[0];
        return data ? data.id : null; 
    }

    return {
        observation_id: $('[name="observation_id"]').val(),
        observation_date: observationDateTime,
        alive: $('[name="alive"]').val() || null,
        nesting: $('[name="nesting"]').val() || null,
        clutch_completed: $('[name="clutch_completed"]').val() || null,
        activity_code: $('[name="activity_code"]').val() || null,
        beach_position_code: $('[name="beach_position_code"]').val() || null,
        condition_code: $('[name="condition_code"]').val() || null,
        number_of_eggs: $('[name="number_of_eggs"]').val() || null,
        egg_count_method: $('[name="egg_count_method"]').val() || null,
        datum_code: $('[name="datum_code"]').val() || null,
        
        measurer_person: getSelect2Value('measurer_person'),
        measurer_reporter_person: getSelect2Value('measurer_reporter_person'),
        tagger_person: getSelect2Value('tagger_person'),
        reporter_person: getSelect2Value('reporter_person'),
        place_code: getSelect2Value('place_code'),
        
        comments: $('[name="comments"]').val() || '',
        other_tags: $('[name="other_tags"]').val() || '',
        other_tags_identification_type: $('[name="other_tags_identification_type"]').val() || null,
        
        latitude: $('[name="latitude"]').val() || null,
        longitude: $('[name="longitude"]').val() || null,
        
        date_convention: $('[name="date_convention"]').val() || null
    };
}

// Get tag information from form
function getTagInfo() {
    const tagInfo = {
        recorded_tags: [],
        recorded_pit_tags: []
    };
    
    // Get regular tags
    $('.tag-card').each(function() {
        tagInfo.recorded_tags.push({
            tag_id: $(this).find('[name="tag_id"]').val(),
            tag_side: $(this).find('[name="tag_side"]').val(),
            tag_position: $(this).find('[name="tag_position"]').val(),
            tag_state: $(this).find('[name="tag_state"]').val()
        });
    });
    
    // Get PIT tags
    $('.pit-tag-card').each(function() {
        tagInfo.recorded_pit_tags.push({
            tag_id: $(this).find('[name="pittag_id"]').val(),
            tag_position: $(this).find('[name="pit_tag_position"]').val(),
            tag_state: $(this).find('[name="pit_tag_state"]').val()
        });
    });
    
    return tagInfo;
}

// Get measurements from form
function getMeasurements() {
    const measurements = [];
    $('.measurement-card').each(function() {
        measurements.push({
            measurement_type: $(this).find('[name="measurement_type"]').val(),
            measurement_value: $(this).find('[name="measurement_value"]').val()
        });
    });
    return measurements;
}

// Get damage records from form
function getDamageRecords() {
    const damageRecords = [];
    $('.damage-card').each(function() {
        damageRecords.push({
            body_part: $(this).find('[name="body_part"]').val(),
            damage_code: $(this).find('[name="damage_code"]').val(),
            damage_cause_code: $(this).find('[name="damage_cause_code"]').val(),
            comments: $(this).find('[name="damage_comments"]').val()
        });
    });
    return damageRecords;
}

// Get identifications from form
function getIdentifications() {
    const identifications = [];
    $('.identification-card').each(function() {
        identifications.push({
            turtle_id: $(this).find('[name="turtle_id[]"]').val(),
            identification_type: $(this).find('[name="identification_type[]"]').val(),
            identifier: $(this).find('[name="identifier[]"]').val(),
            comments: $(this).find('[name="identification_comments[]"]').val()
        });
    });
    return identifications;
}

// Get location information from form
function getLocationInfo() {
    return {
        place_code: $('[name="place_code"]').val(),
        datum_code: $('[name="datum_code"]').val(),
        latitude: $('[name="latitude"]').val(),
        longitude: $('[name="longitude"]').val()
    };
}

// Initialize basic select elements
function initializeBasicSelects() {
    const basicSelects = [
        'alive',
        'nesting',
        'activity_code',
        'beach_position_code',
        'condition_code',
        'egg_count_method',
        'datum_code',
        'date_convention',
        'clutch_completed'
    ];

    basicSelects.forEach(selectName => {
        $(`select[name="${selectName}"]`).select2({
            placeholder: 'Select...',
            allowClear: true
        });
    });
}

// Initialize search select elements
function initializeSearchSelects() {
    // Initialize person searches
    initializePersonSearch('measurer_person', 'Search measurer...');
    initializePersonSearch('measurer_reporter_person', 'Search measurer reporter...');
    initializePersonSearch('tagger_person', 'Search tagger...');
    initializePersonSearch('reporter_person', 'Search reporter...');

    // Initialize place search
    initializePlaceSearch();
}

// Initialize person search select with AJAX
function initializePersonSearch(fieldName, placeholder) {
    $(`select[name="${fieldName}"]`).select2({
        ajax: {
            url: searchPersonsUrl,
            dataType: 'json',
            delay: 250,
            data: function(params) {
                return {
                    q: params.term || ''
                };
            },
            processResults: function(data) {
                return {
                    results: data.map(function(item) {
                        return {
                            id: item.person_id,
                            text: `${item.first_name} ${item.surname}`
                        };
                    })
                };
            },
            cache: true
        },
        minimumInputLength: 2,
        placeholder: placeholder,
        allowClear: true
    });
}

// Initialize place search select with AJAX
function initializePlaceSearch() {
    $('select[name="place_code"]').select2({
        ajax: {
            url: searchPlacesUrl,
            dataType: 'json',
            delay: 250,
            data: function(params) {
                return {
                    q: params.term || ''
                };
            },
            processResults: function(data) {
                return {
                    results: data.map(function(item) {
                        return {
                            id: item.place_code,
                            text: item.full_name
                        };
                    })
                };
            },
            cache: true
        },
        minimumInputLength: 2,
        placeholder: 'Search place...',
        allowClear: true
    });
}

// Set all initial form values
function setInitialFormValues() {
    if (initialData) {
        // First set all values
        setBasicFields();
        setTagInfo();
        setMeasurements();
        setDamageRecords();
        setIdentification();
        setScars();
        saveOriginalFormData();
        
        // Then initialize change tracking after all values are set
        setTimeout(() => {
            initializeChangeTracking();
        }, 100);
    }
}

// Set basic form fields
function setBasicFields() {
    if (!initialData || !initialData.basic_info) {
        console.error('No initial data or basic info available');
        return;
    }
    
    const basicInfo = initialData.basic_info;
    console.log('Setting basic fields with:', basicInfo);

    // Set simple fields
    const simpleFields = {
        'observation_id': basicInfo.observation_id,
        'turtle_id': basicInfo.turtle_id,
        'observation_date': basicInfo.observation_date,
        'number_of_eggs': basicInfo.number_of_eggs,
        'latitude': basicInfo.latitude,
        'longitude': basicInfo.longitude,
        'observation_status': basicInfo.observation_status,
        'entered_by': basicInfo.entered_by,
        'place_description': basicInfo.place_description,
        'action_taken': basicInfo.action_taken,
        'comments': basicInfo.comments
    };

    Object.entries(simpleFields).forEach(([field, value]) => {
        const $field = $(`[name="${field}"]`);
        if ($field.length) {
            $field.val(value);
        } else {
            console.warn(`Field not found: ${field}`);
        }
    });

    // Set dropdown fields
    const dropdownFields = {
        'alive': basicInfo.alive,
        'nesting': basicInfo.nesting,
        'clutch_completed': basicInfo.clutch_completed,
        'activity_code': basicInfo.activity_code,
        'beach_position_code': basicInfo.beach_position_code,
        'condition_code': basicInfo.condition_code,
        'egg_count_method': basicInfo.egg_count_method,
        'datum_code': basicInfo.datum_code,
        'date_convention': basicInfo.date_convention
    };

    Object.entries(dropdownFields).forEach(([field, value]) => {
        const $select = $(`select[name="${field}"]`);
        if ($select.length) {
            if (value) {
                $select.val(value).trigger('change');
            }
        } else {
            console.warn(`Dropdown not found: ${field}`);
        }
    });

    // Set Select2 fields
    const select2Fields = {
        'measurer_person': basicInfo.measurer_person,
        'measurer_reporter_person': basicInfo.measurer_reporter_person,
        'tagger_person': basicInfo.tagger_person,
        'reporter_person': basicInfo.reporter_person,
        'place_code': basicInfo.place_code
    };

    // Set Select2 fields
    Object.entries(select2Fields).forEach(([field, data]) => {
        if (data && data.id) {
            const $select = $(`select[name="${field}"]`);
            if ($select.length) {
                // Create new option
                const option = new Option(data.text, data.id, true, true);
                $select.append(option).trigger('change');
            } else {
                console.warn(`Select2 field not found: ${field}`);
            }
        }
    });

    // Set turtle detail link
    const turtleDetailLink = document.getElementById('turtleDetailLink');
    if (turtleDetailLink && basicInfo.turtle_id) {
        turtleDetailLink.href = `${turtleDetailUrlTemplate}${basicInfo.turtle_id}/`;
    }
}

// Generate tag HTML template
function generateTagHtml(tag = {}) {
    const cardId = 'tag-card-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    return `
        <div class="card mb-3 tag-card" id="${cardId}">
            <div class="card-body">
                <div class="form-row">
                    <div class="col-md-2">
                        <div class="form-group">
                            <label>Tag ID</label>
                            <input type="text" class="form-control" name="tag_id" value="${tag.tag_id || ''}" >
                        </div>
                    </div>
                    <div class="col-md-2">
                        <div class="form-group">
                            <label>Side</label>
                            <select class="form-control select2" name="tag_side">
                                <option value="">Select Side</option>
                                <option value="L" ${tag.tag_side === 'L' ? 'selected' : ''}>Left</option>
                                <option value="R" ${tag.tag_side === 'R' ? 'selected' : ''}>Right</option>
                            </select>
                        </div>
                    </div>
                    <div class="col-md-2">
                        <div class="form-group">
                            <label>Position</label>
                            <select class="form-control select2" name="tag_position">
                                <option value="">Select Position</option>
                                <option value="1" ${String(tag.tag_position) === '1' ? 'selected' : ''}>1</option>
                                <option value="2" ${String(tag.tag_position) === '2' ? 'selected' : ''}>2</option>
                                <option value="3" ${String(tag.tag_position) === '3' ? 'selected' : ''}>3</option>
                            </select>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="form-group">
                            <label>State</label>
                            <select class="form-control select2" name="tag_state">
                                <option value="">Select State</option>
                                ${tagStateChoices.map(state => `
                                    <option value="${state.tag_state}" ${tag.tag_state === state.tag_state ? 'selected' : ''}>
                                        ${state.description}
                                    </option>
                                `).join('')}
                            </select>
                        </div>
                    </div>
                    <div class="col-md-2">
                        <div class="form-group">
                            <label>Barnacles</label>
                            <div class="form-control border-0 d-flex align-items-center">
                                <input type="checkbox" class="form-control" 
                                    name="barnacles" 
                                    id="barnacles-${cardId}" 
                                    style="width: 15px; height: 15px; margin: 0;"
                                    ${tag.barnacles ? 'checked' : ''}>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-1">
                        <div class="form-group">
                            <label>&nbsp;</label>
                            <button type="button" class="btn btn-danger btn-block">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Generate PIT tag HTML template
function generatePitTagHtml(tag = {}) {
    const cardId = 'pit-tag-card-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    return `
        <div class="card mb-3 pit-tag-card" id="${cardId}">
            <div class="card-body">
                <div class="form-row">
                    <div class="col-md-3">
                        <div class="form-group">
                            <label>PIT Tag ID</label>
                            <input type="text" class="form-control" name="pittag_id" value="${tag.tag_id || ''}" >
                        </div>
                    </div>
                    <div class="col-md-2">
                        <div class="form-group">
                            <label>Side</label>
                            <select class="form-control" name="pit_tag_position">
                                <option value="">Select Position</option>
                                <option value="LF" ${tag.tag_position === 'LF' ? 'selected' : ''}>Left</option>
                                <option value="RF" ${tag.tag_position === 'RF' ? 'selected' : ''}>Right</option>
                            </select>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="form-group">
                            <label>State</label>
                            <select class="form-control" name="pit_tag_state">
                                <option value="">Select...</option>
                                ${pitTagStateChoices.map(state => `
                                    <option value="${state.pit_tag_state}" ${tag.tag_state === state.pit_tag_state ? 'selected' : ''}>
                                        ${state.description}
                                    </option>
                                `).join('')}
                            </select>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="form-group">
                            <label>Comments</label>
                            <input type="text" class="form-control" name="comments" value="${tag.comments || ''}" >
                        </div>
                    </div>
                    <div class="col-md-1">
                        <div class="form-group">
                            <label>&nbsp;</label>
                            <button type="button" class="btn btn-danger btn-block">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Generate identification HTML template
function generateIdentificationHtml(identification = {}) {
    const cardId = 'identification-card-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    return `
        <div class="card mb-3 identification-card" id="${cardId}" 
            data-identification-id="${identification.recorded_identification_id || ''}">
            <div class="card-body">
                <div class="form-row">
                    <div class="col-md-4">
                        <div class="form-group">
                            <label>Identification Type</label>
                            <select class="form-control" name="identification_type">
                                <option value="">Select...</option>
                                ${initialData.identification_types.map(type => `
                                    <option value="${type.identification_type}" 
                                        ${identification.identification_type === type.identification_type ? 'selected' : ''}>
                                        ${type.description}
                                    </option>
                                `).join('')}
                            </select>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="form-group">
                            <label>Identifier</label>
                            <input type="text" class="form-control" name="identifier" 
                                value="${identification.identifier || ''}">
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="form-group">
                            <label>Comments</label>
                            <input type="text" class="form-control" name="comments" 
                                value="${identification.comments || ''}">
                        </div>
                    </div>
                    <div class="col-md-1">
                        <div class="form-group">
                            <label>&nbsp;</label>
                            <button type="button" class="btn btn-danger btn-block">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}


// Generate measurement HTML template
function generateMeasurementHtml(measurement = {}) {
    const cardId = 'measurement-card-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    return `
        <div class="card mb-3 measurement-card" id="${cardId}" 
            data-measurement-id="${measurement.id || ''}">
            <div class="card-body">
                <div class="form-row">
                    <div class="col-md-5">
                        <div class="form-group">
                            <label>Measurement Type</label>
                            <select class="form-control" name="measurement_type">
                                <option value="">Select...</option>
                                ${measurementTypeChoices.map(type => `
                                    <option value="${type.measurement_type}" 
                                        ${measurement.measurement_type === type.measurement_type ? 'selected' : ''}>
                                        ${type.description}
                                    </option>
                                `).join('')}
                            </select>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="form-group">
                            <label>Value</label>
                            <input type="number" class="form-control" name="measurement_value" 
                                value="${measurement.measurement_value || ''}" step="0.1">
                        </div>
                    </div>
                    <div class="col-md-2">
                        <div class="form-group">
                            <label>Comments</label>
                            <input type="text" class="form-control" name="comments" 
                                value="${measurement.comments || ''}">
                        </div>
                    </div>
                    <div class="col-md-1">
                        <div class="form-group">
                            <label>&nbsp;</label>
                            <button type="button" class="btn btn-danger btn-block">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}


// Set tag info
function setTagInfo() {
    // Flipper tags
    const tagContainer = document.getElementById('tagContainer');
    
    if (!tagContainer) {
        console.error('Tag container not found!');
        return;
    }

    if (!initialData.tag_info?.recorded_tags) {
        console.error('No tag data found!');
        return;
    }

    tagContainer.innerHTML = '';
    
    if (initialData.tag_info.recorded_tags.length === 0) {
        tagContainer.innerHTML = '<p class="text-muted">No recorded flipper tags found</p>';
    } else {
        initialData.tag_info.recorded_tags.forEach(tag => {
            tagContainer.insertAdjacentHTML('beforeend', generateTagHtml(tag));
        });
    }

    // PIT tags
    const pitTagContainer = document.getElementById('pitTagContainer');
    if (pitTagContainer) {
        const recordedPitTags = initialData.tag_info?.recorded_pit_tags ?? [];
        pitTagContainer.innerHTML = '';
        if (recordedPitTags.length === 0) {
            pitTagContainer.innerHTML = '<p class="text-muted">No recorded PIT tags found</p>';
        } else {
            recordedPitTags.forEach(pitTag => {
                pitTagContainer.insertAdjacentHTML('beforeend', generatePitTagHtml(pitTag));
            });
        }
    }

}


// Set measurements data
function setMeasurements() {
    const measurementContainer = document.getElementById('measurementContainer');
    if (!measurementContainer || !initialData.measurements) return;
    
    measurementContainer.innerHTML = '';

    if (initialData.measurements.length === 0) {
        measurementContainer.innerHTML = '<p class="text-muted">No measurements found</p>';
        return;
    }

    initialData.measurements.forEach(measurement => {
        measurementContainer.insertAdjacentHTML('beforeend', generateMeasurementHtml(measurement));
    });
}

// Set damage records
function setDamageRecords() {
    const damageContainer = document.getElementById('damageContainer');
    if (!damageContainer || !initialData.damage_records) return;
    
    damageContainer.innerHTML = '';

    if (initialData.damage_records.length === 0) {
        damageContainer.innerHTML = '<p class="text-muted">No damage records found</p>';
        return;
    }

    initialData.damage_records.forEach(damage => {
        damageContainer.insertAdjacentHTML('beforeend', generateDamageHtml(damage));
    });
}


// Set other identification data
function setIdentification() {
    const container = document.getElementById('otherIdContainer');
    if (!container) return;
    
    container.innerHTML = '';

    // Check if there are any recorded identifications
    if (!initialData.recorded_identifications || initialData.recorded_identifications.length === 0) {
        container.innerHTML = '<p class="text-muted">No recorded identifications found</p>';
        return;
    }

    // Display recorded identifications
    initialData.recorded_identifications.forEach(identification => {
        container.insertAdjacentHTML('beforeend', generateIdentificationHtml(identification));
    });

}


function setScars() {
        const container = document.getElementById('scarsContainer');
        if (!container || !initialData.scars) return;
    
        const scarsHtml = `
            <div class="form-row">
                <div class="col-md-6">
                    <div class="card mb-3">
                        <div class="card-body">
                            <h5 class="card-title">Left Side</h5>
                            <div class="form-check">
                                <input type="checkbox" class="form-check-input" name="scars_left" 
                                    ${initialData.scars.scars_left ? 'checked' : ''}>
                                <label class="form-check-label">Scars Left</label>
                            </div>
                            <div class="form-check">
                                <input type="checkbox" class="form-check-input" name="scars_left_scale_1" 
                                    ${initialData.scars.scars_left_scale_1 ? 'checked' : ''}>
                                <label class="form-check-label">Scale 1</label>
                            </div>
                            <div class="form-check">
                                <input type="checkbox" class="form-check-input" name="scars_left_scale_2" 
                                    ${initialData.scars.scars_left_scale_2 ? 'checked' : ''}>
                                <label class="form-check-label">Scale 2</label>
                            </div>
                            <div class="form-check">
                                <input type="checkbox" class="form-check-input" name="scars_left_scale_3" 
                                    ${initialData.scars.scars_left_scale_3 ? 'checked' : ''}>
                                <label class="form-check-label">Scale 3</label>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card mb-3">
                        <div class="card-body">
                            <h5 class="card-title">Right Side</h5>
                            <div class="form-check">
                                <input type="checkbox" class="form-check-input" name="scars_right" 
                                    ${initialData.scars.scars_right ? 'checked' : ''}>
                                <label class="form-check-label">Scars Right</label>
                            </div>
                            <div class="form-check">
                                <input type="checkbox" class="form-check-input" name="scars_right_scale_1" 
                                    ${initialData.scars.scars_right_scale_1 ? 'checked' : ''}>
                                <label class="form-check-label">Scale 1</label>
                            </div>
                            <div class="form-check">
                                <input type="checkbox" class="form-check-input" name="scars_right_scale_2" 
                                    ${initialData.scars.scars_right_scale_2 ? 'checked' : ''}>
                                <label class="form-check-label">Scale 2</label>
                            </div>
                            <div class="form-check">
                                <input type="checkbox" class="form-check-input" name="scars_right_scale_3" 
                                    ${initialData.scars.scars_right_scale_3 ? 'checked' : ''}>
                                <label class="form-check-label">Scale 3</label>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="form-row">
                <div class="col-12">
                    <div class="form-check">
                        <input type="checkbox" class="form-check-input" name="tag_scar_not_checked" 
                            ${initialData.scars.tag_scar_not_checked ? 'checked' : ''}>
                        <label class="form-check-label">Tag Scar Not Checked</label>
                    </div>
                </div>
            </div>
        `;
        container.innerHTML = scarsHtml;
}
    

function saveOriginalFormData() {
    originalFormData = {};
    const formElements = document.querySelectorAll('input, select, textarea');
    formElements.forEach(element => {
        
        originalFormData[element.name] = element.value;
    });
}


function getFormChanges() {
    const changes = {};
    const currentFormData = {};
    const formElements = document.querySelectorAll('input, select, textarea');
    
    formElements.forEach(element => {
        const currentValue = element.value;
        const originalValue = originalFormData[element.name];
    
        
        if (currentValue !== originalValue) {
            const label = element.previousElementSibling?.textContent || element.name;
            changes[label] = {
                old: originalValue,
                new: currentValue
            };
        }
    });
    
    return changes;
}

// Add global variable to track deleted tags
let deletedTags = new Set();


// Add new tag
function addFlipperTag() {
    const tagContainer = document.getElementById('tagContainer');
    
    if (tagContainer.innerHTML.includes('No flipper tags found')) {
        tagContainer.innerHTML = '';
    }
    
    tagContainer.insertAdjacentHTML('beforeend', generateTagHtml());
    
}

// Handle delete tag
function deleteTag(event) {
    const tagCard = event.target.closest('.tag-card');
    const tagId = tagCard.querySelector('[name="tag_id"]').value;
    
    if (tagCard.classList.contains('deleted')) {
        // Can't delete the tag
        tagCard.classList.remove('deleted');
        deletedTags.delete(tagId);
    } else {
        // Note the tag is deleted
        tagCard.classList.add('deleted');
        if (tagId) {
            deletedTags.add(tagId);
        }
    }
}

// Save tag changes
async function saveTagChanges() {
    const newTags = [];
    const modifiedTags = [];
    
    document.querySelectorAll('.tag-card:not(.deleted)').forEach(card => {
        const tagData = {
            tag_id: card.querySelector('[name="tag_id"]').value.trim(),
            tag_side: card.querySelector('[name="tag_side"]').value || null,
            tag_position: card.querySelector('[name="tag_position"]').value || null,
            tag_state: card.querySelector('[name="tag_state"]').value || null,
            barnacles: Boolean(card.querySelector('[name="barnacles"]').checked)
        };
        
        const originalTag = initialData.tag_info.recorded_tags.find(
            tag => tag.tag_id === tagData.tag_id
        );
        
        // For existing tags, check if there are actual changes
        if (originalTag) {
            const originalTag = initialData.tag_info.recorded_tags.find(
                tag => tag.tag_id === tagData.tag_id
            );
            
            if (originalTag) {
                const originalValues = {
                    tag_side: originalTag.tag_side || null,
                    tag_position: originalTag.tag_position || null,
                    tag_state: originalTag.tag_state || null,
                    barnacles: !!originalTag.barnacles
                };

                const hasChanges = (
                    tagData.tag_side !== originalValues.tag_side ||
                    String(tagData.tag_position) !== String(originalTag.tag_position) ||
                    tagData.tag_state !== originalValues.tag_state ||
                    tagData.barnacles !== originalValues.barnacles
                );

                
                if (hasChanges) {
                    modifiedTags.push(tagData);
                }
            }
        } else {
            newTags.push(tagData);
        }
    });

    // If no changes, return early
    if (newTags.length === 0 && modifiedTags.length === 0 && deletedTags.size === 0) {
        alert('No changes to save');
        return;
    }

    // Create confirmation message
    let confirmMessage = 'Please confirm the following changes:\n\n';
    
    if (newTags.length > 0) {
        confirmMessage += 'New Tags:\n';
        newTags.forEach(tag => {
            confirmMessage += `- Tag ID: ${tag.tag_id || 'N/A'}\n`;
            if (tag.tag_side) confirmMessage += `  Side: ${tag.tag_side}\n`;
            if (tag.tag_position) confirmMessage += `  Position: ${tag.tag_position}\n`;
            if (tag.tag_state) confirmMessage += `  State: ${tag.tag_state}\n`;
            if (tag.barnacles) confirmMessage += `  Barnacles: Yes\n`;
        });
        confirmMessage += '\n';
    }

    if (modifiedTags.length > 0) {
        confirmMessage += 'Modified Tags:\n';
        modifiedTags.forEach(tag => {
            const originalTag = initialData.tag_info.recorded_tags.find(t => t.tag_id === tag.tag_id);
            confirmMessage += `- Tag ID: ${tag.tag_id}\n`;
            if (tag.tag_side !== originalTag.tag_side) {
                confirmMessage += `  Side: ${originalTag.tag_side || 'N/A'} → ${tag.tag_side || 'N/A'}\n`;
            }
            if (String(tag.tag_position) !== String(originalTag.tag_position)) {
                confirmMessage += `  Position: ${originalTag.tag_position || 'N/A'} → ${tag.tag_position || 'N/A'}\n`;
            }
            if (tag.tag_state !== originalTag.tag_state) {
                confirmMessage += `  State: ${originalTag.tag_state || 'N/A'} → ${tag.tag_state || 'N/A'}\n`;
            }
            if (tag.barnacles !== !!originalTag.barnacles) {
                confirmMessage += `  Barnacles: ${originalTag.barnacles ? 'Yes' : 'No'} → ${tag.barnacles ? 'Yes' : 'No'}\n`;
            }
        });
        confirmMessage += '\n';
    }

    if (deletedTags.size > 0) {
        confirmMessage += 'Deleted Tags:\n';
        deletedTags.forEach(tagId => {
            confirmMessage += `- Tag ID: ${tagId}\n`;
        });
    }

    if (!confirm(confirmMessage)) {
        return;
    }

    try {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        const response = await fetch('/wamtram2/api/recorded-tags/update/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                observation_id: initialData.basic_info.observation_id,
                recorded_tags: [...newTags, ...modifiedTags],
                deleted_tags: Array.from(deletedTags)
            })
        });

        const data = await response.json();
        if (data.status === 'success') {
            alert('Tags updated successfully!');
            location.reload();
        } else {
            alert(`Error: ${data.message}`);
        }
    } catch (error) {
        alert(`Save failed: ${error.message}`);
    }
}

// Add new PIT tag
function addPitTag() {
    const pitTagContainer = document.getElementById('pitTagContainer');
    
    if (pitTagContainer.innerHTML.includes('No recorded PIT tags found')) {
        pitTagContainer.innerHTML = '';
    }
    
    pitTagContainer.insertAdjacentHTML('beforeend', generatePitTagHtml());
}

// Delete PIT tag
function deletePitTag(event) {
    const tagCard = event.target.closest('.pit-tag-card');
    const tagId = tagCard.querySelector('[name="pittag_id"]').value;
    
    if (tagCard.classList.contains('deleted')) {
        // Undelete the tag
        tagCard.classList.remove('deleted');
        deletedTags.delete(tagId);
    } else {
        // Mark the tag as deleted
        tagCard.classList.add('deleted');
        if (tagId) {
            deletedTags.add(tagId);
        }
    }
}

// Save PIT tag changes
async function savePitTagChanges() {
    const newTags = [];
    const modifiedTags = [];
    
    document.querySelectorAll('.pit-tag-card:not(.deleted)').forEach(card => {
        const tagData = {
            pittag_id: card.querySelector('[name="pittag_id"]').value.trim(),
            pit_tag_position: card.querySelector('[name="pit_tag_position"]').value || null,
            pit_tag_state: card.querySelector('[name="pit_tag_state"]').value || null,
            comments: card.querySelector('[name="comments"]').value.trim()
        };
        
        const originalTag = initialData.tag_info.recorded_pit_tags.find(
            tag => tag.tag_id === tagData.pittag_id
        );
        
        if (originalTag) {
            const hasChanges = (
                tagData.pit_tag_position !== originalTag.tag_position ||
                tagData.pit_tag_state !== originalTag.tag_state ||
                tagData.comments !== originalTag.comments
            );
            
            if (hasChanges) {
                modifiedTags.push(tagData);
            }
        } else {
            newTags.push(tagData);
        }
    });

    if (newTags.length === 0 && modifiedTags.length === 0 && deletedTags.size === 0) {
        alert('No changes to save');
        return;
    }

    // Create confirmation message
    let confirmMessage = 'Please confirm the following changes:\n\n';
    
    if (newTags.length > 0) {
        confirmMessage += 'New PIT Tags:\n';
        newTags.forEach(tag => {
            confirmMessage += `- Tag ID: ${tag.pittag_id}\n`;
            if (tag.pit_tag_position) confirmMessage += `  Position: ${tag.pit_tag_position}\n`;
            if (tag.pit_tag_state) confirmMessage += `  State: ${tag.pit_tag_state}\n`;
            if (tag.comments) confirmMessage += `  Comments: ${tag.comments}\n`;
        });
    }

    if (modifiedTags.length > 0) {
        confirmMessage += '\nModified PIT Tags:\n';
        modifiedTags.forEach(tag => {
            const originalTag = initialData.tag_info.recorded_pit_tags.find(t => t.tag_id === tag.pittag_id);
            confirmMessage += `- Tag ID: ${tag.pittag_id}\n`;
            
            if (tag.pit_tag_position !== originalTag.tag_position) {
                confirmMessage += `  Position: ${originalTag.tag_position || 'N/A'} → ${tag.pit_tag_position || 'N/A'}\n`;
            }
            
            if (tag.pit_tag_state !== originalTag.tag_state) {
                confirmMessage += `  State: ${originalTag.tag_state || 'N/A'} → ${tag.pit_tag_state || 'N/A'}\n`;
            }
            
            if (tag.comments !== originalTag.comments) {
                confirmMessage += `  Comments: ${originalTag.comments || 'N/A'} → ${tag.comments || 'N/A'}\n`;
            }
        });
        confirmMessage += '\n';
    }

    if (deletedTags.size > 0) {
        confirmMessage += '\nDeleted PIT Tags:\n';
        deletedTags.forEach(tagId => {
            confirmMessage += `- Tag ID: ${tagId}\n`;
        });
    }

    if (!confirm(confirmMessage)) {
        return;
    }
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    try {
        const response = await fetch('/wamtram2/api/recorded-pit-tags/update/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                observation_id: initialData.basic_info.observation_id,
                recorded_pit_tags: [...newTags, ...modifiedTags],
                deleted_tags: Array.from(deletedTags)
            })
        });

        const result = await response.json();
        if (result.status === 'success') {
            alert('PIT tags updated successfully');
            location.reload();
        } else {
            throw new Error(result.message);
        }
    } catch (error) {
        alert(`Save failed: ${error.message}`);
    }
}

// Add new identification
function addIdentification() {
    const container = document.getElementById('otherIdContainer');
    if (!container) return;
    
    // Remove "No recorded identifications" message if it exists
    if (container.querySelector('.text-muted')) {
        container.innerHTML = '';
    }
    
    // Add new empty identification card
    container.insertAdjacentHTML('beforeend', generateIdentificationHtml({}));
    
}

// Save identification changes
function saveIdentificationChanges() {
    const newIdentifications = [];
    const modifiedIdentifications = [];
    const deletedIdentifications = [];
    
    // Collect current identifications
    document.querySelectorAll('.identification-card:not(.deleted)').forEach(card => {
        const identificationData = {
            identification_type: card.querySelector('[name="identification_type"]').value,
            identifier: card.querySelector('[name="identifier"]').value.trim(),
            comments: card.querySelector('[name="comments"]').value.trim(),
            recorded_identification_id: card.dataset.identificationId || null
        };
        
        if (identificationData.recorded_identification_id) {
            const originalId = initialData.recorded_identifications.find(
                id => id.recorded_identification_id === parseInt(identificationData.recorded_identification_id)
            );
            
            if (originalId) {
                const hasChanges = (
                    String(identificationData.identification_type).trim() !== String(originalId.identification_type).trim() ||
                    String(identificationData.identifier).trim() !== String(originalId.identifier).trim() ||
                    String(identificationData.comments).trim() !== String(originalId.comments).trim()
                );
                
                if (hasChanges) {
            
                    if (
                        String(identificationData.identification_type).trim() !== String(originalId.identification_type).trim() ||
                        String(identificationData.identifier).trim() !== String(originalId.identifier).trim() ||
                        String(identificationData.comments).trim() !== String(originalId.comments).trim()
                    ) {
                        modifiedIdentifications.push({
                            ...identificationData,
                            original: originalId
                        });
                    }
                }
            }
        } else {
            
            newIdentifications.push(identificationData);
        }
    });

    // Collect deleted identifications
    document.querySelectorAll('.identification-card.deleted').forEach(card => {
        const id = card.dataset.identificationId;
        if (id) {
            deletedIdentifications.push(id);
        }
    });

    if (newIdentifications.length === 0 && modifiedIdentifications.length === 0 && deletedIdentifications.length === 0) {
        alert('No changes to save');
        return;
    }

    // Create confirmation message
    let confirmMessage = 'Please confirm the following changes:\n\n';
    
    if (newIdentifications.length > 0) {
        confirmMessage += 'New Identifications:\n';
        newIdentifications.forEach(id => {
            const typeDescription = initialData.identification_types.find(
                type => type.identification_type === id.identification_type
            )?.description || id.identification_type;
            
            confirmMessage += `- Type: ${typeDescription}\n`;
            if (id.identifier) confirmMessage += `  Identifier: ${id.identifier}\n`;
            if (id.comments) confirmMessage += `  Comments: ${id.comments}\n`;
        });
    }

    if (modifiedIdentifications.length > 0) {
        confirmMessage += '\nModified Identifications:\n';
        modifiedIdentifications.forEach(id => {
            const typeDescription = initialData.identification_types.find(
                type => String(type.identification_type).trim() === String(id.identification_type).trim()
            )?.description || id.identification_type;
            
            const originalTypeDescription = initialData.identification_types.find(
                type => String(type.identification_type).trim() === String(id.original.identification_type).trim()
            )?.description || id.original.identification_type;

            if (String(id.identification_type).trim() !== String(id.original.identification_type).trim()) {
                confirmMessage += `- Type: ${originalTypeDescription} → ${typeDescription}\n`;
            } else {
                confirmMessage += `- Type: ${typeDescription}\n`;
            }
            
            if (String(id.identifier).trim() !== String(id.original.identifier).trim()) {
                confirmMessage += `  Identifier: ${id.original.identifier || 'N/A'} → ${id.identifier || 'N/A'}\n`;
            }
            if (String(id.comments).trim() !== String(id.original.comments).trim()) {
                confirmMessage += `  Comments: ${id.original.comments || 'N/A'} → ${id.comments || 'N/A'}\n`;
            }
        });
    }

    if (deletedIdentifications.length > 0) {
        confirmMessage += '\nDeleted Identifications:\n';
        deletedIdentifications.forEach(id => {
            const originalId = initialData.recorded_identifications.find(
                ident => ident.recorded_identification_id === parseInt(id)
            );
            const typeDescription = originalId ? 
                initialData.identification_types.find(
                    type => type.identification_type === originalId.identification_type
                )?.description || originalId.identification_type 
                : 'Unknown';
            
            confirmMessage += `- ID: ${id} (${typeDescription})\n`;
            if (originalId?.identifier) confirmMessage += `  Identifier: ${originalId.identifier}\n`;
            if (originalId?.comments) confirmMessage += `  Comments: ${originalId.comments}\n`;
        });
    }

    if (!confirm(confirmMessage)) {
        return;
    }

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Send data to server
    fetch('/wamtram2/api/recorded-identifications/update/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            observation_id: initialData.basic_info.observation_id,
            recorded_identifications: [...newIdentifications, ...modifiedIdentifications],
            deleted_identifications: deletedIdentifications
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Identifications updated successfully');
            location.reload();
        } else {
            throw new Error(data.message);
        }
    })
    .catch(error => {
        alert(`Save failed: ${error.message}`);
    });
}

// Initialize deletedIdentifications set
let deletedIdentifications = new Set();

// Delete identification
function deleteIdentification(event) {
    const identificationCard = event.target.closest('.identification-card');
    const identificationId = identificationCard.dataset.identificationId;
    if (identificationCard.classList.contains('deleted')) {
        identificationCard.classList.remove('deleted');
        deletedIdentifications.delete(identificationId);
    } else {
        identificationCard.classList.add('deleted');
        if (identificationId) {
            deletedIdentifications.add(identificationId);
        }
    }

}

// Event listeners setup
document.addEventListener('DOMContentLoaded', function() {
    // Add Flipper Tag button
    document.getElementById('addFlipperTagBtn').addEventListener('click', addFlipperTag);
    
    // Delete button (using event delegation)
    document.getElementById('tagContainer').addEventListener('click', function(e) {
        if (e.target.closest('.btn-danger')) {
            deleteTag(e);
        }
    });
    
    // Save button
    document.getElementById('saveTagsBtn').addEventListener('click', saveTagChanges);

    // PIT Tag buttons
    const addPitTagBtn = document.getElementById('addPitTagBtn');
    if (addPitTagBtn) {
        addPitTagBtn.addEventListener('click', addPitTag);
    }
    
    // Delete PIT tag (using event delegation)
    const pitTagContainer = document.getElementById('pitTagContainer');
    if (pitTagContainer) {
        pitTagContainer.addEventListener('click', function(e) {
            if (e.target.closest('.btn-danger')) {
                deletePitTag(e);
            }
        });
    }
    
    // Save PIT Tags button
    const savePitTagsBtn = document.getElementById('savePitTagsBtn');
    if (savePitTagsBtn) {
        savePitTagsBtn.addEventListener('click', savePitTagChanges);
    }

    // Add Identification button
    const addIdentificationBtn = document.getElementById('addIdentificationBtn');
    if (addIdentificationBtn) {
        addIdentificationBtn.addEventListener('click', addIdentification);
    }
    
    // Save Identifications button
    const saveIdentificationsBtn = document.getElementById('saveIdentificationsBtn');
    if (saveIdentificationsBtn) {
        saveIdentificationsBtn.addEventListener('click', saveIdentificationChanges);
    }
    
    // Delete identification button handler
    const otherIdContainer = document.getElementById('otherIdContainer');
    
    if (otherIdContainer) {
        otherIdContainer.addEventListener('click', function(e) {
            
            if (e.target.closest('.btn-danger')) {
                deleteIdentification(e);
            }
        });
    }

    // Measurements buttons
    const addMeasurementBtn = document.getElementById('addMeasurementBtn');
    if (addMeasurementBtn) {
        addMeasurementBtn.addEventListener('click', addMeasurement);
    }
    
    // Delete measurement (using event delegation)
    const measurementContainer = document.getElementById('measurementContainer');
    if (measurementContainer) {
        measurementContainer.addEventListener('click', function(e) {
            const deleteBtn = e.target.closest('.btn-danger');
            
            if (deleteBtn) {
                deleteMeasurement(e);
            }
        });
    }
    
    // Save Measurements button
    const saveMeasurementsBtn = document.getElementById('saveMeasurementsBtn');
    if (saveMeasurementsBtn) {
        saveMeasurementsBtn.addEventListener('click', saveMeasurementChanges);
    }

        // Damage buttons
        const addDamageBtn = document.getElementById('addDamageBtn');
        if (addDamageBtn) {
            addDamageBtn.addEventListener('click', addDamage);
        }
        
        // Delete damage (using event delegation)
        const damageContainer = document.getElementById('damageContainer');
        if (damageContainer) {
            damageContainer.addEventListener('click', function(e) {
                if (e.target.closest('.btn-danger')) {
                    deleteDamage(e);
                }
            });
        }
        
        // Save Damage button
        const saveDamageBtn = document.getElementById('saveDamageBtn');
        if (saveDamageBtn) {
            saveDamageBtn.addEventListener('click', saveDamageChanges);
        }
});

// Add global variable to track deleted measurements
let deletedMeasurements = new Set();

// Add new measurement
function addMeasurement() {
    const measurementContainer = document.getElementById('measurementContainer');
    
    if (measurementContainer.innerHTML.includes('No measurements found')) {
        measurementContainer.innerHTML = '';
    }
    
    measurementContainer.insertAdjacentHTML('beforeend', generateMeasurementHtml());
}

// Delete measurement
function deleteMeasurement(event) {
    const measurementCard = event.target.closest('.measurement-card');
    
    const measurementId = measurementCard.dataset.measurementId;
    
    if (measurementCard.classList.contains('deleted')) {
        measurementCard.classList.remove('deleted');
        deletedMeasurements.delete(measurementId);
    } else {
        measurementCard.classList.add('deleted');
        if (measurementId) {
            deletedMeasurements.add(measurementId);
        }
    }
}

// Save measurement changes
async function saveMeasurementChanges() {
    const newMeasurements = [];
    const modifiedMeasurements = [];
    
    document.querySelectorAll('.measurement-card:not(.deleted)').forEach(card => {
        const measurementType = card.querySelector('[name="measurement_type"]').value;
        let measurementValue = card.querySelector('[name="measurement_value"]').value;
        const comments = card.querySelector('[name="comments"]').value.trim();
        
        if (measurementType.endsWith('(mm)') || measurementType.endsWith('(g)')) {
            measurementValue = parseInt(measurementValue);
        } else if (measurementType.endsWith('(kg)')) {
            measurementValue = parseFloat(measurementValue).toFixed(3);
        }

        const measurementData = {
            measurement_type: String(measurementType),
            measurement_value: measurementValue,
            comments: comments,
            id: card.dataset.measurementId || null
        };
        
        if (measurementData.id) {
            const originalMeasurement = initialData.measurements.find(
                m => m.id === parseInt(measurementData.id)
            );
            
            if (originalMeasurement) {
                let originalValue = originalMeasurement.measurement_value;
                if (originalMeasurement.measurement_type.endsWith('(mm)') || 
                    originalMeasurement.measurement_type.endsWith('(g)')) {
                    originalValue = parseInt(originalValue);
                } else if (originalMeasurement.measurement_type.endsWith('(kg)')) {
                    originalValue = parseFloat(originalValue).toFixed(3);
                }

                // 分别检查每个字段的变化
                const typeChanged = measurementData.measurement_type !== String(originalMeasurement.measurement_type);
                const valueChanged = String(measurementData.measurement_value) !== String(originalValue);
                const commentsChanged = measurementData.comments !== (originalMeasurement.comments || '');

                // 只有在真正有变化时才添加到修改列表
                if (typeChanged || valueChanged || commentsChanged) {
                    const changes = {
                        ...measurementData,
                        original: originalMeasurement,
                        changedFields: {
                            type: typeChanged,
                            value: valueChanged,
                            comments: commentsChanged
                        }
                    };
                    modifiedMeasurements.push(changes);
                }
            }
        } else {
            newMeasurements.push(measurementData);
        }
    });

    // If no changes, return early
    if (newMeasurements.length === 0 && modifiedMeasurements.length === 0 && deletedMeasurements.size === 0) {
        alert('No changes to save');
        return;
    }

    // Create confirmation message
    let confirmMessage = 'Please confirm the following changes:\n\n';
    
    if (newMeasurements.length > 0) {
        confirmMessage += 'New Measurements:\n';
        newMeasurements.forEach(measurement => {
            const typeDescription = measurementTypeChoices.find(
                type => type.measurement_type === measurement.measurement_type
            )?.description || measurement.measurement_type;
            
            confirmMessage += `- Type: ${typeDescription}\n`;
            confirmMessage += `  Value: ${measurement.measurement_value}\n`;
            if (measurement.comments) confirmMessage += `  Comments: ${measurement.comments}\n`;
        });
        confirmMessage += '\n';
    }

    if (modifiedMeasurements.length > 0) {
        confirmMessage += 'Modified Measurements:\n';
        modifiedMeasurements.forEach(measurement => {
            confirmMessage += `- Type: ${measurement.measurement_type}\n`;
            
            if (measurement.changedFields.value) {
                confirmMessage += `  Value: ${measurement.original.measurement_value} → ${measurement.measurement_value}\n`;
            }
            if (measurement.changedFields.comments) {
                confirmMessage += `  Comments: ${measurement.original.comments || 'N/A'} → ${measurement.comments || 'N/A'}\n`;
            }
        });
        confirmMessage += '\n';
    }

    if (deletedMeasurements.size > 0) {
        confirmMessage += 'Deleted Measurements:\n';
        deletedMeasurements.forEach(id => {
            const measurement = initialData.measurements.find(m => m.id === parseInt(id));
            const typeDescription = measurementTypeChoices.find(
                type => type.measurement_type === measurement.measurement_type
            )?.description || measurement.measurement_type;
            
            confirmMessage += `- Type: ${typeDescription}\n`;
            confirmMessage += `  Value: ${measurement.measurement_value}\n`;
            if (measurement.comments) confirmMessage += `  Comments: ${measurement.comments}\n`;
        });
    }

    if (!confirm(confirmMessage)) {
        return;
    }

    try {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        const response = await fetch('/wamtram2/api/recorded-measurements/update/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                observation_id: initialData.basic_info.observation_id,
                recorded_measurements: [...newMeasurements, ...modifiedMeasurements],
                deleted_measurements: Array.from(deletedMeasurements)
            })
        });

        const data = await response.json();
        if (data.status === 'success') {
            alert('Measurements updated successfully!');
            location.reload();
        } else {
            alert(`Error: ${data.message}`);
        }
    } catch (error) {
        alert(`Save failed: ${error.message}`);
    }
}

// Add global variable to track deleted damage records
let deletedDamage = new Set();

// Generate damage HTML template
function generateDamageHtml(damage = {}) {
    const cardId = 'damage-card-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    return `
        <div class="card mb-3 damage-card" id="${cardId}" 
            data-damage-id="${damage.observation_id || ''}">
            <div class="card-body">
                <div class="form-row">
                    <div class="col-md-4">
                        <div class="form-group">
                            <label>Body Part</label>
                            <select class="form-control" name="body_part">
                                <option value="">Select...</option>
                                ${initialData.body_parts.map(part => `
                                    <option value="${part.body_part}" 
                                        ${damage.body_part === part.body_part ? 'selected' : ''}>
                                        ${part.description}
                                    </option>
                                `).join('')}
                            </select>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="form-group">
                            <label>Damage Code</label>
                            <select class="form-control" name="damage_code">
                                <option value="">Select...</option>
                                ${initialData.damage_codes.map(code => `
                                    <option value="${code.damage_code}" 
                                        ${damage.damage_code === code.damage_code ? 'selected' : ''}>
                                        ${code.description}
                                    </option>
                                `).join('')}
                            </select>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="form-group">
                            <label>Comments</label>
                            <input type="text" class="form-control" name="comments" 
                                value="${damage.comments || ''}">
                        </div>
                    </div>
                    <div class="col-md-1">
                        <div class="form-group">
                            <label>&nbsp;</label>
                            <button type="button" class="btn btn-danger btn-block">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Add new damage record
function addDamage() {
    const damageContainer = document.getElementById('damageContainer');
    
    if (damageContainer.innerHTML.includes('No damage records found')) {
        damageContainer.innerHTML = '';
    }
    
    damageContainer.insertAdjacentHTML('beforeend', generateDamageHtml());
}

// Delete damage record
function deleteDamage(event) {
    const damageCard = event.target.closest('.damage-card');
    const bodyPartSelect = damageCard.querySelector('[name="body_part"]');
    const bodyPart = bodyPartSelect ? bodyPartSelect.value : null;

    
    if (damageCard.classList.contains('deleted')) {
        damageCard.classList.remove('deleted');
        deletedDamage.delete(bodyPart);
    } else {
        damageCard.classList.add('deleted');
        if (bodyPart) {
            deletedDamage.add(bodyPart);
        }
    }
}

// Save damage changes
async function saveDamageChanges() {
    const newDamage = [];
    const modifiedDamage = [];
    
    document.querySelectorAll('.damage-card:not(.deleted)').forEach(card => {
        const bodyPartSelect = card.querySelector('[name="body_part"]');
        const damageCodeSelect = card.querySelector('[name="damage_code"]');
        const commentsInput = card.querySelector('[name="comments"]');
        
        if (!bodyPartSelect || !damageCodeSelect) {
            console.error('Required elements not found in damage card');
            return;
        }

        const damageData = {
            body_part: bodyPartSelect.value,
            damage_code: damageCodeSelect.value,
            comments: commentsInput ? commentsInput.value.trim() : '',
        };
        
        // Skip if required fields are missing
        if (!damageData.body_part || !damageData.damage_code) {
            return;
        }

        const existingDamage = initialData.damage_records.find(
            d => d.body_part === damageData.body_part
        );
        
        if (existingDamage) {
            if (existingDamage.damage_code !== damageData.damage_code || 
                existingDamage.comments !== damageData.comments) {
                modifiedDamage.push(damageData);
            }
        } else {
            newDamage.push(damageData);
        }
    });

    // If no changes, return early
    if (newDamage.length === 0 && modifiedDamage.length === 0 && deletedDamage.size === 0) {
        alert('No changes to save');
        return;
    }

    // Create confirmation message
    let confirmMessage = 'Please confirm the following changes:\n\n';
    
    if (newDamage.length > 0) {
        confirmMessage += 'New Damage Records:\n';
        newDamage.forEach(damage => {
            const bodyPartDesc = initialData.body_parts.find(
                part => part.body_part === damage.body_part
            )?.description || damage.body_part;
            const damageCodeDesc = initialData.damage_codes.find(
                code => code.damage_code === damage.damage_code
            )?.description || damage.damage_code;
            
            confirmMessage += `- Body Part: ${bodyPartDesc}\n`;
            confirmMessage += `  Damage Code: ${damageCodeDesc}\n`;
            if (damage.comments) confirmMessage += `  Comments: ${damage.comments}\n`;
        });
        confirmMessage += '\n';
    }

    if (modifiedDamage.length > 0) {
        confirmMessage += 'Modified Damage Records:\n';
        modifiedDamage.forEach(damage => {
            const bodyPartDesc = initialData.body_parts.find(
                part => part.body_part === damage.body_part
            )?.description || damage.body_part;
            const existingDamage = initialData.damage_records.find(
                d => d.body_part === damage.body_part
            );
            
            confirmMessage += `- Body Part: ${bodyPartDesc}\n`;
            if (existingDamage.damage_code !== damage.damage_code) {
                const oldDesc = initialData.damage_codes.find(
                    code => code.damage_code === existingDamage.damage_code
                )?.description || existingDamage.damage_code;
                const newDesc = initialData.damage_codes.find(
                    code => code.damage_code === damage.damage_code
                )?.description || damage.damage_code;
                confirmMessage += `  Damage Code: ${oldDesc} → ${newDesc}\n`;
            }
            if (existingDamage.comments !== damage.comments) {
                confirmMessage += `  Comments: ${existingDamage.comments || 'N/A'} → ${damage.comments || 'N/A'}\n`;
            }
        });
        confirmMessage += '\n';
    }

    if (deletedDamage.size > 0) {
        confirmMessage += 'Deleted Damage Records:\n';
        deletedDamage.forEach(bodyPart => {
            const damage = initialData.damage_records.find(d => d.body_part === bodyPart);
            if (damage) {
                const bodyPartDesc = initialData.body_parts.find(
                    part => part.body_part === damage.body_part
                )?.description || damage.body_part;
                confirmMessage += `- Body Part: ${bodyPartDesc}\n`;
                if (damage.comments) confirmMessage += `  Comments: ${damage.comments}\n`;
            }
        });
    }

    if (!confirm(confirmMessage)) {
        return;
    }

    const requestData = {
        observation_id: initialData.basic_info.observation_id,
        recorded_damage: [...newDamage, ...modifiedDamage],
        deleted_damage: Array.from(deletedDamage)
    };

    try {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        const response = await fetch('/wamtram2/api/recorded-damage/update/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(requestData)
        });

        const data = await response.json();
        
        if (data.status === 'success') {
            alert('Damage records updated successfully!');
            location.reload();
        } else {
            alert(`Error: ${data.message}`);
        }
    } catch (error) {
        console.error('Save failed:', error);
        alert(`Save failed: ${error.message}`);
    }
}

async function saveScarsChanges() {
    const scarsData = {
        scars_left: document.querySelector('[name="scars_left"]').checked,
        scars_right: document.querySelector('[name="scars_right"]').checked,
        scars_left_scale_1: document.querySelector('[name="scars_left_scale_1"]').checked,
        scars_left_scale_2: document.querySelector('[name="scars_left_scale_2"]').checked,
        scars_left_scale_3: document.querySelector('[name="scars_left_scale_3"]').checked,
        scars_right_scale_1: document.querySelector('[name="scars_right_scale_1"]').checked,
        scars_right_scale_2: document.querySelector('[name="scars_right_scale_2"]').checked,
        scars_right_scale_3: document.querySelector('[name="scars_right_scale_3"]').checked,
        tag_scar_not_checked: document.querySelector('[name="tag_scar_not_checked"]').checked
    };

    // Check for changes
    const hasChanges = Object.keys(scarsData).some(key => 
        scarsData[key] !== initialData.scars[key]
    );

    if (!hasChanges) {
        alert('No changes to save');
        return;
    }

    // Create confirmation message
    let confirmMessage = 'Please confirm the following changes:\n\n';
    Object.keys(scarsData).forEach(key => {
        if (scarsData[key] !== initialData.scars[key]) {
            confirmMessage += `${key}: ${initialData.scars[key]} → ${scarsData[key]}\n`;
        }
    });

    if (!confirm(confirmMessage)) {
        return;
    }

    try {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        const response = await fetch('/wamtram2/api/recorded-scars/update/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                observation_id: initialData.basic_info.observation_id,
                scars: scarsData
            })
        });

        const data = await response.json();
        if (data.status === 'success') {
            alert('Scars updated successfully!');
            location.reload();
        } else {
            alert(`Error: ${data.message}`);
        }
    } catch (error) {
        alert(`Save failed: ${error.message}`);
    }
}
