(function () {
    "use strict";

    function initializeDirectory(directory) {
        var search = directory.querySelector("[data-combat-search]");
        var category = directory.querySelector("[data-combat-category]");
        var count = directory.querySelector("[data-combat-count]");
        var groups = Array.from(
            directory.querySelectorAll("[data-combat-group]")
        );
        var items = Array.from(
            directory.querySelectorAll("[data-combat-item]")
        );

        function applyFilters() {
            var query = search.value.toLowerCase().trim();
            var selectedCategory = category.value;
            var visible = 0;

            items.forEach(function (item) {
                var nameMatches = !query ||
                    item.dataset.name.indexOf(query) !== -1;
                var categoryMatches = !selectedCategory ||
                    item.dataset.category === selectedCategory;
                var matches = nameMatches && categoryMatches;

                item.hidden = !matches;

                if (matches) {
                    visible += 1;
                }
            });

            groups.forEach(function (group) {
                group.hidden = !group.querySelector(
                    "[data-combat-item]:not([hidden])"
                );
            });

            count.textContent =
                visible + (visible === 1 ? " topic" : " topics");
        }

        [search, category].forEach(function (control) {
            control.addEventListener("input", applyFilters);
            control.addEventListener("change", applyFilters);
        });

        applyFilters();
    }

    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll("[data-combat-directory]").forEach(
            initializeDirectory
        );
    });
}());
