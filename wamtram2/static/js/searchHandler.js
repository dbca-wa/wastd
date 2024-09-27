// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const context = this;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
    };
}

// Function to search and display results
function searchAndDisplayResults(url, input, resultsContainer, hiddenFieldId, formatResult, extractId) {

    // Show the searching status
    resultsContainer.style.display = 'block';
    resultsContainer.innerHTML = '<div class="search-result">Searching...</div>';

    // Send an AJAX request to get search results
    var xhr = new XMLHttpRequest();
    xhr.open('GET', `${url}?q=${encodeURIComponent(input.value)}`, true);
    xhr.onload = function() {
        if (xhr.status === 200) {
            var results = JSON.parse(xhr.responseText);
            // Display the dropdown list and populate the results
            resultsContainer.style.display = 'block';
            resultsContainer.innerHTML = ''; // Clear previous results
            if (results.length > 0) {
                results.forEach(function(result) {
                    var div = document.createElement('div');
                    div.textContent = formatResult(result);
                    div.className = 'search-result';
                    div.onclick = function() {
                        input.value = formatResult(result);
                        let hiddenField = document.getElementById(hiddenFieldId);
                        if (hiddenField) {
                            hiddenField.value = extractId(result); // Store the ID in the hidden field
                        }
                        resultsContainer.style.display = 'none';
                    };
                    resultsContainer.appendChild(div);
                });
            } else {
                resultsContainer.innerHTML = '<div class="search-result">No data found</div>';
            }
        } else {
            // Error handling
            console.error('Search failed with status:', xhr.status);
            resultsContainer.style.display = 'none';
        }
    };
    xhr.onerror = function() {
        console.error('Search request failed');
        resultsContainer.style.display = 'none';
    };
    xhr.send();
}

// Initialize search fields
document.querySelectorAll('.search-field').forEach(function(input) {
    let resultsContainer = input.parentNode.querySelector('.search-results');
    let hiddenFieldId = input.nextElementSibling ? input.nextElementSibling.id : null;
    if (hiddenFieldId) {
        // Bind the debounce function to the input event listener
        let debouncedSearch = debounce(function() {
            let query = input.value;
            if (query.length === 0) {
                resultsContainer.style.display = 'none';
                return;
            }
            if (input.id === 'search_place_code') {
                searchAndDisplayResults('/wamtram2/search-places', input, resultsContainer, hiddenFieldId, 
                (place) => `${place.place_name} (${place.location_code__location_name})`, 
                (place) => {
                    return place.place_code;
                });
            } else {
                searchAndDisplayResults('/wamtram2/search-persons', input, resultsContainer, hiddenFieldId, 
                (person) => `${person.first_name} ${person.surname}`, 
                (person) => person.person_id);
            }
        }, 500);
        
        input.addEventListener('input', debouncedSearch);
        
        resultsContainer.addEventListener('click', function(e) {
            if (e.target.className === 'search-result') {
                input.value = e.target.textContent;
                resultsContainer.style.display = 'none';
            }
        });
    }
});
