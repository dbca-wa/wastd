document.addEventListener('DOMContentLoaded', function() {
    const didNotCheckInjuryBox = document.getElementById('id_didnotcheckforinjury');
    if (didNotCheckInjuryBox) {
        didNotCheckInjuryBox.addEventListener('change', toggleInjuryDetails);
        toggleInjuryDetails();
    } else {
        console.error('didNotCheckInjuryBox not found: id_didnotcheckforinjury');
    }

    const toggleInjuryFieldsButton = document.getElementById('toggleInjuryFieldsButton');
    if (toggleInjuryFieldsButton) {
        toggleInjuryFieldsButton.addEventListener('click', toggleInjuryFields);
    } else {
        console.error('toggleInjuryFieldsButton not found');
    }
});

function toggleInjuryDetails() {
    const didNotCheckInjuryBox = document.getElementById('id_didnotcheckforinjury');
    const injuryDetails = document.getElementById('injuryDetails');

    if (didNotCheckInjuryBox && didNotCheckInjuryBox.checked) {
        injuryDetails.style.display = 'none';
    } else {
        injuryDetails.style.display = 'block';
    }
}

function toggleInjuryFields() {
    const injuryAdditionalFields = document.getElementById('injuryAdditionalFields');
    const toggleButtonIcon = document.getElementById('toggleInjuryIcon');

    if (injuryAdditionalFields.style.display === 'none' || injuryAdditionalFields.style.display === '') {
        injuryAdditionalFields.style.display = 'block';
        toggleButtonIcon.classList.remove('fa-plus');
        toggleButtonIcon.classList.add('fa-minus');
    } else {
        injuryAdditionalFields.style.display = 'none';
        toggleButtonIcon.classList.remove('fa-minus');
        toggleButtonIcon.classList.add('fa-plus');
    }
}
