(function () {
    "use strict";

    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll("[data-print-page]").forEach(
            function (button) {
                button.addEventListener("click", function () {
                    window.print();
                });
            }
        );
    });
}());
