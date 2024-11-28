document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded');

    const searchButtons = document.querySelectorAll('[id$="SearchBtn"]');
    console.log('Found search buttons:', searchButtons.length);

    const searchResultForm = document.getElementById('searchResultForm');
    const noResultsDiv = document.getElementById('noResults');
    const loadingSpinner = document.querySelector('.loading-spinner');
    const loadingOverlay = document.querySelector('.loading-overlay');


    async function handleSearch(searchType, searchValue) {
        try {

            loadingSpinner.style.display = 'block';
            loadingOverlay.style.display = 'block';

            const inputs = searchResultForm.querySelectorAll('input');
            inputs.forEach(input => input.value = '');
            noResultsDiv.style.display = 'none';

            const params = new URLSearchParams();
            params.append(searchType, searchValue);

            const response = await fetch(`/api/turtle-search/?${params.toString()}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();

            if (data.status === 'success' && data.data.length > 0) {
                const turtle = data.data[0];
                searchResultForm.style.display = 'block';
                
                Object.keys(turtle).forEach(key => {
                    const input = searchResultForm.querySelector(`input[name="${key}"]`);
                    if (input) {
                        input.value = turtle[key];
                    }
                });
            } else {
                noResultsDiv.style.display = 'block';
                searchResultForm.style.display = 'none';
            }
        } catch (error) {
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert alert-danger';
            alertDiv.textContent = 'An error occurred while searching. Please try again.';
            searchResultForm.parentNode.insertBefore(alertDiv, searchResultForm);
            
            setTimeout(() => alertDiv.remove(), 3000);
        } finally {
            loadingSpinner.style.display = 'none';
            loadingOverlay.style.display = 'none';
        }
    }

    searchButtons.forEach(button => {
        console.log('Adding click listener to button:', button.id);
        button.addEventListener('click', function() {
            console.log('Button clicked:', this.id);
            const searchInput = this.parentElement.previousElementSibling;
            console.log('Search input:', searchInput.id, 'value:', searchInput.value);
            const searchType = searchInput.id.replace('Search', '').toLowerCase();
            const searchValue = searchInput.value.trim();
            
            if (searchValue) {
                handleSearch(searchType, searchValue);
            }
        });
    });
}); 