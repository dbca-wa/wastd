document.addEventListener('DOMContentLoaded', function() {
    const entryId = document.body.dataset.entryId;

    if (entryId) {
        console.log("Entry ID found:", entryId);
        expandAdditionalFields();
    } else {
        console.log("No Entry ID found");
    }

    function expandAdditionalFields() {
        console.log("Expanding additional fields");
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
                console.log(`Expanding ${id}`);
                element.style.display = 'block';
            } else {
                console.log(`Element not found: ${id}`);
            }
        });

        updateButtonStates();
    }

    function updateButtonStates() {
        console.log("Updating button states");
        const buttonUpdates = [
            { id: 'toggleInjuryFieldsButton', text: 'Less Injuries' },
            { id: 'toggleRecaptureTagsBtn', text: 'Less Recapture Tags' },
            { id: 'toggleNewTagsBtn', text: 'Less New Tags' },
            { id: 'toggleMeasurementButton', text: 'Less Measurements' },
            { id: 'advancedDataButton', action: 'hide' }
        ];

        buttonUpdates.forEach(update => {
            const button = document.getElementById(update.id);
            if (button) {
                if (update.action === 'hide') {
                    console.log(`Hiding ${update.id}`);
                    button.style.display = 'none';
                } else {
                    console.log(`Updating text for ${update.id}`);
                    button.textContent = update.text;
                }
                
                const icon = button.querySelector('i');
                if (icon) {
                    icon.classList.remove('fa-plus');
                    icon.classList.add('fa-minus');
                }
            } else {
                console.log(`Button not found: ${update.id}`);
            }
        });
    }
});