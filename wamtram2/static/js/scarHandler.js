document.addEventListener('DOMContentLoaded', function() {
    const tagscarnotcheckedCheckbox = document.getElementById('id_tagscarnotchecked');
    if (tagscarnotcheckedCheckbox) {
        tagscarnotcheckedCheckbox.addEventListener('change', toggleScarsDetails);
        toggleScarsDetails();
    } else {
        console.error('tagscarnotcheckedCheckbox not found: id_tagscarnotchecked');
    }
});

function toggleScarsDetails() {
    const tagscarnotcheckedCheckbox = document.getElementById('id_tagscarnotchecked');
    const scarsDetails = document.getElementById('scarsDetails');
    const scarsDetailsRight = document.getElementById('scarsDetailsRight');

    if (tagscarnotcheckedCheckbox && tagscarnotcheckedCheckbox.checked) {
        scarsDetails.style.display = 'none';
        scarsDetailsRight.style.display = 'none';
    } else {
        scarsDetails.style.display = 'block';
        scarsDetailsRight.style.display = 'block';
    }
}
