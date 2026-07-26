(function () {
    "use strict";

    var storageKey = "d20srdhub-bookmarks";
    var bookmarks = readBookmarks();

    function readBookmarks() {
        try {
            var saved = JSON.parse(window.localStorage.getItem(storageKey));
            return Array.isArray(saved) ? saved : [];
        } catch (error) {
            return [];
        }
    }

    function writeBookmarks() {
        try {
            window.localStorage.setItem(
                storageKey,
                JSON.stringify(bookmarks.slice(0, 200))
            );
        } catch (error) {
            // Bookmarks still work for this tab if storage is unavailable.
        }
    }

    function currentPage() {
        var canonical = document.querySelector('link[rel="canonical"]');
        var heading = document.querySelector(".article-card h1, .article-card h2");
        var url;

        try {
            url = canonical ? new URL(canonical.href).pathname : location.pathname;
        } catch (error) {
            url = location.pathname;
        }

        return {
            title: heading?.textContent.trim() ||
                document.title.replace(/\s*\|\s*d20 SRD Hub$/, ""),
            url: url
        };
    }

    function isSaved(url) {
        return bookmarks.some(function (bookmark) {
            return bookmark.url === url;
        });
    }

    function updateButton(button, saved) {
        button.setAttribute("aria-pressed", String(saved));
        button.textContent = saved ? "★ Saved" : "☆ Save rule";
    }

    function initializeButton(button) {
        var page = currentPage();

        updateButton(button, isSaved(page.url));
        button.addEventListener("click", function () {
            var saved = isSaved(page.url);

            if (saved) {
                bookmarks = bookmarks.filter(function (bookmark) {
                    return bookmark.url !== page.url;
                });
            } else {
                bookmarks.unshift(page);
            }

            writeBookmarks();
            updateButton(button, !saved);
        });
    }

    function renderBookmarks(container) {
        container.replaceChildren();

        if (!bookmarks.length) {
            var empty = document.createElement("p");
            empty.className = "bookmarks-empty";
            empty.textContent =
                "You have not saved any rules yet. Use “Save rule” on any rules page.";
            container.appendChild(empty);
            return;
        }

        var list = document.createElement("ul");
        list.className = "bookmarks-list";

        bookmarks.forEach(function (bookmark) {
            var item = document.createElement("li");
            var link = document.createElement("a");
            var remove = document.createElement("button");

            link.href = bookmark.url;
            link.textContent = bookmark.title;
            remove.type = "button";
            remove.textContent = "Remove";
            remove.setAttribute("aria-label", "Remove " + bookmark.title);
            remove.addEventListener("click", function () {
                bookmarks = bookmarks.filter(function (saved) {
                    return saved.url !== bookmark.url;
                });
                writeBookmarks();
                renderBookmarks(container);
            });

            item.append(link, remove);
            list.appendChild(item);
        });

        container.appendChild(list);
    }

    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll("[data-bookmark-page]").forEach(
            initializeButton
        );
        document.querySelectorAll("[data-bookmarks-list]").forEach(
            renderBookmarks
        );
    });
}());
