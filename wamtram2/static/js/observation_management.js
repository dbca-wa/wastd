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
    initializeBasicSelects();
    initializeSearchSelects();
    
    // Initialize change tracking
    initializeChangeTracking();
    
    // If initialData is defined, set initial form values
    if (typeof initialData !== 'undefined' && initialData) {
        setInitialFormValues();
    }

    // Bind save button click event
    $('#saveButton').on('click', function(e) {
        e.preventDefault();
        handleSave();
    });

    $('.select2').select2({
        theme: 'bootstrap4',
        width: '100%'
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
        'date_convention'
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
        setOtherIdentification();
        setScars();
        setOtherTagInfo();
        
        // Then initialize change tracking after all values are set
        setTimeout(() => {
            initializeChangeTracking();
        }, 100);
    }
}

// Set basic form fields
function setBasicFields() {
    const basicInfo = initialData.basic_info;
    if (!basicInfo) return;

    // Set date/time
    if (basicInfo.observation_date) {
        $('[name="observation_date"]').val(basicInfo.observation_date);
    }

    // Set person fields
    const personFields = ['measurer_person', 'measurer_reporter_person', 'tagger_person', 'reporter_person'];
    personFields.forEach(field => {
        if (basicInfo[field] && basicInfo[field].id) {
            const $select = $(`select[name="${field}"]`);
            const option = new Option(basicInfo[field].text, basicInfo[field].id, true, true);
            $select.append(option).trigger('change');
        }
    });

    if (basicInfo.turtle_id) {
        $('[name="turtle_id"]').val(basicInfo.turtle_id);
        $('#turtleDetailLink').attr('href', `/wamtram2/turtles/${basicInfo.turtle_id}/`);
    }

    // Set place select
    if (basicInfo.place_code) {
        const $placeSelect = $('select[name="place_code"]');
        const option = new Option(basicInfo.place_code.text, basicInfo.place_code.id, true, true);
        $placeSelect.append(option).trigger('change');
    }

    // Set other basic fields
    const basicFields = [
        'observation_id', 'turtle_id', 'alive', 'nesting','clutch_completed',
        'activity_code', 'beach_position_code', 'condition_code',
        'egg_count_method', 'observation_status', 'comments',
        'date_convention', 'datum_code',
        'latitude', 'longitude', 'number_of_eggs'
    ];

    basicFields.forEach(fieldName => {
        if (basicInfo[fieldName] !== undefined) {
            const $field = $(`[name="${fieldName}"]`);
            if ($field.length) {
                if ($field.is('select')) {
                    $field.val(basicInfo[fieldName]).trigger('change');
                } else {
                    $field.val(basicInfo[fieldName]);
                }
            }
        }
    });
}

