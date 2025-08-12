document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('dataEntryForm');
    if (!form) {
        console.error('Form element not found');
        return;
    }

    function updateBackgroundColor() {
        const bodyElement = document.body;
        const doNotProcessField = document.getElementById('id_do_not_process');
        if (doNotProcessField.checked) {
            bodyElement.classList.add('bg-yellow');
        } else {
            bodyElement.classList.remove('bg-yellow');
        }
    }

    // Initialize background color on page load
    const doNotProcessField = document.getElementById('id_do_not_process');
    doNotProcessField.addEventListener('change', updateBackgroundColor);
    updateBackgroundColor();

    // Get the do_not_process cookie value and set the field
    const batchId = window.BATCH_ID;
    const cookieName = `${batchId}_do_not_process`;
    const doNotProcessCookie = document.cookie.split('; ').find(row => row.startsWith(cookieName));

    if (doNotProcessCookie && doNotProcessField) {
        const cookieValue = doNotProcessCookie.split('=')[1];
        if (cookieValue === 'true') {
            doNotProcessField.checked = true;
            doNotProcessField.disabled = true;
            updateBackgroundColor();
        } else if (cookieValue === 'false') {
            doNotProcessField.checked = false;
            doNotProcessField.disabled = false;
        }
    }
});
