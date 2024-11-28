document.addEventListener('DOMContentLoaded', function() {

    const searchButtons = document.querySelectorAll('[id$="SearchBtn"]');
    const turtleTable = document.getElementById('turtleInfoTable');
    const tableBody = turtleTable.querySelector('tbody');
    const noResultsDiv = document.getElementById('noResults');
    const loadingSpinner = document.querySelector('.loading-spinner');
    const loadingOverlay = document.querySelector('.loading-overlay');


    async function handleSearch(searchType, searchValue) {
        try {

            loadingSpinner.style.display = 'block';
            loadingOverlay.style.display = 'block';

            tableBody.innerHTML = '';
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
                data.data.forEach(turtle => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${turtle.turtle_id}</td>
                        <td>${turtle.species}</td>
                        <td>${turtle.turtle_name}</td>
                        <td>${turtle.sex}</td>
                        <td>${turtle.cause_of_death}</td>
                        <td>${turtle.turtle_status}</td>
                        <td>${turtle.date_entered}</td>
                        <td>${turtle.comments}</td>
                    `;
                    tableBody.appendChild(row);
                });
            } else {
                noResultsDiv.style.display = 'block';
            }
        } catch (error) {
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert alert-danger';
            alertDiv.textContent = 'An error occurred while searching. Please try again.';
            turtleTable.parentNode.insertBefore(alertDiv, turtleTable);
            
            setTimeout(() => alertDiv.remove(), 3000);
        } finally {
            loadingSpinner.style.display = 'none';
            loadingOverlay.style.display = 'none';
        }
    }

    searchButtons.forEach(button => {
        button.addEventListener('click', function() {
            const searchInput = this.parentElement.previousElementSibling;
            const searchType = searchInput.id.replace('Search', '').toLowerCase();
            const searchValue = searchInput.value.trim();
            
            if (searchValue) {
                handleSearch(searchType, searchValue);
            }
        });
    });
}); 