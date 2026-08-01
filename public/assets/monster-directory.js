(function () {
    "use strict";

    function initializeDirectory(directory) {
        var search = directory.querySelector("[data-monster-search]");
        var type = directory.querySelector("[data-monster-type]");
        var challengeRating = directory.querySelector("[data-monster-cr]");
        var count = directory.querySelector("[data-monster-count]");
        var groups = Array.from(directory.querySelectorAll("[data-monster-group]"));
        var items = Array.from(directory.querySelectorAll("[data-monster-item]"));

        function applyFilters() {
            var tokens = search.value.toLowerCase().trim().split(/\s+/).filter(Boolean);
            var visible = 0;
            items.forEach(function (item) {
                var nameMatches = tokens.every(function (token) {
                    return item.dataset.name.indexOf(token) !== -1;
                });
                var typeMatches = !type.value || item.dataset.type === type.value;
                var crMatches = !challengeRating.value || item.dataset.cr === challengeRating.value;
                var matches = nameMatches && typeMatches && crMatches;
                item.hidden = !matches;
                if (matches) visible += 1;
            });
            groups.forEach(function (group) {
                group.hidden = !group.querySelector("[data-monster-item]:not([hidden])");
            });
            count.textContent = visible + (visible === 1 ? " monster" : " monsters");
        }

        [search, type, challengeRating].forEach(function (control) {
            control.addEventListener("input", applyFilters);
            control.addEventListener("change", applyFilters);
        });

        document.querySelectorAll("[data-monster-type-card]").forEach(function (card) {
            card.addEventListener("click", function () {
                type.value = card.dataset.monsterTypeCard;
                applyFilters();
            });
        });
        applyFilters();
    }

    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll("[data-monster-directory]").forEach(initializeDirectory);
    });
}());
