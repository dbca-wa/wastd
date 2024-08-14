document.addEventListener('DOMContentLoaded', function() {
    const injuryCheckSelect = document.getElementById('id_injury_check');
    if (injuryCheckSelect) {
        injuryCheckSelect.addEventListener('change', toggleInjuryDetails);
        toggleInjuryDetails();
    } else {
        console.error('injuryCheckSelect not found: id_injury_check');
    }

    const toggleInjuryFieldsButton = document.getElementById('toggleInjuryFieldsButton');
    if (toggleInjuryFieldsButton) {
        toggleInjuryFieldsButton.addEventListener('click', toggleInjuryFields);
    } else {
        console.error('toggleInjuryFieldsButton not found');
    }
});

function toggleInjuryDetails() {
    const injuryCheckSelect = document.getElementById('id_injury_check');
    const injuryDetails = document.getElementById('injuryDetails');

    if (injuryCheckSelect && injuryCheckSelect.value === 'N' || injuryCheckSelect.value === 'D') {
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
