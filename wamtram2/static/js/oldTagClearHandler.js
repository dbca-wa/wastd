document.addEventListener('DOMContentLoaded', function() {
    const flipperTagCheckField = document.getElementById('id_flipper_tag_check');
    const pitTagCheckField = document.getElementById('id_pit_tag_check');

    function clearFlipperTagFields() {
        const fields = [
            'id_recapture_left_tag_id',
            'id_recapture_left_tag_id_2',
            'id_recapture_right_tag_id',
            'id_recapture_right_tag_id_2',
            'id_recapture_left_tag_state',
            'id_recapture_left_tag_state_2',
            'id_recapture_right_tag_state',
            'id_recapture_right_tag_state_2',
            'id_recapture_left_tag_position',
            'id_recapture_left_tag_position_2',
            'id_recapture_right_tag_position',
            'id_recapture_right_tag_position_2',
            'id_recapture_left_tag_barnacles',
            'id_recapture_left_tag_barnacles_2',
            'id_recapture_right_tag_barnacles',
            'id_recapture_right_tag_barnacles_2'
        ];
        fields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                field.value = '';
            }
        });
    }

    function clearPitTagFields() {
        const fields = [
            'id_recapture_pittag_id',
            'id_recapture_pittag_id_2',
            'id_recapture_pittag_id_3',
            'id_recapture_pittag_id_4'
        ];
        fields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                field.value = '';
            }
        });
    }

    if (flipperTagCheckField) {
        flipperTagCheckField.addEventListener('change', function() {
            if (this.value === 'N') {
                clearFlipperTagFields();
            }
        });
    }

    if (pitTagCheckField) {
        pitTagCheckField.addEventListener('change', function() {
            if (this.value === 'N') {
                clearPitTagFields();
            }
        });
    }
});