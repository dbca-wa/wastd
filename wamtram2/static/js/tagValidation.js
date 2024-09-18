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
    const batchId = form.querySelector('[name="entry_batch"]').value;
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

    // Tag validation
    const turtleIdInput = document.getElementById('id_turtle_id');
    const tagInputs = {
        recaptureLeftTagInput: document.getElementById('id_recapture_left_tag_id'),
        recaptureRightTagInput: document.getElementById('id_recapture_right_tag_id'),
        recaptureLeftTagInput2: document.getElementById('id_recapture_left_tag_id_2'),
        recaptureRightTagInput2: document.getElementById('id_recapture_right_tag_id_2'),
        newLeftTagInput: document.getElementById('id_new_left_tag_id'),
        newRightTagInput: document.getElementById('id_new_right_tag_id'),
        newLeftTagInput2: document.getElementById('id_new_left_tag_id_2'),
        newRightTagInput2: document.getElementById('id_new_right_tag_id_2'),
        newPitTagInput: document.getElementById('id_new_pittag_id'),
        newPitTagInput2: document.getElementById('id_new_pittag_id_2'),
        recapturePitTagInput: document.getElementById('id_recapture_pittag_id'),
        recapturePitTagInput2: document.getElementById('id_recapture_pittag_id_2'),
        newPitTagInput3: document.getElementById('id_new_pittag_id_3'),
        newPitTagInput4: document.getElementById('id_new_pittag_id_4'),
        recapturePitTagInput3: document.getElementById('id_recapture_pittag_id_3'),
        recapturePitTagInput4: document.getElementById('id_recapture_pittag_id_4')
    };

    const validationMessages = {
        recaptureLeftTagMessage: document.getElementById('left-tag-validation-message'),
        recaptureRightTagMessage: document.getElementById('right-tag-validation-message'),
        recaptureLeftTagMessage2: document.getElementById('left-tag-validation-message-2'),
        recaptureRightTagMessage2: document.getElementById('right-tag-validation-message-2'),
        newLeftTagMessage: document.getElementById('new-left-tag-validation-message'),
        newRightTagMessage: document.getElementById('new-right-tag-validation-message'),
        newLeftTagMessage2: document.getElementById('new-left-tag-validation-message-2'),
        newRightTagMessage2: document.getElementById('new-right-tag-validation-message-2'),
        newPitTagMessage: document.getElementById('new-pit-tag-validation-message'),
        newPitTagMessage2: document.getElementById('new-pit-tag-validation-message-2'),
        recapturePitTagMessage: document.getElementById('recapture-pit-tag-validation-message'),
        recapturePitTagMessage2: document.getElementById('recapture-pit-tag-validation-message-2'),
        newPitTagMessage3: document.getElementById('new-pit-tag-validation-message-3'),
        newPitTagMessage4: document.getElementById('new-pit-tag-validation-message-4'),
        recapturePitTagMessage3: document.getElementById('recapture-pit-tag-validation-message-3'),
        recapturePitTagMessage4: document.getElementById('recapture-pit-tag-validation-message-4'),
    };

    const detailedMessages = {
        recaptureLeftTagDetailedMessage: document.getElementById('left-tag-message'),
        recaptureRightTagDetailedMessage: document.getElementById('right-tag-message'),
        recaptureLeftTagDetailedMessage2: document.getElementById('left-tag-message-2'),
        recaptureRightTagDetailedMessage2: document.getElementById('right-tag-message-2'),
        newLeftTagDetailedMessage: document.getElementById('new-left-tag-message'),
        newRightTagDetailedMessage: document.getElementById('new-right-tag-message'),
        newLeftTagDetailedMessage2: document.getElementById('new-left-tag-message-2'),
        newRightTagDetailedMessage2: document.getElementById('new-right-tag-message-2'),
        newPitTagDetailedMessage: document.getElementById('new-pit-tag-message'),
        newPitTagDetailedMessage2: document.getElementById('new-pit-tag-message-2'),
        recapturePitTagDetailedMessage: document.getElementById('recapture-pit-tag-message'),
        recapturePitTagDetailedMessage2: document.getElementById('recapture-pit-tag-message-2'),
        newPitTagDetailedMessage3: document.getElementById('new-pit-tag-message-3'),
        newPitTagDetailedMessage4: document.getElementById('new-pit-tag-message-4'),
        recapturePitTagDetailedMessage3: document.getElementById('recapture-pit-tag-message-3'),
        recapturePitTagDetailedMessage4: document.getElementById('recapture-pit-tag-message-4')
    };

    function validateTag(tagInput, validationMessage, detailedMessage, type, side) {
        const turtleId = turtleIdInput.value;
        const tagId = tagInput.value;
    
        tagInput.classList.remove('is-valid', 'is-invalid', 'is-warning');
    
        if (!turtleId && tagId && (type === 'recaptured_tag' || type === 'recaptured_pit_tag')) {
            setValidationStatus(tagInput, validationMessage, detailedMessage, 'invalid', '✗ invalid untagged turtle with recapture tag');
            doNotProcessField.checked = true;
            updateBackgroundColor();
            return;
        }
    
        if (tagId) {
            let url = `/wamtram2/validate-tag/?type=${type}&tag=${tagId}`;
            if (type === 'recaptured_tag') {
                url += `&turtle_id=${turtleId}&side=${side}`;
            } else if (type === 'recaptured_pit_tag') {
                url += `&turtle_id=${turtleId}`;
            }
    
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    if (data.valid && !data.wrong_side) {
                        setValidationStatus(tagInput, validationMessage, detailedMessage, 'valid', '✓ Valid tag');
                        doNotProcessField.checked = false;
                    } else if (data.wrong_side) {
                        setValidationStatus(tagInput, validationMessage, detailedMessage, 'warning', '! Tag may be on the wrong side');
                        doNotProcessField.checked = true;
                    } else if (data.other_turtle_id) {
                        setValidationStatus(tagInput, validationMessage, detailedMessage, 'invalid', '✗ Invalid tag:', `Tag belongs to another turtle (ID: <a href="/wamtram2/turtles/${data.other_turtle_id}/" target="_blank">${data.other_turtle_id}</a>)`);
                        doNotProcessField.checked = true;
                    } else if (data.status) {
                        setValidationStatus(tagInput, validationMessage, detailedMessage, 'invalid', '✗ Invalid tag:', `Tag status - ${data.status}`);
                        doNotProcessField.checked = true;
                    } else if (data.tag_not_found) {
                        setValidationStatus(tagInput, validationMessage, detailedMessage, 'invalid', '✗ Invalid tag: Tag not found (Please remove it from here and add it to the comment area)');
                        doNotProcessField.checked = true;
                    } else {
                        setValidationStatus(tagInput, validationMessage, detailedMessage, 'invalid', '✗ Invalid tag');
                        doNotProcessField.checked = true;
                    }
                    updateBackgroundColor();
                })
                .catch(error => {
                    console.error('Error:', error);
                    setValidationStatus(tagInput, validationMessage, detailedMessage, 'invalid', 'Error validating tag');
                    doNotProcessField.checked = true;
                    updateBackgroundColor();
                });
        } else {
            validationMessage.textContent = '';
            detailedMessage.textContent = '';
            updateBackgroundColor();
        }
    }
    
    function setValidationStatus(input, validationMessage, detailedMessage, status, message, detailedMessageText = '') {
        input.classList.remove('is-valid', 'is-invalid', 'is-warning');
        input.classList.add(`is-${status}`);
    
        validationMessage.textContent = message;
        detailedMessage.innerHTML = detailedMessageText;
    
        switch (status) {
            case 'valid':
                validationMessage.style.color = 'green';
                break;
            case 'invalid':
                validationMessage.style.color = 'red';
                detailedMessage.style.color = 'red';
                break;
            case 'warning':
                validationMessage.style.color = 'orange';
                break;
        }

        if (status === 'invalid' && message.includes('Tag not found')) {
            detailedMessage.innerHTML = `${detailedMessageText} <a href="#" class="remove-and-comment-link">Remove and add to comment</a>`;
            const link = detailedMessage.querySelector('.remove-and-comment-link');
            link.addEventListener('click', function(e) {
                e.preventDefault();
                removeTagAndAddToComment(input);
            });
        } else {
            detailedMessage.innerHTML = detailedMessageText;
        }

    }

    function removeTagAndAddToComment(input) {
        const tagValue = input.value;
        const commentArea = document.getElementById('id_comments');
        
        if (commentArea) {
            commentArea.value += (commentArea.value ? '\n' : '') + `Invalid tag: ${tagValue}`;
        }
        
        input.value = '';
        
        input.dispatchEvent(new Event('blur'));
    }
    
    function addValidationListener(input, validationMessage, detailedMessage, type, side = '') {
        if (input) {
            input.addEventListener('blur', function() {
                validateTag(this, validationMessage, detailedMessage, type, side);
            });
        } else {
            console.error('Input element not found for validation listener');
        }
    }

    // Add validation listeners for each tag input
    addValidationListener(tagInputs.recaptureLeftTagInput, validationMessages.recaptureLeftTagMessage, detailedMessages.recaptureLeftTagDetailedMessage, 'recaptured_tag', 'L');
    addValidationListener(tagInputs.recaptureRightTagInput, validationMessages.recaptureRightTagMessage, detailedMessages.recaptureRightTagDetailedMessage, 'recaptured_tag', 'R');
    addValidationListener(tagInputs.recaptureLeftTagInput2, validationMessages.recaptureLeftTagMessage2, detailedMessages.recaptureLeftTagDetailedMessage2, 'recaptured_tag', 'L');
    addValidationListener(tagInputs.recaptureRightTagInput2, validationMessages.recaptureRightTagMessage2, detailedMessages.recaptureRightTagDetailedMessage2, 'recaptured_tag', 'R');
    addValidationListener(tagInputs.newLeftTagInput, validationMessages.newLeftTagMessage, detailedMessages.newLeftTagDetailedMessage, 'new_tag');
    addValidationListener(tagInputs.newRightTagInput, validationMessages.newRightTagMessage, detailedMessages.newRightTagDetailedMessage, 'new_tag');
    addValidationListener(tagInputs.newLeftTagInput2, validationMessages.newLeftTagMessage2, detailedMessages.newLeftTagDetailedMessage2, 'new_tag');
    addValidationListener(tagInputs.newRightTagInput2, validationMessages.newRightTagMessage2, detailedMessages.newRightTagDetailedMessage2, 'new_tag');
    addValidationListener(tagInputs.newPitTagInput, validationMessages.newPitTagMessage, detailedMessages.newPitTagDetailedMessage, 'new_pit_tag');
    addValidationListener(tagInputs.newPitTagInput2, validationMessages.newPitTagMessage2, detailedMessages.newPitTagDetailedMessage2, 'new_pit_tag');
    addValidationListener(tagInputs.recapturePitTagInput, validationMessages.recapturePitTagMessage, detailedMessages.recapturePitTagDetailedMessage, 'recaptured_pit_tag');
    addValidationListener(tagInputs.recapturePitTagInput2, validationMessages.recapturePitTagMessage2, detailedMessages.recapturePitTagDetailedMessage2, 'recaptured_pit_tag');
    addValidationListener(tagInputs.newPitTagInput3, validationMessages.newPitTagMessage3, detailedMessages.newPitTagDetailedMessage3, 'new_pit_tag');
    addValidationListener(tagInputs.newPitTagInput4, validationMessages.newPitTagMessage4, detailedMessages.newPitTagDetailedMessage4, 'new_pit_tag');
    addValidationListener(tagInputs.recapturePitTagInput3, validationMessages.recapturePitTagMessage3, detailedMessages.recapturePitTagDetailedMessage3, 'recaptured_pit_tag');
    addValidationListener(tagInputs.recapturePitTagInput4, validationMessages.recapturePitTagMessage4, detailedMessages.recapturePitTagDetailedMessage4, 'recaptured_pit_tag');
});
