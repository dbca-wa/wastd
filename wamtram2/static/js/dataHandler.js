// static/js/tagToggleHandler.js

function toggleRecaptureTags() {
    const additionalRecaptureTags = document.getElementById('additionalRecaptureTags');
    const toggleBtn = document.getElementById('toggleRecaptureTagsBtn');
    if (additionalRecaptureTags.style.display === 'none') {
        additionalRecaptureTags.style.display = 'block';
        toggleBtn.textContent = 'Less Recapture Tags';
    } else {
        additionalRecaptureTags.style.display = 'none';
        toggleBtn.textContent = 'More Recapture Tags';
    }
}

function toggleNewTags() {
    const additionalNewTags = document.getElementById('additionalNewTags');
    const toggleBtn = document.getElementById('toggleNewTagsBtn');
    if (additionalNewTags.style.display === 'none') {
        additionalNewTags.style.display = 'block';
        toggleBtn.textContent = 'Less New Tags';
    } else {
        additionalNewTags.style.display === 'none';
        toggleBtn.textContent = 'More New Tags';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const toggleRecaptureTagsBtn = document.getElementById('toggleRecaptureTagsBtn');
    if (toggleRecaptureTagsBtn) {
        toggleRecaptureTagsBtn.addEventListener('click', toggleRecaptureTags);
    }

    const toggleNewTagsBtn = document.getElementById('toggleNewTagsBtn');
    if (toggleNewTagsBtn) {
        toggleNewTagsBtn.addEventListener('click', toggleNewTags);
    }
});

// static/js/scarHandler.js

function toggleScarsDetails() {
    const tagscarnotcheckedCheckbox = document.getElementById('{{ form.tagscarnotchecked.auto_id }}');
    const scarsDetails = document.getElementById('scarsDetails');
    const scarsDetailsRight = document.getElementById('scarsDetailsRight');

    if (tagscarnotcheckedCheckbox.checked) {
        scarsDetails.style.display = 'none';
        scarsDetailsRight.style.display = 'none';
    } else {
        scarsDetails.style.display = 'block';
        scarsDetailsRight.style.display = 'block';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('{{ form.tagscarnotchecked.auto_id }}').addEventListener('change', toggleScarsDetails);
    toggleScarsDetails();
});

// static/js/measurementHandler.js

function toggleMeasurement() {
    const moreMeasurement = document.getElementById('moreMeasurement');
    const addMeasurementButton = document.getElementById('addMeasurementButton');
    if (moreMeasurement.style.display === 'none' || moreMeasurement.style.display === '') {
        moreMeasurement.style.display = 'block';
        addMeasurementButton.innerText = 'Less Measurements';
    } else {
        moreMeasurement.style.display = 'none';
        addMeasurementButton.innerText = 'More Measurements';
    }
}

function toggleCurvedCarapaceLength() {
    const curvedCarapaceLength = document.getElementById('{{ form.curved_carapace_length.auto_id }}').parentElement;
    if (document.getElementById('{{ form.cc_length_not_measured.auto_id }}').checked) {
        curvedCarapaceLength.style.display = 'none';
    } else {
        curvedCarapaceLength.style.display = 'block';
    }
}

function toggleCurvedCarapaceWidth() {
    const curvedCarapaceWidth = document.getElementById('{{ form.curved_carapace_width.auto_id }}').parentElement;
    if (document.getElementById('{{ form.cc_width_not_measured.auto_id }}').checked) {
        curvedCarapaceWidth.style.display = 'none';
    } else {
        curvedCarapaceWidth.style.display = 'block';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('addMeasurementButton').addEventListener('click', toggleMeasurement);
    document.getElementById('{{ form.cc_length_not_measured.auto_id }}').addEventListener('change', toggleCurvedCarapaceLength);
    document.getElementById('{{ form.cc_width_not_measured.auto_id }}').addEventListener('change', toggleCurvedCarapaceWidth);
    toggleCurvedCarapaceLength(); 
    toggleCurvedCarapaceWidth();
});

// static/js/injuryHandler.js

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

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('{{ form.didnotcheckforinjury.auto_id }}').addEventListener('change', toggleInjuryDetails);
    toggleInjuryDetails();

    document.getElementById('toggleInjuryFieldsButton').addEventListener('click', toggleInjuryFields);
});