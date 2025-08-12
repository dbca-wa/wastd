document.addEventListener('DOMContentLoaded', function() {
    const toggleSampleButton = document.getElementById('toggleSampleButton');
    if (toggleSampleButton) {
        toggleSampleButton.addEventListener('click', toggleSampleFields);
    } else {
        console.error('toggleSampleButton not found');
    }
});

function toggleSampleFields() {
    const moreSamples = document.getElementById('moreSamples');
    const toggleButtonIcon = document.getElementById('toggleSampleIcon');

    if (moreSamples.style.display === 'none' || moreSamples.style.display === '') {
        moreSamples.style.display = 'block';
        toggleButtonIcon.classList.remove('fa-plus');
        toggleButtonIcon.classList.add('fa-minus');
    } else {
        moreSamples.style.display = 'none';
        toggleButtonIcon.classList.remove('fa-minus');
        toggleButtonIcon.classList.add('fa-plus');
    }
} 