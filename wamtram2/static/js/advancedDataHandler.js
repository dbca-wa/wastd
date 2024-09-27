document.addEventListener('DOMContentLoaded', function() {
    const advancedDataButton = document.getElementById('advancedDataButton');
    if (advancedDataButton) {
        advancedDataButton.addEventListener('click', function() {
            const advancedDataCard = document.getElementById('advancedDataCard');
            advancedDataCard.style.display = 'block';
            this.style.display = 'none';
        });
    }
});
