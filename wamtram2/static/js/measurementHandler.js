document.addEventListener('DOMContentLoaded', function() {
    const addMeasurementButton = document.getElementById('toggleMeasurementButton');
    if (addMeasurementButton) {
        addMeasurementButton.addEventListener('click', toggleMeasurementFields);
    } else {
        console.error('toggleMeasurementButton not found');
    }

    const ccLengthNotMeasured = document.getElementById('id_cc_length_not_measured');
    if (ccLengthNotMeasured) {
        ccLengthNotMeasured.addEventListener('change', toggleCurvedCarapaceLength);
    } else {
        console.error('ccLengthNotMeasured not found');
    }

    const ccWidthNotMeasured = document.getElementById('id_cc_width_not_measured');
    if (ccWidthNotMeasured) {
        ccWidthNotMeasured.addEventListener('change', toggleCurvedCarapaceWidth);
    } else {
        console.error('ccWidthNotMeasured not found');
    }

    toggleCurvedCarapaceLength();
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

function toggleCurvedCarapaceLength() {
    const ccLengthElement = document.getElementById('id_curved_carapace_length');
    if (!ccLengthElement) {
        console.error('ccLengthElement not found');
        return;
    }
    const curvedCarapaceLength = ccLengthElement.parentElement;
    if (curvedCarapaceLength) {
        const ccLengthNotMeasured = document.getElementById('id_cc_length_not_measured');
        if (ccLengthNotMeasured.checked) {
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
