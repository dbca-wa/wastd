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
        setOtherIdentification();
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
                console.log(`Set ${field} select2 to:`, data);
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
                            <button type="button" class="btn btn-danger btn-block delete-flipper-tag">
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
        tagContainer.innerHTML = '<p class="text-muted">No flipper tags found</p>';
        return;
    }

    initialData.tag_info.recorded_tags.forEach(tag => {
        tagContainer.insertAdjacentHTML('beforeend', generateTagHtml(tag));
    });

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

    const allTagSelects = [
        // Flipper tag selects
        'tag_side',
        'tag_position',
        'tag_state',
        // PIT tag selects
        'pit_tag_position',
        'pit_tag_state'
    ];

    allTagSelects.forEach(selectName => {
        $(`#tagContainer select[name="${selectName}"], #pitTagContainer select[name="${selectName}"]`).select2({
            theme: 'bootstrap4',
            placeholder: 'Select...',
            allowClear: true,
            width: '100%'
        });
    });

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
    

function saveOriginalFormData() {
    originalFormData = {};
    const formElements = document.querySelectorAll('input, select, textarea');
    formElements.forEach(element => {
        
        originalFormData[element.name] = element.value;
    });
    console.log('Saved original form data:', originalFormData);
}


function getFormChanges() {
    const changes = {};
    const currentFormData = {};
    const formElements = document.querySelectorAll('input, select, textarea');
    
    formElements.forEach(element => {
        const currentValue = element.value;
        const originalValue = originalFormData[element.name];
        
        console.log(`Comparing ${element.name}:`, { 
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
function handleDeleteTag(event) {
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


// Event listener setup
document.addEventListener('DOMContentLoaded', function() {
    // Add Flipper Tag button
    document.getElementById('addFlipperTagBtn').addEventListener('click', addFlipperTag);
    
    // Delete button (using event delegation)
    document.getElementById('tagContainer').addEventListener('click', function(e) {
        if (e.target.closest('.delete-flipper-tag')) {
            handleDeleteTag(e);
        }
    });
    
    // Save button
    document.getElementById('saveTagsBtn').addEventListener('click', saveTagChanges);
});
