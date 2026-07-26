(function () {
    "use strict";

    var minimumHeadings = 3;

    function slugify(value) {
        return String(value || "")
            .toLowerCase()
            .normalize("NFKD")
            .replace(/[\u0300-\u036f]/g, "")
            .replace(/[^a-z0-9]+/g, "-")
            .replace(/^-+|-+$/g, "") || "section";
    }

    function ensureHeadingId(heading, usedIds) {
        var base = heading.id || slugify(heading.textContent);
        var candidate = base;
        var suffix = 2;

        while (usedIds.has(candidate)) {
            candidate = base + "-" + suffix;
            suffix += 1;
        }

        heading.id = candidate;
        usedIds.add(candidate);
        return candidate;
    }

    function buildTableOfContents(article) {
        var headings = Array.from(article.querySelectorAll("h2, h3"));

        if (headings.length < minimumHeadings) {
            return null;
        }

        var usedIds = new Set(
            Array.from(document.querySelectorAll("[id]"))
                .map(function (element) {
                    return element.id;
                })
                .filter(Boolean)
        );
        var details = document.createElement("details");
        var summary = document.createElement("summary");
        var list = document.createElement("ol");
        var links = [];

        headings.forEach(function (heading) {
            usedIds.delete(heading.id);
        });

        details.className = "page-toc";
        details.open = true;
        summary.textContent = "On this page";
        list.className = "page-toc-list";

        headings.forEach(function (heading) {
            var id = ensureHeadingId(heading, usedIds);
            var item = document.createElement("li");
            var link = document.createElement("a");

            item.className = "page-toc-" + heading.tagName.toLowerCase();
            link.href = "#" + id;
            link.textContent = heading.textContent.trim();
            link.dataset.tocTarget = id;
            item.appendChild(link);
            list.appendChild(item);
            links.push(link);
        });

        details.append(summary, list);
        article.insertBefore(details, headings[0]);

        if ("IntersectionObserver" in window) {
            var observer = new IntersectionObserver(function (entries) {
                entries.forEach(function (entry) {
                    if (!entry.isIntersecting) {
                        return;
                    }

                    links.forEach(function (link) {
                        link.removeAttribute("aria-current");
                    });

                    details.querySelector(
                        '[data-toc-target="' + entry.target.id + '"]'
                    )?.setAttribute("aria-current", "location");
                });
            }, {
                rootMargin: "-15% 0px -70% 0px"
            });

            headings.forEach(function (heading) {
                observer.observe(heading);
            });
        }

        return details;
    }

    if (typeof document !== "undefined") {
        document.addEventListener("DOMContentLoaded", function () {
            var article = document.querySelector(".article-card");

            if (article) {
                buildTableOfContents(article);
            }
        });
    }

    if (typeof module !== "undefined" && module.exports) {
        module.exports = {
            slugify: slugify
        };
    }
}());
