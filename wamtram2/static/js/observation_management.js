$(document).ready(function() {
    initializeBasicSelects();
    initializeSearchSelects();
    // If initialData is defined, set initial form values
    if (typeof initialData !== 'undefined' && initialData) {
        setInitialFormValues();
    }
});

// Initialize basic select elements
function initializeBasicSelects() {
    const basicSelects = [
        'alive',
        'nesting',
        'activity_code',
        'beach_position_code',
        'condition_code',
        'egg_count_method',
        'datum_code'
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
    setBasicFields();
    setTagInfo();
    setMeasurements();
    setDamageRecords();
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

    // Set place select
    if (basicInfo.place_code) {
        const $placeSelect = $('select[name="place_code"]');
        const option = new Option(basicInfo.place_code.text, basicInfo.place_code.id, true, true);
        $placeSelect.append(option).trigger('change');
    }

    // Set other basic fields
    const basicFields = [
        'observation_id', 'turtle_id', 'alive', 'nesting',
        'activity_code', 'beach_position_code', 'condition_code',
        'egg_count_method', 'observation_status', 'comments', 'clutch_completed', 'date_convention',
        'datum_code', 'latitude', 'longitude' 
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

// Set measurements data and render measurement cards
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

// Set damage records data and render damage cards
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

// Set tag info
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

// Handle form submission
function handleFormSubmit() {
    const formData = {
        basic_info: getBasicInfo(),
        tag_info: getTagInfo(),
        measurements: getMeasurements(),
        damage_records: getDamageRecords(),
        location: getLocationInfo()
    };

    $.ajax({
        url: submitUrl,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(formData),
        headers: {
            'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
        },
        success: function(response) {
            if (response.status === 'success') {
                showSuccessMessage('Observation saved successfully');
            } else {
                showErrorMessage(response.message || 'Error saving observation');
            }
        },
        error: function(xhr) {
            showErrorMessage('Error saving observation');
        }
    });
}

// Get basic information from form
function getBasicInfo() {
    const observationDateTime = $('[name="observation_date"]').val();
    return {
        observation_id: $('[name="observation_id"]').val(),
        observation_date: observationDateTime,
        alive: $('[name="alive"]').val(),
        nesting: $('[name="nesting"]').val(),
        activity_code: $('[name="activity_code"]').val(),
        beach_position_code: $('[name="beach_position_code"]').val(),
        condition_code: $('[name="condition_code"]').val(),
        egg_count_method: $('[name="egg_count_method"]').val(),
        status: $('[name="status"]').val(),
        comments: $('[name="comments"]').val()
    };
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

// Get location information from form
function getLocationInfo() {
    return {
        place_code: $('[name="place_code"]').val(),
        datum_code: $('[name="datum_code"]').val(),
        latitude: $('[name="latitude"]').val(),
        longitude: $('[name="longitude"]').val()
    };
}

// Add getTagInfo function
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
    }, 3000);
}
