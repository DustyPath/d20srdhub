(function () {
    "use strict";

    function initializeDirectory(directory) {
        var search = directory.querySelector("[data-rule-search]");
        var category = directory.querySelector("[data-rule-category]");
        var count = directory.querySelector("[data-rule-count]");
        var groups = Array.from(directory.querySelectorAll("[data-rule-group]"));
        var items = Array.from(directory.querySelectorAll("[data-rule-item]"));

        function applyFilters() {
            var tokens = search.value.toLowerCase().trim().split(/\s+/).filter(Boolean);
            var selectedCategory = category.value;
            var visible = 0;

            items.forEach(function (item) {
                var nameMatches = tokens.every(function (token) {
                    return item.dataset.name.indexOf(token) !== -1;
                });
                var categoryMatches = !selectedCategory || item.dataset.category === selectedCategory;
                var matches = nameMatches && categoryMatches;
                item.hidden = !matches;
                if (matches) visible += 1;
            });

            groups.forEach(function (group) {
                group.hidden = !group.querySelector("[data-rule-item]:not([hidden])");
            });

            count.textContent = visible + (visible === 1 ? " topic" : " topics");
        }

        [search, category].forEach(function (control) {
            control.addEventListener("input", applyFilters);
            control.addEventListener("change", applyFilters);
        });
        applyFilters();
    }

    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll("[data-rule-directory]").forEach(initializeDirectory);
    });
}());
