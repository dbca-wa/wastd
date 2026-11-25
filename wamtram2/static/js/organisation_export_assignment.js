document.addEventListener("DOMContentLoaded", function () {
    const validityType = document.getElementById("id_validity_type");
    const validFrom = document.getElementById("id_valid_from");
    const validTo = document.getElementById("id_valid_to");

    const dateFields = [
        document.getElementById("id_data_from"),
        document.getElementById("id_data_to"),
        validFrom,
        validTo,
    ].filter(Boolean);

    function formatDateInput(input) {
        const value = input.value.trim();

        // Convert DDMMYYYY to DD/MM/YYYY.
        if (/^\d{8}$/.test(value)) {
            input.value =
                value.substring(0, 2) +
                "/" +
                value.substring(2, 4) +
                "/" +
                value.substring(4, 8);
        }
    }

    dateFields.forEach(function (input) {
        input.placeholder = "DD/MM/YYYY";

        input.addEventListener("blur", function () {
            formatDateInput(input);
        });
    });

    function updateValidityFields() {
        if (!validityType || !validFrom || !validTo) {
            return;
        }

        const isPermanent = validityType.value === "permanent";

        if (isPermanent) {
            validFrom.value = "";
            validTo.value = "";
        }

        validFrom.disabled = isPermanent;
        validTo.disabled = isPermanent;
    }

    if (validityType) {
        validityType.addEventListener("change", updateValidityFields);
        updateValidityFields();
    }
});
