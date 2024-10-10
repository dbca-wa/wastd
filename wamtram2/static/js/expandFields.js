document.addEventListener('DOMContentLoaded', function() {
    const entryId = document.body.dataset.entryId;

    if (entryId) {
        console.log("Entry ID found:", entryId);
        expandAllFields();
    } else {
        console.log("No Entry ID found");
    }

    function expandAllFields() {
        console.log("Expanding all fields");
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

        removeToggleButtons();
    }

    function removeToggleButtons() {
        console.log("Removing toggle buttons");
        const buttonsToRemove = [
            'toggleInjuryFieldsButton',
            'toggleRecaptureTagsBtn',
            'toggleNewTagsBtn',
            'toggleMeasurementButton',
            'toggleRecapturePITTagsBtn',
            'toggleNewPITTagsBtn',
            'advancedDataButton'
        ];

        buttonsToRemove.forEach(id => {
            const button = document.getElementById(id);
            if (button) {
                console.log(`Removing ${id}`);
                button.style.display = 'none';
            } else {
                console.log(`Button not found: ${id}`);
            }
        });
    }
});