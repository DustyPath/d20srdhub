(function () {
    "use strict";

    function initializeDirectory(directory) {
        var search = directory.querySelector("[data-spell-search]");
        var school = directory.querySelector("[data-spell-school]");
        var level = directory.querySelector("[data-spell-level]");
        var count = directory.querySelector("[data-spell-count]");
        var groups = Array.from(directory.querySelectorAll("[data-spell-group]"));
        var items = Array.from(directory.querySelectorAll("[data-spell-item]"));

        function applyFilters() {
            var query = search.value.toLowerCase().trim();
            var selectedSchool = school.value;
            var selectedLevel = level.value;
            var visible = 0;

            items.forEach(function (item) {
                var nameMatches = !query ||
                    item.dataset.name.indexOf(query) !== -1;
                var schoolMatches = !selectedSchool ||
                    item.dataset.school === selectedSchool;
                var levels = (item.dataset.levels || "").split(",");
                var levelMatches = !selectedLevel ||
                    levels.includes(selectedLevel);
                var matches = nameMatches && schoolMatches && levelMatches;

                item.hidden = !matches;

                if (matches) {
                    visible += 1;
                }
            });

            groups.forEach(function (group) {
                group.hidden = !group.querySelector(
                    "[data-spell-item]:not([hidden])"
                );
            });

            count.textContent = visible + (visible === 1 ? " spell" : " spells");
        }

        [search, school, level].forEach(function (control) {
            control.addEventListener("input", applyFilters);
            control.addEventListener("change", applyFilters);
        });

        applyFilters();
    }

    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll("[data-spell-directory]").forEach(
            initializeDirectory
        );
    });
}());
