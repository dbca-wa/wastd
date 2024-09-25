document.addEventListener('DOMContentLoaded', function() {
    const addMeasurementButton = document.getElementById('toggleMeasurementButton');
    if (addMeasurementButton) {
        addMeasurementButton.addEventListener('click', toggleMeasurementFields);
    } else {
        console.error('toggleMeasurementButton not found');
    }

    const ccLengthMinNotMeasured = document.getElementById('id_cc_notch_length_not_measured');
    if (ccLengthMinNotMeasured) {
        ccLengthMinNotMeasured.addEventListener('change', toggleCCLMin);
    } else {
        console.error('ccLengthMinNotMeasured not found');
    }

    const ccWidthNotMeasured = document.getElementById('id_cc_width_not_measured');
    if (ccWidthNotMeasured) {
        ccWidthNotMeasured.addEventListener('change', toggleCurvedCarapaceWidth);
    } else {
        console.error('ccWidthNotMeasured not found');
    }

    toggleCCLMin();
    toggleCurvedCarapaceWidth();
});

function toggleMeasurementFields() {
    const moreMeasurement = document.getElementById('moreMeasurement');
    const toggleButtonIcon = document.getElementById('toggleMeasurementIcon');

    if (moreMeasurement.style.display === 'none' || moreMeasurement.style.display === '') {
        moreMeasurement.style.display = 'block';
        toggleButtonIcon.classList.remove('fa-plus');
        toggleButtonIcon.classList.add('fa-minus');
    } else {
        moreMeasurement.style.display = 'none';
        toggleButtonIcon.classList.remove('fa-minus');
        toggleButtonIcon.classList.add('fa-plus');
    }
}

function toggleCCLMin() {
    const ccLengthElement = document.getElementById('id_curved_carapace_length_notch');
    if (!ccLengthElement) {
        console.error('ccLengthElement not found');
        return;
    }
    const curvedCarapaceLength = ccLengthElement.parentElement;
    if (curvedCarapaceLength) {
        const ccLengthMinNotMeasured = document.getElementById('id_cc_notch_length_not_measured');
        if (ccLengthMinNotMeasured.checked) {
            curvedCarapaceLength.style.display = 'none';
        } else {
            curvedCarapaceLength.style.display = 'block';
        }
    } else {
        console.error('curvedCarapaceLength not found');
    }
}

function toggleCurvedCarapaceWidth() {
    const ccWidthElement = document.getElementById('id_curved_carapace_width');
    if (!ccWidthElement) {
        console.error('ccWidthElement not found');
        return;
    }
    const curvedCarapaceWidth = ccWidthElement.parentElement;
    if (curvedCarapaceWidth) {
        const ccWidthNotMeasured = document.getElementById('id_cc_width_not_measured');
        if (ccWidthNotMeasured.checked) {
            curvedCarapaceWidth.style.display = 'none';
        } else {
            curvedCarapaceWidth.style.display = 'block';
        }
    } else {
        console.error('curvedCarapaceWidth not found');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const measurementTypes = [
        'measurement_type_1', 'measurement_type_2', 'measurement_type_3',
        'measurement_type_4', 'measurement_type_5', 'measurement_type_6'
    ];

    function updateMeasurementOptions() {
        const selectedValues = new Set();

        measurementTypes.forEach(id => {
            const select = document.getElementById(id);
            if (select.value) {
                selectedValues.add(select.value);
            }
        });

        measurementTypes.forEach(id => {
            const select = document.getElementById(id);
            const currentValue = select.value;

            selectedValues.delete(currentValue);

            Array.from(select.options).forEach(option => {
                if (option.value && option.value !== currentValue) {
                    option.style.display = selectedValues.has(option.value) ? 'none' : '';
                }
            });

            if (currentValue) {
                selectedValues.add(currentValue);
            }
        });
    }

    measurementTypes.forEach(id => {
        document.getElementById(id).addEventListener('change', updateMeasurementOptions);
    });

    updateMeasurementOptions();
});
