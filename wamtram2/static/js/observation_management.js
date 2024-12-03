$(document).ready(function() {
    initializeBasicSelects();
    initializeSearchSelects();
    // If initialData is defined, set initial form values
    if (typeof initialData !== 'undefined') {
        setInitialFormValues();
    }
});

// Initialize basic selects
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

// Initialize search selects
function initializeSearchSelects() {
    // Initialize person search
    initializePersonSearch('measurer_person', 'Search measurer...');
    initializePersonSearch('measurer_reporter_person', 'Search measurer reporter...');
    initializePersonSearch('tagger_person', 'Search tagger...');
    initializePersonSearch('reporter_person', 'Search reporter...');

    // Initialize place search
    initializePlaceSearch();
}

// Initialize person search
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

// Initialize place search
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

// Set initial form values
function setInitialFormValues() {
    // Set basic fields
    setBasicFields();
    // Set search fields
    setSearchFields();
}

// Set basic fields
function setBasicFields() {
    if (initialData.observation_date) {
        const dateTime = initialData.observation_date.replace(' ', 'T');
        $('[name="observation_date"]').val(dateTime);
    }
    const basicFields = {
        'observation_id': '',
        'observation_date': '',
        'observation_time': '',
        'alive': '',
        'nesting': '',
        'activity_code': '',
        'beach_position_code': '',
        'condition_code': '',
        'egg_count_method': '',
        'datum_code': '',
        'clutch_completed': '',
        'place_description': '',
        'action_taken': '',
        'comments': '',
        'latitude': '',
        'longitude': '',
        'observation_status': '',
        'turtle_id': '',
        'entered_by': ''
    };

    Object.keys(basicFields).forEach(fieldName => {
        if (initialData[fieldName]) {
            const $field = $(`[name="${fieldName}"]`);
            if ($field.is('select')) {
                $field.val(initialData[fieldName]).trigger('change');
            } else {
                $field.val(initialData[fieldName]);
            }
        }
    });
}

// Set search fields
function setSearchFields() {
    // Set person fields
    setPersonField('measurer_person');
    setPersonField('measurer_reporter_person');
    setPersonField('tagger_person');
    setPersonField('reporter_person');

    // Set place field
    setPlaceField();
}

// Set person field
function setPersonField(fieldName) {
    if (initialData[fieldName]) {
        const $field = $(`select[name="${fieldName}"]`);
        const personName = initialData[`${fieldName}_name`];
        const option = new Option(personName, initialData[fieldName], true, true);
        $field.append(option).trigger('change');
    }
}

// Set place field
function setPlaceField() {
    if (initialData.place_code) {
        const $place = $('select[name="place_code"]');
        const option = new Option(initialData.place_description, initialData.place_code, true, true);
        $place.append(option).trigger('change');
    }
}

// Handle form submission
function handleFormSubmit() {
    const formData = {
        basic_info: getBasicInfo(),
        // Other data parts can be added as needed
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
                // Handle success response
                showSuccessMessage('Observation saved successfully');
            } else {
                // Handle error response
                showErrorMessage(response.message || 'Error saving observation');
            }
        },
        error: function(xhr) {
            // Handle error response
            showErrorMessage('Error saving observation');
        }
    });
}

// Get basic info
function getBasicInfo() {
    const observationDateTime = $('[name="observation_date"]').val();
    return {
        observation_id: $('[name="observation_id"]').val(),
        observation_date: observationDateTime,
        observation_time: observationDateTime,  
        alive: $('[name="alive"]').val(),
        nesting: $('[name="nesting"]').val(),
        activity_code: $('[name="activity_code"]').val(),
        beach_position_code: $('[name="beach_position_code"]').val(),
        condition_code: $('[name="condition_code"]').val(),
        egg_count_method: $('[name="egg_count_method"]').val(),
        datum_code: $('[name="datum_code"]').val(),
        measurer_person: $('[name="measurer_person"]').val(),
        measurer_reporter_person: $('[name="measurer_reporter_person"]').val(),
        tagger_person: $('[name="tagger_person"]').val(),
        reporter_person: $('[name="reporter_person"]').val(),
        place_code: $('[name="place_code"]').val(),
        clutch_completed: $('[name="clutch_completed"]').val(),
        place_description: $('[name="place_description"]').val(),
        action_taken: $('[name="action_taken"]').val(),
        comments: $('[name="comments"]').val(),
        latitude: $('[name="latitude"]').val(),
        longitude: $('[name="longitude"]').val()
    };
}

// Show success message
function showSuccessMessage(message) {
    // Implement message display logic
    console.log('Success:', message);
}

// Show error message
function showErrorMessage(message) {
    // Implement error message display logic
    console.error('Error:', message);
}
