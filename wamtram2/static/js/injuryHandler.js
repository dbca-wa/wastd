document.addEventListener('DOMContentLoaded', function() {
    const toggleInjuryFieldsButton = document.getElementById('toggleInjuryFieldsButton');
    if (toggleInjuryFieldsButton) {
        toggleInjuryFieldsButton.addEventListener('click', toggleInjuryFields);
    } else {
        console.error('toggleInjuryFieldsButton not found');
    }

    const bodyPartFields = ['id_body_part_1', 'id_body_part_2', 'id_body_part_3', 'id_body_part_4'];
    bodyPartFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) {
            field.addEventListener('change', updateBodyPartOptions);
        } else {
            console.error(`${fieldId} not found`);
        }
    });

    updateBodyPartOptions();
});

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

function updateBodyPartOptions() {
    const bodyPartFields = ['id_body_part_1', 'id_body_part_2', 'id_body_part_3', 'id_body_part_4'];
    const selectedValues = new Set();

    bodyPartFields.forEach(fieldId => {
        const select = document.getElementById(fieldId);
        if (select && select.value) {
            selectedValues.add(select.value);
        }
    });

    bodyPartFields.forEach(fieldId => {
        const select = document.getElementById(fieldId);
        if (select) {
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
        }
    });
}
