document.addEventListener('DOMContentLoaded', function() {
    const entryId = document.body.dataset.entryId;

    if (entryId) {
        expandAdditionalFields();
    }

    function expandAdditionalFields() {
        const fieldsToExpand = [
            'injuryAdditionalFields',
            'additionalRecaptureLeftTag',
            'advancedDataCard',
            'moreMeasurement',
            'additionalNewPITTags',
            'additionalRecapturePITTags',
            'additionalNewRightTag',
            'additionalNewLeftTag',
            'additionalRecaptureRightTag',
            'additionalRecaptureLeftTag',
            'additionalRecaptureTags',
            'additionalNewTags',
            'scarsDetails',
            'scarsDetailsRight'
        ];

        fieldsToExpand.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
            element.style.display = 'block';
            }
        });

        updateButtonStates();
    }

    function updateButtonStates() {
        const buttonUpdates = [
            { id: 'toggleInjuryFieldsButton', text: 'Less Injuries' },
            { id: 'toggleRecaptureTagsBtn', text: 'Less Recapture Tags' },
            { id: 'toggleNewTagsBtn', text: 'Less New Tags' },
            { id: 'addMeasurementButton', text: 'Less Measurements' },
            { id: 'advancedDataButton', action: 'hide' }
        ];

        buttonUpdates.forEach(update => {
            const button = document.getElementById(update.id);
            if (button) {
            if (update.action === 'hide') {
                button.style.display = 'none';
            } else {
                button.textContent = update.text;
            }
            
            const icon = button.querySelector('i');
            if (icon) {
                icon.classList.remove('fa-plus');
                icon.classList.add('fa-minus');
            }
            }
        });
        }
    });