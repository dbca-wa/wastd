document.addEventListener('DOMContentLoaded', function() {
    const entryId = document.body.dataset.entryId;
    if (entryId) {
        expandAllFields();
    }

    function expandAllFields() {
        const fieldsToExpand = [
            'injuryAdditionalFields',
            'additionalRecaptureLeftTag',
            'advancedDataCard',
            'moreMeasurement',
            'moreSamples',
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
                const displayStyle = element.tagName === 'TR' ? 'table-row' : 'block';
                element.style.display = displayStyle;
            }
        });

        removeToggleButtons();
    }

    function removeToggleButtons() {
        const buttonsToRemove = [
            'toggleInjuryFieldsButton',
            'toggleRecaptureTagsBtn',
            'toggleNewTagsBtn',
            'toggleMeasurementButton',
            'toggleSampleButton',
            'toggleRecapturePITTagsBtn',
            'toggleNewPITTagsBtn',
            'advancedDataButton'
        ];

        buttonsToRemove.forEach(id => {
            const button = document.getElementById(id);
            if (button) {
                button.style.display = 'none';
            } 
        });
    }
});