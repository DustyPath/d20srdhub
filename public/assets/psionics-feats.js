(function () {
    "use strict";

    function initialize(directory) {
        var search = directory.querySelector("[data-psionic-feat-search]");
        var type = directory.querySelector("[data-psionic-feat-type]");
        var count = directory.querySelector("[data-psionic-feat-count]");
        var items = Array.from(directory.querySelectorAll("[data-psionic-feat]"));

        function applyFilters() {
            var tokens = search.value.toLowerCase().trim().split(/\s+/).filter(Boolean);
            var visible = 0;
            items.forEach(function (item) {
                var nameMatches = tokens.every(function (token) {
                    return item.dataset.name.indexOf(token) !== -1;
                });
                var typeMatches = !type.value || item.dataset.type === type.value;
                item.hidden = !(nameMatches && typeMatches);
                if (!item.hidden) visible += 1;
            });
            count.textContent = visible + (visible === 1 ? " feat" : " feats");
        }

        [search, type].forEach(function (control) {
            control.addEventListener("input", applyFilters);
            control.addEventListener("change", applyFilters);
        });
        applyFilters();
    }

    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll("[data-psionic-feat-directory]").forEach(initialize);
    });
}());
