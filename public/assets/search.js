(function () {
    "use strict";

    var indexPromise;
    var maximumResults = 20;

    function normalize(value) {
        return String(value || "").toLowerCase().replace(/\s+/g, " ").trim();
    }

    function searchDocuments(documents, query) {
        var terms = normalize(query).split(" ").filter(Boolean);

        if (!terms.length) {
            return [];
        }

        return documents
            .map(function (document) {
                var title = normalize(document.title);
                var headings = normalize(document.headings);
                var text = normalize(document.text);
                var combined = title + " " + headings + " " + text;

                if (!terms.every(function (term) {
                    return combined.indexOf(term) !== -1;
                })) {
                    return null;
                }

                var score = terms.reduce(function (total, term) {
                    if (title === term) {
                        total += 250;
                    } else if (title.indexOf(term) === 0) {
                        total += 140;
                    } else if (title.indexOf(term) !== -1) {
                        total += 90;
                    }

                    if (headings.indexOf(term) !== -1) {
                        total += 35;
                    }

                    if (text.indexOf(term) !== -1) {
                        total += 5;
                    }

                    return total;
                }, 0);

                return { document: document, score: score };
            })
            .filter(Boolean)
            .sort(function (left, right) {
                return right.score - left.score ||
                    left.document.title.localeCompare(right.document.title);
            })
            .slice(0, maximumResults)
            .map(function (result) {
                return result.document;
            });
    }

    function makeSnippet(document, query) {
        var text = String(document.text || "");
        var term = normalize(query).split(" ").filter(Boolean)[0] || "";
        var index = text.toLowerCase().indexOf(term);
        var start = Math.max(0, index > -1 ? index - 70 : 0);
        var end = Math.min(text.length, start + 180);
        var snippet = text.slice(start, end).trim();

        return (start > 0 ? "…" : "") + snippet +
            (end < text.length ? "…" : "");
    }

    function loadIndex() {
        if (!indexPromise) {
            indexPromise = fetch("/assets/search-index.json")
                .then(function (response) {
                    if (!response.ok) {
                        throw new Error("Search index could not be loaded.");
                    }

                    return response.json();
                });
        }

        return indexPromise;
    }

    function clearResults(results) {
        results.replaceChildren();
        results.hidden = true;
    }

    function renderResults(results, documents, query) {
        results.replaceChildren();

        if (!documents.length) {
            var empty = document.createElement("p");
            empty.className = "search-empty";
            empty.textContent = "No rules matched “" + query + "”.";
            results.appendChild(empty);
            results.hidden = false;
            return;
        }

        var list = document.createElement("ul");
        list.className = "search-results-list";

        documents.forEach(function (item) {
            var row = document.createElement("li");
            var link = document.createElement("a");
            var title = document.createElement("strong");
            var meta = document.createElement("span");
            var snippet = document.createElement("span");

            link.href = item.url;
            title.textContent = item.title;
            meta.className = "search-result-section";
            meta.textContent = item.section;
            snippet.className = "search-result-snippet";
            snippet.textContent = makeSnippet(item, query);

            link.append(title, meta, snippet);
            row.appendChild(link);
            list.appendChild(row);
        });

        results.appendChild(list);
        results.hidden = false;
    }

    function initializeSearch(form) {
        var input = form.querySelector("[data-search-input]");
        var results = form.querySelector("[data-search-results]");
        var timer;
        var currentResults = [];

        if (!input || !results) {
            return;
        }

        function runSearch() {
            var query = input.value.trim();

            if (query.length < 2) {
                currentResults = [];
                clearResults(results);
                return;
            }

            results.hidden = false;
            results.textContent = "Searching…";

            loadIndex()
                .then(function (documents) {
                    currentResults = searchDocuments(documents, query);
                    renderResults(results, currentResults, query);
                })
                .catch(function () {
                    results.textContent =
                        "Search is temporarily unavailable. Please try again.";
                });
        }

        input.addEventListener("input", function () {
            window.clearTimeout(timer);
            timer = window.setTimeout(runSearch, 120);
        });

        input.addEventListener("keydown", function (event) {
            if (event.key === "Escape") {
                input.value = "";
                currentResults = [];
                clearResults(results);
            } else if (event.key === "ArrowDown" && !results.hidden) {
                var firstLink = results.querySelector("a");

                if (firstLink) {
                    event.preventDefault();
                    firstLink.focus();
                }
            }
        });

        form.addEventListener("submit", function (event) {
            event.preventDefault();

            if (currentResults.length) {
                window.location.href = currentResults[0].url;
            } else {
                runSearch();
            }
        });

        document.addEventListener("click", function (event) {
            if (!form.contains(event.target)) {
                clearResults(results);
            }
        });
    }

    if (typeof document !== "undefined") {
        document.addEventListener("DOMContentLoaded", function () {
            document.querySelectorAll("[data-search-form]").forEach(
                initializeSearch
            );
        });
    }

    if (typeof module !== "undefined" && module.exports) {
        module.exports = {
            makeSnippet: makeSnippet,
            searchDocuments: searchDocuments
        };
    }
}());
