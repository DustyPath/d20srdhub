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
        results.closest("[data-search-form]")
            ?.querySelector("[data-search-input]")
            ?.setAttribute("aria-expanded", "false");
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

        var input = results.closest("[data-search-form]")
            ?.querySelector("[data-search-input]");

        if (input) {
            input.setAttribute("aria-expanded", "true");
        }
    }

    function initializeSearch(form) {
        var input = form.querySelector("[data-search-input]");
        var results = form.querySelector("[data-search-results]");
        var timer;
        var currentResults = [];

        if (!input || !results) {
            return;
        }

        if (!results.id) {
            results.id = "search-results";
        }

        input.setAttribute("aria-controls", results.id);
        input.setAttribute("aria-expanded", "false");
        input.setAttribute("aria-autocomplete", "list");

        function focusResult(direction) {
            var links = Array.from(results.querySelectorAll("a"));
            var currentIndex = links.indexOf(document.activeElement);

            if (!links.length) {
                return;
            }

            var nextIndex;

            if (currentIndex === -1) {
                nextIndex = direction > 0 ? 0 : links.length - 1;
            } else {
                nextIndex = (currentIndex + direction + links.length) %
                    links.length;
            }

            links[nextIndex].focus();
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
            input.setAttribute("aria-expanded", "true");

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
                event.preventDefault();
                focusResult(1);
            }
        });

        results.addEventListener("keydown", function (event) {
            if (event.key === "ArrowDown") {
                event.preventDefault();
                focusResult(1);
            } else if (event.key === "ArrowUp") {
                event.preventDefault();
                focusResult(-1);
            } else if (event.key === "Escape") {
                event.preventDefault();
                input.focus();
                input.value = "";
                currentResults = [];
                clearResults(results);
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

        document.addEventListener("keydown", function (event) {
            var target = event.target;
            var isTyping = target instanceof HTMLInputElement ||
                target instanceof HTMLTextAreaElement ||
                target?.isContentEditable;

            if (event.key === "/" && !isTyping &&
                    !event.metaKey && !event.ctrlKey && !event.altKey) {
                event.preventDefault();
                input.focus();
                input.select();
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
