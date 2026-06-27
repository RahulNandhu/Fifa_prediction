(function () {
    'use strict';
    var KNOCKOUT_FROM = '2026-06-29';

    function updateKnockout(kickoffInput, knockoutCheck) {
        var val = kickoffInput.value;
        if (!val) return;
        var dateStr = val.substring(0, 10);
        if (dateStr >= KNOCKOUT_FROM) {
            knockoutCheck.checked = true;
        }
    }

    document.addEventListener('DOMContentLoaded', function () {
        var kickoffInput = document.getElementById('id_kickoff_at');
        var knockoutCheck = document.getElementById('id_is_knockout');
        if (!kickoffInput || !knockoutCheck) return;

        ['change', 'input'].forEach(function (evt) {
            kickoffInput.addEventListener(evt, function () {
                updateKnockout(kickoffInput, knockoutCheck);
            });
        });
        updateKnockout(kickoffInput, knockoutCheck);
    });
})();
