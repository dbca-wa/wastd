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