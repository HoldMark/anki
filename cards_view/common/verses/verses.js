document.addEventListener("DOMContentLoaded", () => {
});  // для запуска кода после загрузки DOM

{
    // Группирует <p>-строки в четверостишия по разделителям <br>.
    function groupLinesByStanza(container) {
        const stanzas = [[]];

        Array.from(container.childNodes).forEach((node) => {
            if (node.nodeType !== Node.ELEMENT_NODE) {
                return;
            }
            if (node.tagName === "BR") {
                stanzas.push([]);
            } else if (node.tagName === "P") {
                stanzas[stanzas.length - 1].push(node);
            }
        });

        return stanzas.filter((lines) => lines.length > 0);
    }

    // На лицевой стороне (interactive) каждая строка скрыта под спойлером
    // и открывается кликом по ней.
    function buildStanza(lines, interactive) {
        const stanza = document.createElement("div");
        stanza.className = "verse-stanza";

        const linesWrapper = document.createElement("div");
        linesWrapper.className = "stanza-lines";

        lines.forEach((line) => {
            line.classList.add("verse-line");

            if (interactive) {
                line.classList.add("verse-line-hidden");
                line.addEventListener("click", (event) => {
                    event.stopPropagation();
                    line.classList.toggle("verse-line-hidden");
                    line.classList.toggle("verse-line-revealed");
                });
            }

            linesWrapper.appendChild(line);
        });

        stanza.appendChild(linesWrapper);

        if (interactive) {
            // Клик мимо узкой раскрытой строки: находим строку по Y-координате
            // и переключаем её. Заодно гасит всплытие клика до stanza.
            linesWrapper.addEventListener("click", (event) => {
                event.stopPropagation();
                const y = event.clientY;
                const target = lines.find((line) => {
                    const rect = line.getBoundingClientRect();
                    return y >= rect.top && y <= rect.bottom;
                });
                if (target) {
                    target.classList.toggle("verse-line-hidden");
                    target.classList.toggle("verse-line-revealed");
                }
            });

            stanza.addEventListener("click", () => {
                const open = !lines.every((line) => line.classList.contains("verse-line-revealed"));
                lines.forEach((line) => {
                    line.classList.toggle("verse-line-hidden", !open);
                    line.classList.toggle("verse-line-revealed", open);
                });
            });
        }

        return stanza;
    }

    // Истинная ширина отрисованного текста строки (не зависит от ширины
    // охватывающего блока, в отличие от scrollWidth).
    function measureLineWidth(line) {
        const range = document.createRange();
        range.selectNodeContents(line);
        return range.getBoundingClientRect().width;
    }

    // Максимальная ширина строки по всему стиху — записывается в
    // --verse-max-line-width, см. style.css.
    function syncMaxLineWidth(container) {
        const lines = container.querySelectorAll(".verse-line");
        let maxWidth = 0;
        lines.forEach((line) => {
            maxWidth = Math.max(maxWidth, measureLineWidth(line));
        });
        if (maxWidth > 0) {
            container.style.setProperty("--verse-max-line-width", `${Math.ceil(maxWidth)}px`);
        }
    }

    function buildVerse(container) {
        const interactive = container.classList.contains("verse-block-hidden");
        const stanzasLines = groupLinesByStanza(container);

        container.innerHTML = "";
        const stanzas = stanzasLines.map((lines) => buildStanza(lines, interactive));
        stanzas.forEach((stanza) => container.appendChild(stanza));

        // Последнему четверостишию не нужен border-bottom-разделитель.
        const lastStanza = stanzas[stanzas.length - 1];
        if (lastStanza) {
            lastStanza.classList.add("verse-stanza-last");
        }

        syncMaxLineWidth(container);

        // Подстраховка: пересчёт после кадра отрисовки и на resize.
        requestAnimationFrame(() => requestAnimationFrame(() => syncMaxLineWidth(container)));
        window.addEventListener("resize", () => syncMaxLineWidth(container));
    }

    const verseBlock = document.querySelector(".verse-block");
    if (verseBlock) {
        buildVerse(verseBlock);
    }
}
