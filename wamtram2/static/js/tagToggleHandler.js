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

function toggleRecaptureTags() {
    const additionalRecaptureLeftTag = document.getElementById('additionalRecaptureLeftTag');
    const additionalRecaptureRightTag = document.getElementById('additionalRecaptureRightTag');
    const toggleBtn = document.getElementById('toggleRecaptureTagsBtn');
    if (additionalRecaptureLeftTag.style.display === 'none' || additionalRecaptureLeftTag.style.display === '') {
        additionalRecaptureLeftTag.style.display = 'table-row';
        additionalRecaptureRightTag.style.display = 'table-row';
        toggleBtn.innerHTML = '<i class="fas fa-minus"></i>';
    } else {
        additionalRecaptureLeftTag.style.display = 'none';
        additionalRecaptureRightTag.style.display = 'none';
        toggleBtn.innerHTML = '<i class="fas fa-plus"></i>';
    }
}

function toggleNewTags() {
    const additionalNewLeftTag = document.getElementById('additionalNewLeftTag');
    const additionalNewRightTag = document.getElementById('additionalNewRightTag');
    const toggleBtn = document.getElementById('toggleNewTagsBtn');
    if (additionalNewLeftTag.style.display === 'none' || additionalNewLeftTag.style.display === '') {
        additionalNewLeftTag.style.display = 'table-row';
        additionalNewRightTag.style.display = 'table-row';
        toggleBtn.innerHTML = '<i class="fas fa-minus"></i>';
    } else {
        additionalNewLeftTag.style.display = 'none';
        additionalNewRightTag.style.display = 'none';
        toggleBtn.innerHTML = '<i class="fas fa-plus"></i>';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Existing toggle buttons
    const toggleRecaptureTagsBtn = document.getElementById('toggleRecaptureTagsBtn');
    if (toggleRecaptureTagsBtn) {
        toggleRecaptureTagsBtn.addEventListener('click', toggleRecaptureTags);
    }

    const toggleNewTagsBtn = document.getElementById('toggleNewTagsBtn');
    if (toggleNewTagsBtn) {
        toggleNewTagsBtn.addEventListener('click', toggleNewTags);
    }

    // New toggle buttons for PIT tags
    const toggleRecapturePITTagsBtn = document.getElementById('toggleRecapturePITTagsBtn');
    if (toggleRecapturePITTagsBtn) {
        toggleRecapturePITTagsBtn.addEventListener('click', toggleRecapturePITTags);
    }

    const toggleNewPITTagsBtn = document.getElementById('toggleNewPITTagsBtn');
    if (toggleNewPITTagsBtn) {
        toggleNewPITTagsBtn.addEventListener('click', toggleNewPITTags);
    }
});

// Toggle function for Recapture PIT Tags
function toggleRecapturePITTags() {
    const additionalRecapturePITTags = document.getElementById('additionalRecapturePITTags');
    const toggleBtn = document.getElementById('toggleRecapturePITTagsBtn');
    if (additionalRecapturePITTags.style.display === 'none' || additionalRecapturePITTags.style.display === '') {
        additionalRecapturePITTags.style.display = 'block';
        toggleBtn.innerHTML = '<i class="fas fa-minus"></i>';
    } else {
        additionalRecapturePITTags.style.display = 'none';
        toggleBtn.innerHTML = '<i class="fas fa-plus"></i>';
    }
}

// Toggle function for New PIT Tags
function toggleNewPITTags() {
    const additionalNewPITTags = document.getElementById('additionalNewPITTags');
    const toggleBtn = document.getElementById('toggleNewPITTagsBtn');
    if (additionalNewPITTags.style.display === 'none' || additionalNewPITTags.style.display === '') {
        additionalNewPITTags.style.display = 'block';
        toggleBtn.innerHTML = '<i class="fas fa-minus"></i>';
    } else {
        additionalNewPITTags.style.display = 'none';
        toggleBtn.innerHTML = '<i class="fas fa-plus"></i>';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    var flipperTagCheck = document.getElementById('id_flipper_tag_check');
    var oldFlipperTagSection = document.getElementById('oldFlipperTagSection');

    function toggleOldFlipperTagSection() {
        if (flipperTagCheck.value === 'N') {
            oldFlipperTagSection.style.display = 'none';
        } else {
            oldFlipperTagSection.style.display = '';
        }
    }

    toggleOldFlipperTagSection();

    flipperTagCheck.addEventListener('change', toggleOldFlipperTagSection);
});