// Set tag information
function setTagInfo() {
    // Regular tags
    const tagContainer = document.getElementById('tagContainer');
    if (tagContainer && initialData.tag_info?.recorded_tags) {
        tagContainer.innerHTML = '';
        
        if (initialData.tag_info.recorded_tags.length === 0) {
            tagContainer.innerHTML = '<p class="text-muted">No flipper tags found</p>';
            return;
        }

        initialData.tag_info.recorded_tags.forEach(tag => {
            const tagHtml = `
                <div class="card mb-3 tag-card">
                    <div class="card-body">
                        <div class="form-row">
                            <div class="col-md-3">
                                <div class="form-group">
                                    <label>Tag ID</label>
                                    <input type="text" class="form-control" name="tag_id" value="${tag.tag_id || ''}" >
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="form-group">
                                    <label>Side</label>
                                    <select class="form-control" name="tag_side">
                                        <option value="L" ${tag.tag_side === 'L' ? 'selected' : ''}>L</option>
                                        <option value="R" ${tag.tag_side === 'R' ? 'selected' : ''}>R</option>
                                    </select>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="form-group">
                                    <label>Position</label>
                                    <select class="form-control" name="tag_position">
                                        <option value="1" ${tag.tag_position === '1' ? 'selected' : ''}>1</option>
                                        <option value="2" ${tag.tag_position === '2' ? 'selected' : ''}>2</option>
                                        <option value="3" ${tag.tag_position === '3' ? 'selected' : ''}>3</option>
                                    </select>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="form-group">
                                    <label>State</label>
                                    <select class="form-control" name="tag_state">
                                        <option value="">Select...</option>
                                        ${tagStateChoices.map(state => `
                                            <option value="${state.tag_state}" ${tag.tag_state === state.tag_state ? 'selected' : ''}>
                                                ${state.description}
                                            </option>
                                        `).join('')}
                                    </select>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            tagContainer.insertAdjacentHTML('beforeend', tagHtml);
        });
    }

    // PIT tags
    const pitTagContainer = document.getElementById('pitTagContainer');
    if (pitTagContainer && initialData.tag_info?.recorded_pit_tags) {
        pitTagContainer.innerHTML = '';
        
        if (initialData.tag_info.recorded_pit_tags.length === 0) {
            pitTagContainer.innerHTML = '<p class="text-muted">No PIT tags found</p>';
            return;
        }

        initialData.tag_info.recorded_pit_tags.forEach(pitTag => {
            const pitTagHtml = `
                <div class="card mb-3 pit-tag-card">
                    <div class="card-body">
                        <div class="form-row">
                            <div class="col-md-4">
                                <div class="form-group">
                                    <label>PIT Tag ID</label>
                                    <input type="text" class="form-control" name="pittag_id" value="${pitTag.tag_id || ''}" >
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="form-group">
                                    <label>Position</label>
                                    <select class="form-control" name="pit_tag_position">
                                        <option value="LF" ${pitTag.tag_position === 'LF' ? 'selected' : ''}>L</option>
                                        <option value="RF" ${pitTag.tag_position === 'RF' ? 'selected' : ''}>R</option>
                                    </select>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="form-group">
                                    <label>State</label>
                                    <select class="form-control" name="pit_tag_state">
                                        <option value="">Select...</option>
                                        ${pitTagStateChoices.map(state => `
                                            <option value="${state.pit_tag_state}" ${pitTag.tag_state === state.pit_tag_state ? 'selected' : ''}>
                                                ${state.description}
                                            </option>
                                        `).join('')}
                                    </select>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            pitTagContainer.insertAdjacentHTML('beforeend', pitTagHtml);
        });
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
        const measurementHtml = `
            <div class="card mb-3 measurement-card">
                <div class="card-body">
                    <div class="form-row">
                        <div class="col-md-6">
                            <div class="form-group">
                                <label>Measurement Type</label>
                                <select class="form-control" name="measurement_type" value="${measurement.measurement_type}">
                                    <option value="">Select...</option>
                                    ${measurementTypeChoices.map(type => `
                                        <option value="${type.measurement_type}" ${measurement.measurement_type === type.measurement_type ? 'selected' : ''}>
                                            ${type.description}
                                        </option>
                                    `).join('')}
                                </select>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="form-group">
                                <label>Value</label>
                                <input type="number" class="form-control" name="measurement_value" value="${measurement.measurement_value}">
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        measurementContainer.insertAdjacentHTML('beforeend', measurementHtml);
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
        const damageHtml = `
            <div class="card mb-3 damage-card">
                <div class="card-body">
                    <div class="form-row">
                        <div class="col-md-4">
                            <div class="form-group">
                                <label>Body Part</label>
                                <select class="form-control" name="body_part">
                                    <option value="">Select...</option>
                                    ${bodyPartsChoices.map(part => `
                                        <option value="${part.body_part}" ${damage.body_part === part.body_part ? 'selected' : ''}>
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
                                    ${damageCodesChoices.map(code => `
                                        <option value="${code.damage_code}" ${damage.damage_code === code.damage_code ? 'selected' : ''}>
                                            ${code.description}
                                        </option>
                                    `).join('')}
                                </select>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="form-group">
                                <label>Comments</label>
                                <input type="text" class="form-control" name="damage_comments" value="${damage.comments || ''}">
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        damageContainer.insertAdjacentHTML('beforeend', damageHtml);
    });
}

// Set other identification data
function setOtherIdentification() {
    const container = document.getElementById('otherIdContainer');
    if (!container || !initialData.recorded_identifications) return;
    
    container.innerHTML = '';

    // Set other identification data
    if (initialData.other_tags_data) {
        const otherIdentificationHtml = `
            <div class="card mb-3">
                <div class="card-body">
                    <div class="form-row">
                        <div class="col-md-6">
                            <div class="form-group">
                                <label>Other Identification</label>
                                <input type="text" class="form-control" name="other_tags" 
                                    value="${initialData.other_tags_data.other_tags || ''}">
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="form-group">
                                <label>Identification Type</label>
                                <select class="form-control" name="other_tags_identification_type">
                                    <option value="">Select...</option>
                                    ${identificationTypeChoices.map(type => `
                                        <option value="${type.identification_type}" 
                                            ${initialData.other_tags_data.identification_type === type.identification_type ? 'selected' : ''}>
                                            ${type.description}
                                        </option>
                                    `).join('')}
                                </select>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        container.insertAdjacentHTML('beforeend', otherIdentificationHtml);

        $('[name="other_tags_identification_type"]').select2({
            placeholder: 'Select identification type...',
            allowClear: true
        });
    }

    if (initialData.recorded_identifications.length === 0) {
        if (!initialData.other_tags_data) {
            container.innerHTML = '<p class="text-muted">No other identifications found</p>';
        }
        return;
    }

    initialData.recorded_identifications.forEach(identification => {
        const identificationHtml = `
            <div class="card mb-3 identification-card">
                <div class="card-body">
                    <div class="form-row">
                        <div class="col-md-3">
                            <div class="form-group">
                                <label>Turtle ID</label>
                                <input type="text" class="form-control" name="turtle_id[]" 
                                    value="${identification.turtle_id || ''}">
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-group">
                                <label>Identification Type</label>
                                <select class="form-control" name="identification_type[]">
                                    <option value="">Select...</option>
                                    ${identificationTypeChoices.map(type => `
                                        <option value="${type.identification_type}" 
                                            ${identification.identification_type === type.identification_type ? 'selected' : ''}>
                                            ${type.description}
                                        </option>
                                    `).join('')}
                                </select>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-group">
                                <label>Identifier</label>
                                <input type="text" class="form-control" name="identifier[]" 
                                    value="${identification.identifier || ''}">
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-group">
                                <label>Comments</label>
                                <input type="text" class="form-control" name="identification_comments[]" 
                                    value="${identification.comments || ''}">
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        container.insertAdjacentHTML('beforeend', identificationHtml);
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
    

function setOtherTagInfo() {
    const container = document.getElementById('otherTagInfoContainer');
    console.log('Setting other tag info:', initialData.other_tags_data); // 添加调试日志
    
    if (!container || !initialData.other_tags_data) {
        console.log('Container or other tags data missing:', {
            container, 
            other_tags_data: initialData.other_tags_data
        });
        return;
    }

    const otherTagInfoHtml = `
        <div class="card mb-3">
            <div class="card-body">
                <div class="form-row">
                    <div class="col-md-6">
                        <div class="form-group">
                            <label>Other Tags</label>
                            <input type="text" class="form-control" name="other_tags" 
                                value="${initialData.other_tags_data.other_tags || ''}">
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="form-group">
                            <label>Identification Type</label>
                            <select class="form-control" name="other_tags_identification_type">
                                <option value="">Select...</option>
                                ${identificationTypeChoices.map(type => `
                                    <option value="${type.identification_type}" 
                                        ${initialData.other_tags_data.identification_type === type.identification_type ? 'selected' : ''}>
                                        ${type.description}
                                    </option>
                                `).join('')}
                            </select>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    container.innerHTML = otherTagInfoHtml;

    $('[name="other_tags_identification_type"]').select2({
        placeholder: 'Select identification type...',
        allowClear: true
    });
}

// Add Flipper Tag
document.getElementById('addFlipperTagBtn')?.addEventListener('click', function() {
    const template = document.getElementById('flipperTagTemplate');
    const container = document.getElementById('flipperTagContainer');
    const clone = template.content.cloneNode(true);
    
    // Populate tag status dropdown
    const statusSelect = clone.querySelector('[name="tag_status"]');
    populateTagStatus(statusSelect);
    
    container.appendChild(clone);
});

// Delete handlers
document.addEventListener('click', function(e) {
    if (e.target.closest('.delete-flipper-tag')) {
        const tagCard = e.target.closest('.flipper-tag-card');
        if (tagCard && confirm('Are you sure you want to delete this flipper tag?')) {
            const tagId = tagCard.querySelector('[name="tag_id"]').value;
            if (tagId) {
                deletedFlipperTags.push(tagId);
            }
            tagCard.remove();
        }
    }
});

// Save handlers
function saveFlipperTags() {
    const formData = {
        observation_id: currentObservationId,
        flipperTags: [],
        deletedTags: deletedFlipperTags
    };

    document.querySelectorAll('.flipper-tag-card').forEach(card => {
        formData.flipperTags.push({
            tag_id: card.querySelector('[name="tag_id"]').value,
            side: card.querySelector('[name="side"]').value,
            tag_status: card.querySelector('[name="tag_status"]').value,
            comments: card.querySelector('[name="comments"]').value
        });
    });

    return formData;
}

// 当页面加载时初始化数据
document.addEventListener('DOMContentLoaded', function() {
    // 获取初始数据
    const initialDataElement = document.getElementById('initial-data');
    if (initialDataElement) {
        const initialData = JSON.parse(initialDataElement.textContent);
        
        // 在设置表单值之前，先保存一个空的原始数据
        saveOriginalFormData();
        
        // 设置表单值
        if (initialData.basic_info) {
            Object.entries(initialData.basic_info).forEach(([key, value]) => {
                const element = document.querySelector(`[name="${key}"]`);
                if (element) {
                    element.value = value;
                }
            });
        }
        
        // 在设置完表单值后，再次保存作为真正的原始数据
        saveOriginalFormData();
    }
});

function saveOriginalFormData() {
    originalFormData = {};
    const formElements = document.querySelectorAll('input, select, textarea');
    formElements.forEach(element => {
        // 确保我们保存实际的值，而不是默认的空值
        originalFormData[element.name] = element.value;
    });
    console.log('Saved original form data:', originalFormData); // 添加调试日志
}

function getFormChanges() {
    const changes = {};
    const currentFormData = {};
    const formElements = document.querySelectorAll('input, select, textarea');
    
    formElements.forEach(element => {
        const currentValue = element.value;
        const originalValue = originalFormData[element.name];
        
        console.log(`Comparing ${element.name}:`, { // 添加调试日志
            original: originalValue,
            current: currentValue
        });
        
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