document.addEventListener('DOMContentLoaded', function() {
    const tagscarnotcheckedCheckbox = document.getElementById('{{ form.tagscarnotchecked.auto_id }}');
    if (tagscarnotcheckedCheckbox) {
        tagscarnotcheckedCheckbox.addEventListener('change', toggleScarsDetails);
        toggleScarsDetails();
    }
});

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
