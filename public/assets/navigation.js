(function () {
    "use strict";

    var mobileQuery = window.matchMedia("(max-width: 850px)");

    function initializeNavigation(button) {
        var navigationId = button.getAttribute("aria-controls");
        var navigation = document.getElementById(navigationId);

        if (!navigation) {
            return;
        }

        function setExpanded(expanded) {
            button.setAttribute("aria-expanded", String(expanded));
            navigation.hidden = mobileQuery.matches && !expanded;
        }

        function synchronizeLayout() {
            if (mobileQuery.matches) {
                setExpanded(button.getAttribute("aria-expanded") === "true");
            } else {
                navigation.hidden = false;
            }
        }

        button.addEventListener("click", function () {
            setExpanded(button.getAttribute("aria-expanded") !== "true");
        });

        navigation.addEventListener("click", function (event) {
            if (mobileQuery.matches && event.target.closest("a")) {
                setExpanded(false);
            }
        });

        mobileQuery.addEventListener?.("change", synchronizeLayout);
        synchronizeLayout();
    }

    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll("[data-sidebar-toggle]").forEach(
            initializeNavigation
        );
    });
}());
