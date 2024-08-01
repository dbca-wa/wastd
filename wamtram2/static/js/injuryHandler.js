document.addEventListener('DOMContentLoaded', function() {
    const didNotCheckCheckbox = document.getElementById('{{ form.didnotcheckforinjury.auto_id }}');
    if (didNotCheckCheckbox) {
        didNotCheckCheckbox.addEventListener('change', toggleInjuryDetails);
        toggleInjuryDetails();
    }

    const toggleInjuryFieldsButton = document.getElementById('toggleInjuryFieldsButton');
    if (toggleInjuryFieldsButton) {
        toggleInjuryFieldsButton.addEventListener('click', toggleInjuryFields);
    }
});

function toggleInjuryDetails() {
    const didNotCheckCheckbox = document.getElementById('{{ form.didnotcheckforinjury.auto_id }}');
    const injuryDetails = document.getElementById('injuryDetails');

    if (didNotCheckCheckbox.checked) {
        injuryDetails.style.display = 'none';
    } else {
        injuryDetails.style.display = 'block';
    }
}

function toggleInjuryFields() {
    const injuryAdditionalFields = document.getElementById('injuryAdditionalFields');
    const toggleButton = document.getElementById('toggleInjuryFieldsButton');
    if (injuryAdditionalFields.style.display === 'none' || injuryAdditionalFields.style.display === '') {
        injuryAdditionalFields.style.display = 'block';
        toggleButton.innerText = 'Less Injuries';
    } else {
        injuryAdditionalFields.style.display = 'none';
        toggleButton.innerText = 'More Injuries';
    }
}
