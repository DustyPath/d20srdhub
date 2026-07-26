(function () {
    "use strict";

    function initializeDirectory(directory) {
        var search = directory.querySelector("[data-class-search]");
        var category = directory.querySelector("[data-class-category]");
        var count = directory.querySelector("[data-class-count]");
        var groups = Array.from(
            directory.querySelectorAll("[data-class-group]")
        );
        var items = Array.from(
            directory.querySelectorAll("[data-class-item]")
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
                    "[data-class-item]:not([hidden])"
                );
            });

            count.textContent =
                visible + (visible === 1 ? " feature" : " features");
        }

        [search, category].forEach(function (control) {
            control.addEventListener("input", applyFilters);
            control.addEventListener("change", applyFilters);
        });

        applyFilters();
    }

    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll("[data-class-directory]").forEach(
            initializeDirectory
        );
    });
}());
