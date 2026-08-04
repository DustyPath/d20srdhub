(function () {
    "use strict";

    function initializeDirectory(directory) {
        var search = directory.querySelector("[data-power-search]");
        var discipline = directory.querySelector("[data-power-discipline]");
        var level = directory.querySelector("[data-power-level]");
        var count = directory.querySelector("[data-power-count]");
        var groups = Array.from(directory.querySelectorAll("[data-power-group]"));
        var items = Array.from(directory.querySelectorAll("[data-power-item]"));

        function applyFilters() {
            var tokens = search.value.toLowerCase().trim().split(/\s+/).filter(Boolean);
            var visible = 0;
            items.forEach(function (item) {
                var nameMatches = tokens.every(function (token) {
                    return item.dataset.name.indexOf(token) !== -1;
                });
                var disciplineMatches = !discipline.value || item.dataset.discipline === discipline.value;
                var levels = item.dataset.levels.split(/\s+/).filter(Boolean);
                var levelMatches = !level.value || levels.indexOf(level.value) !== -1;
                var matches = nameMatches && disciplineMatches && levelMatches;
                item.hidden = !matches;
                if (matches) visible += 1;
            });
            groups.forEach(function (group) {
                group.hidden = !group.querySelector("[data-power-item]:not([hidden])");
            });
            count.textContent = visible + (visible === 1 ? " power" : " powers");
        }

        [search, discipline, level].forEach(function (control) {
            control.addEventListener("input", applyFilters);
            control.addEventListener("change", applyFilters);
        });
        applyFilters();
    }

    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll("[data-power-directory]").forEach(initializeDirectory);
    });
}());
