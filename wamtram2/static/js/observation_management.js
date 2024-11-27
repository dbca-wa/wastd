$(document).ready(function() {
    // Global variables
    let currentObservationId = null;
    const formFields = new Set();
    let originalData = {};

    // Initialize form validation and other components
    function initialize() {
        initializeFormValidation();
        initializeDropdowns();
        bindEventHandlers();
        // setupAutoSave();
    }

    // Form validation
    function initializeFormValidation() {
        $('form input, form select').each(function() {
            if ($(this).prop('required')) {
                formFields.add($(this).attr('name'));
            }
        });
    }

    // Initialize select2 dropdowns
    function initializeDropdowns() {
        $('select').select2({
            theme: 'bootstrap4',
            width: '100%'
        });

        $('.select2-places').select2({
            theme: 'bootstrap4',
            width: '100%',
            placeholder: 'Search Place...',
            allowClear: true,
            minimumInputLength: 2,
            ajax: {
                url: '/wamtram2/api/get-places/',
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
                                text: item.full_name,
                                place_name: item.place_name,
                                location_name: item.location_code__location_name
                            };
                        })
                    };
                },
                cache: true
            },
            templateResult: formatPlace,
            templateSelection: formatPlaceSelection
        });

        $('.select2-places').on('change', function() {
            handleSearch();
        });
    }

    function formatPlace(place) {
        if (!place.id) return place.text;
        return $(`<span>
            <strong>${place.place_name}</strong><br>
            <small class="text-muted">${place.location_name}</small>
        </span>`);
    }
    

    function formatPlaceSelection(place) {
        if (!place.id) return place.text;
        return place.text;
    }

    // Bind event handlers
    function bindEventHandlers() {
        // Save button click
        $('#saveChanges').click(handleSave);
        // Filter changes
        $('#tagSearch, #placeFilter, #dateFilter, #statusFilter').on('change', handleSearch);

        // Form field changes
        $('form input, form select').on('change', function() {
            $(this).addClass('modified');
            checkFormValidity();
        });

        // Add damage record button
        $('#addDamage').click(addDamageRecord);

        // Add measurement button
        $('#addMeasurement').click(addMeasurementRow);

        // // Coordinate conversion
        // $('.coordinate-input').on('change', convertCoordinates);

        $('#searchBtn').click(handleSearch);
    
        $('#tagSearch').keypress(function(e) {
            if(e.which == 13) {
                handleSearch();
            }
        });

        $('#placeFilter, #dateFilter, #statusFilter').change(handleSearch);

        $(document).on('click', '.remove-tag', function() {
            $(this).closest('.tag-row').remove();
        });
        
        $(document).on('click', '.remove-measurement', function() {
            $(this).closest('.measurement-row').remove();
        });
        
        $(document).on('click', '.remove-damage', function() {
            $(this).closest('.damage-record').remove();
        });
    }

    function clearForm() {
        $('#basicInfo input, #basicInfo select').val('');
        
        $('#tagInfo .tag-row').remove();
        
        $('#measurements .measurement-row').remove();
        
        $('#damage .damage-record').remove();
        
        $('#location input, #location select').val('');
        
        $('.modified').removeClass('modified');
        currentObservationId = null;
    }

    function updateOriginalData(data) {
        originalData = JSON.parse(JSON.stringify(data));
    }
    
    function validateForm() {
        let isValid = true;
        let firstInvalidField = null;

        formFields.forEach(fieldName => {
            const field = $(`[name="${fieldName}"]`);
            if (!field.val()) {
                field.addClass('is-invalid');
                if (!firstInvalidField) {
                    firstInvalidField = field;
                }
                isValid = false;
            } else {
                field.removeClass('is-invalid');
            }
        });
        if (firstInvalidField) {
            firstInvalidField.focus();
            $('html, body').animate({
                scrollTop: firstInvalidField.offset().top - 100
            }, 500);
        }

        return isValid;
    }

    function addTagRow(tagData = {}) {
        const tagRow = $(`
            <div class="tag-row form-row mb-2">
                <div class="col">
                    <input type="text" class="form-control" name="tag_id" 
                           value="${tagData.tag_id || ''}" placeholder="Tag ID">
                </div>
                <div class="col">
                    <select class="form-control" name="tag_type">
                        <option value="">Select Type...</option>
                        <!-- Add tag type options -->
                    </select>
                </div>
                <div class="col">
                    <button type="button" class="btn btn-danger btn-sm remove-tag">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
        `);
        $('#tagInfo .tag-container').append(tagRow);
    }
    
    function addMeasurementRow(measurementData = {}) {
        const measurementRow = $(`
            <div class="measurement-row form-row mb-2">
                <div class="col">
                    <select class="form-control" name="measurement_type">
                        <option value="">Select Type...</option>
                        <!-- Add measurement type options -->   
                    </select>
                </div>
                <div class="col">
                    <input type="number" class="form-control" name="measurement_value" 
                           value="${measurementData.measurement_value || ''}" step="0.1">
                </div>
                <div class="col">
                    <button type="button" class="btn btn-danger btn-sm remove-measurement">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
        `);
        $('#measurements .measurement-container').append(measurementRow);
    }
    
    function addDamageRecord(damageData = {}) {
        const damageRecord = $(`
            <div class="damage-record form-row mb-2">
                <div class="col">
                    <select class="form-control" name="body_part">
                        <option value="">Select Body Part...</option>
                        <!-- Add body part options -->
                    </select>
                </div>
                <div class="col">
                    <select class="form-control" name="damage_code">
                        <option value="">Select Damage...</option>
                        <!-- Add damage code options -->
                    </select>
                </div>
                <div class="col">
                    <button type="button" class="btn btn-danger btn-sm remove-damage">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
        `);
        $('#damage .damage-container').append(damageRecord);
    }

    async function handleSearch() {
        console.log("\n=== Starting Search ===");
        console.log("Search input values:");
        console.log("Tag Search:", $('#tagSearch').val());
        console.log("Place:", $('.select2-places').val());
        console.log("Date:", $('#dateFilter').val());
        console.log("Status:", $('#statusFilter').val());

        showLoadingOverlay();
        $('#searchResults tbody').html(`
            <tr>
                <td colspan="6" class="text-center">
                    <div class="spinner-border spinner-border-sm" role="status">
                        <span class="sr-only">Loading...</span>
                    </div>
                    Searching...
                </td>
            </tr>
        `);    
        try {
            const searchParams = new URLSearchParams({
                search: $('#tagSearch').val(),
                place: $('.select2-places').val(),
                date: $('#dateFilter').val(),
                status: $('#statusFilter').val()
            });
    
            const response = await $.get(`/wamtram2/api/observations/?${searchParams.toString()}`);
            if (response.status === 'success') {
                displaySearchResults(response.data);
            } else {
                throw new Error(response.message);
            }
        } catch (error) {
            $('#searchResults tbody').html(`
                <tr>
                    <td colspan="6" class="text-center text-danger">
                        <i class="fas fa-exclamation-circle"></i>
                        Error performing search: ${error.message}
                    </td>
                </tr>
            `);
        } finally {
            hideLoadingOverlay();
        }
    }

    function displaySearchResults(results) {
        console.log("\n=== Displaying Results ===");
        console.log("Results count:", results.length);
        
        const resultsTable = $('#searchResults');
        if (resultsTable.length === 0) {
            
            $('.container-fluid').append(`
                <div class="row mt-3">
                    <div class="col-12">
                        <table id="searchResults" class="table table-striped">
                            <thead>
                                <tr>
                                    <th>Observation ID</th>
                                    <th>Turtle ID</th>
                                    <th>Date</th>
                                    <th>Place</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody></tbody>
                        </table>
                    </div>
                </div>
            `);
        }
    
        const tbody = $('#searchResults tbody');
        tbody.empty();

        if (results.length === 0) {
            tbody.append(`
                <tr>
                    <td colspan="6" class="text-center">No results found</td>
                </tr>
            `);
            return;
        }
    
        results.forEach(result => {
            const tagInfo = result.tags.length > 0 ? 
            `Tags: ${result.tags.join(', ')}` : '';
            const pitTagInfo = result.pit_tags.length > 0 ? 
                `PIT Tags: ${result.pit_tags.join(', ')}` : '';
            const tagDisplay = [tagInfo, pitTagInfo].filter(x => x).join(' | ');
            tbody.append(`
            <tr>
                <td>${result.observation_id}</td>
                <td>${result.turtle_id || ''}</td>
                <td>${result.observation_date}
                    ${result.observation_time ? ' ' + result.observation_time : ''}
                </td>
                <td>${result.place_code} - ${result.place_description}</td>
                <td>${result.status || ''}</td>
                <td>
                    <small class="text-muted d-block">${tagDisplay}</small>
                    <button class="btn btn-sm btn-primary mt-1" 
                            onclick="loadObservation(${result.observation_id})">
                        Edit
                    </button>
                </td>
            </tr>
            `);
        });
    }

    // Handle save operation
    async function handleSave() {
        if (!validateForm()) {
            showErrorMessage('Please fill in all required fields');
            return;
        }

        showLoadingOverlay();
        try {
            const formData = collectFormData();
            const response = await $.ajax({
                url: '/wamtram2/api/observations/',
                method: currentObservationId ? 'PUT' : 'POST',
                data: JSON.stringify(formData),
                contentType: 'application/json'
            });

            if (response.status === 'success') {
                showSuccessMessage('Changes saved successfully');
                updateOriginalData(formData);
                if (!currentObservationId) {
                    currentObservationId = response.observation_id;
                }
            } else {
                throw new Error(response.message);
            }
        } catch (error) {
            showErrorMessage('Error saving changes: ' + error.message);
        } finally {
            hideLoadingOverlay();
        }
    }

    // Collect form data
    function collectFormData() {
        const data = {
            basic_info: {},
            tag_info: {
                recorded_tags: [],
                recorded_pit_tags: []
            },
            measurements: [],
            damage_records: [],
            location: {}
        };

        // Collect basic information
        $('#basicInfo input, #basicInfo select').each(function() {
            data.basic_info[$(this).attr('name')] = $(this).val();
        });

        // Collect tag information
        $('#tagInfo .tag-row').each(function() {
            const tagData = {
                tag_id: $(this).find('[name="tag_id"]').val(),
                tag_type: $(this).find('[name="tag_type"]').val(),
                tag_position: $(this).find('[name="tag_position"]').val(),
                tag_state: $(this).find('[name="tag_state"]').val()
            };
            data.tag_info.recorded_tags.push(tagData);
        });

        // Collect measurements
        $('#measurements .measurement-row').each(function() {
            const measurementData = {
                measurement_type: $(this).find('[name="measurement_type"]').val(),
                measurement_value: $(this).find('[name="measurement_value"]').val()
            };
            data.measurements.push(measurementData);
        });

        // Collect damage records
        $('#damage .damage-record').each(function() {
            const damageData = {
                body_part: $(this).find('[name="body_part"]').val(),
                damage_code: $(this).find('[name="damage_code"]').val()
            };
            data.damage_records.push(damageData);
        });

        // Collect location information
        $('#location input, #location select').each(function() {
            data.location[$(this).attr('name')] = $(this).val();
        });

        return data;
    }

    // Load observation data
    async function loadObservation(observationId) {
        showLoadingOverlay();
        try {
            const response = await $.get(`/wamtram2/api/observations/${observationId}/`);
            if (response.status === 'success') {
                populateForm(response.data);
                currentObservationId = observationId;
                updateOriginalData(response.data);
            } else {
                throw new Error(response.message);
            }
        } catch (error) {
            showErrorMessage('Error loading observation: ' + error.message);
        } finally {
            hideLoadingOverlay();
        }
    }

    // Populate form with data
    function populateForm(data) {
        clearForm();

        // Populate basic information
        for (const [key, value] of Object.entries(data.basic_info)) {
            $(`[name="${key}"]`).val(value);
        }

        // Populate tags
        data.tag_info.recorded_tags.forEach(tag => {
            addTagRow(tag);
        });

        // Populate measurements
        data.measurements.forEach(measurement => {
            addMeasurementRow(measurement);
        });

        // Populate damage records
        data.damage_records.forEach(damage => {
            addDamageRecord(damage);
        });

        // Populate location
        for (const [key, value] of Object.entries(data.location)) {
            $(`[name="${key}"]`).val(value);
        }
    }

    // Utility functions
    function showLoadingOverlay() {
        $('.loading-overlay').show();
    }

    function hideLoadingOverlay() {
        $('.loading-overlay').hide();
    }

    function showSuccessMessage(message) {
        const alertHtml = `
            <div class="alert alert-success alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
            </div>
        `;
        $('.container-fluid').prepend(alertHtml);
    }

    function showErrorMessage(message) {
        const alertHtml = `
            <div class="alert alert-danger alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
            </div>
        `;
        $('.container-fluid').prepend(alertHtml);
    }

    // function setupAutoSave() {
    //     let autoSaveTimer;
    //     let autoSaveNotification;
    
    //     $('form').on('change', 'input, select', function() {
    //         clearTimeout(autoSaveTimer);
            
    //         if (!autoSaveNotification) {
    //             autoSaveNotification = $('<div class="alert alert-info position-fixed" style="bottom: 20px; right: 20px;">Changes will be auto-saved...</div>');
    //             $('body').append(autoSaveNotification);
    //         }
            
    //         autoSaveTimer = setTimeout(() => {
    //             handleSave().then(() => {
    //                 if (autoSaveNotification) {
    //                     autoSaveNotification.remove();
    //                     autoSaveNotification = null;
    //                 }
    //             });
    //         }, 30000);
    //     });
    // }

    $(window).on('beforeunload', function() {
        if (hasUnsavedChanges()) {
            return "You have unsaved changes. Are you sure you want to leave?";
        }
    });
    
    function hasUnsavedChanges() {
        return $('.modified').length > 0;
    }

    // Initialize the page
    initialize();
}); 