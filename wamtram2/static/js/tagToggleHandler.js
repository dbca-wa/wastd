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
