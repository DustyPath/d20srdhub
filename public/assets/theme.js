(function () {
    "use strict";

    var storageKey = "d20srdhub-theme";

    function currentTheme() {
        return document.documentElement.dataset.theme || "light";
    }

    function updateToggle(button) {
        var dark = currentTheme() === "dark";

        button.textContent = dark ? "☀ Light" : "☾ Dark";
        button.setAttribute(
            "aria-label",
            dark ? "Use light theme" : "Use dark theme"
        );
        button.setAttribute("aria-pressed", String(dark));
    }

    function setTheme(theme, remember) {
        document.documentElement.dataset.theme = theme;

        if (remember) {
            try {
                window.localStorage.setItem(storageKey, theme);
            } catch (error) {
                // The selected theme still applies when storage is unavailable.
            }
        }

        document.querySelectorAll("[data-theme-toggle]").forEach(updateToggle);
    }

    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll("[data-theme-toggle]").forEach(
            function (button) {
                updateToggle(button);
                button.addEventListener("click", function () {
                    setTheme(currentTheme() === "dark" ? "light" : "dark", true);
                });
            }
        );

        var media = window.matchMedia("(prefers-color-scheme: dark)");

        media.addEventListener?.("change", function (event) {
            try {
                if (window.localStorage.getItem(storageKey)) {
                    return;
                }
            } catch (error) {
                return;
            }

            setTheme(event.matches ? "dark" : "light", false);
        });
    });
}());
