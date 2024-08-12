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