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
        setupAutoSave();
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
        $('.select2-dropdown').select2({
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
                url: '/search-places/',
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

        // New record button click
        $('#addNew').click(handleNewRecord);

        // Filter changes
        $('#tagSearch, #placeFilter, #dateFilter, #statusFilter').on('change', handleFilter);

        // Form field changes
        $('form input, form select').on('change', function() {
            $(this).addClass('modified');
            checkFormValidity();
        });

        // Add damage record button
        $('#addDamage').click(addDamageRecord);

        // Add measurement button
        $('#addMeasurement').click(addMeasurementRow);

        // Coordinate conversion
        $('.coordinate-input').on('change', convertCoordinates);

        $('#searchBtn').click(handleSearch);
    
        $('#tagSearch').keypress(function(e) {
            if(e.which == 13) {
                handleSearch();
            }
        });

        $('#placeFilter, #dateFilter, #statusFilter').change(handleSearch);
    }

    async function handleSearch() {
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
    
            const response = await $.get(`/api/observations/?${searchParams.toString()}`);
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
                url: '/api/observations/',
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
            const response = await $.get(`/api/observations/${observationId}/`);
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
        // Implement your preferred notification method
        alert(message);
    }

    function showErrorMessage(message) {
        // Implement your preferred notification method
        alert(message);
    }

    // Initialize the page
    initialize();
}); 