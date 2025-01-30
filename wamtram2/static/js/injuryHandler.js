document.addEventListener('DOMContentLoaded', function() {
    const toggleInjuryFieldsButton = document.getElementById('toggleInjuryFieldsButton');
    if (toggleInjuryFieldsButton) {
        toggleInjuryFieldsButton.addEventListener('click', toggleInjuryFields);
    } else {
        console.error('toggleInjuryFieldsButton not found');
    }

    const flipperBodyParts = ['B', 'C', 'D', 'E'];

    function updateDamageCodeOptions(bodyPartSelect, damageCodeSelect) {
        const selectedBodyPart = bodyPartSelect.value;
        const options = damageCodeSelect.options;

        for (let i = 0; i < options.length; i++) {
            const option = options[i];
            if (flipperBodyParts.includes(selectedBodyPart)) {
                option.style.display = '';
            } else {
                if (['0', '5', '6', '7'].includes(option.value)) {
                    option.style.display = '';
                } else {
                    option.style.display = 'none';
                }
            }
        }
        damageCodeSelect.value = '';
    }

    for (let i = 1; i <= 6; i++) {
        const bodyPartSelect = document.getElementById(`id_body_part_${i}`);
        const damageCodeSelect = document.getElementById(`id_damage_code_${i}`);

        if (bodyPartSelect && damageCodeSelect) {
            bodyPartSelect.addEventListener('change', function() {
                const index = this.id.split('_').pop();
                const correspondingDamageCodeSelect = document.getElementById(`id_damage_code_${index}`);
                updateDamageCodeOptions(this, correspondingDamageCodeSelect);
            });
            updateDamageCodeOptions(bodyPartSelect, damageCodeSelect);
        }
    }

    const injuryCheckField = document.querySelector('[name="injury_check"]');
    const bodyPartField = document.querySelector('[name="body_part_1"]');
    const damageCodeField = document.querySelector('[name="damage_code_1"]');

    if (injuryCheckField) {
        injuryCheckField.addEventListener('change', function() {
            if (this.value === 'N') {
                bodyPartField.value = 'W';
                bodyPartField.dispatchEvent(new Event('change'));
                
                damageCodeField.value = '0';
                damageCodeField.dispatchEvent(new Event('change'));
            } else {
                bodyPartField.value = '';
                bodyPartField.dispatchEvent(new Event('change'));
                
                damageCodeField.value = '';
                damageCodeField.dispatchEvent(new Event('change'));
            }
        });
    }

    updateBodyPartOptions();

    function initializeDamageCodes() {
        for (let i = 1; i <= 6; i++) {
            const damageCodeSelect = document.getElementById(`id_damage_code_${i}`);
            if (damageCodeSelect) {
                const initialValue = damageCodeSelect.getAttribute('data-initial');
                if (initialValue) {
                    damageCodeSelect.value = initialValue;
                    damageCodeSelect.dispatchEvent(new Event('change'));
                }
            }
        }
    }
    
    initializeDamageCodes();
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
    const bodyPartFields = ['id_body_part_1', 'id_body_part_2', 'id_body_part_3', 'id_body_part_4', 'id_body_part_5', 'id_body_part_6'];
    const selectedValues = new Set();

    bodyPartFields.forEach(fieldId => {
        const select = document.getElementById(fieldId);
        if (select && select.value) {
            selectedValues.add(select.value);
        }
    });
}
