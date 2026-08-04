document.addEventListener("DOMContentLoaded", () => {
});  // для запуска кода после загрузки DOM

{
    // Разбивает содержимое блока стиха на четверостишия.
    // Внутри поля {{answer}} каждая строка сохранена в <p>, а <br>
    // отделяет одно четверостишие от другого.
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
    // (как .hide-hints-span) и открывается кликом по ней. Клик по строке
    // останавливает всплытие (stopPropagation), поэтому клик по самой
    // строке и клик по рамке/отступам четверостишия вокруг строк —
    // два явно разных, не пересекающихся способа открыть текст.
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
            // Клик в зазор между строками попадает на linesWrapper, а не на
            // конкретную <p>, и без этого всплывал бы до stanza и открывал
            // всё четверостишие. Гасим его здесь, чтобы «открыть всё»
            // срабатывало только на рамке/отступах вокруг строк.
            linesWrapper.addEventListener("click", (event) => {
                event.stopPropagation();
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

    function buildVerse(container) {
        const interactive = container.classList.contains("verse-block-hidden");
        const stanzasLines = groupLinesByStanza(container);

        container.innerHTML = "";
        const stanzas = stanzasLines.map((lines) => buildStanza(lines, interactive));
        stanzas.forEach((stanza) => container.appendChild(stanza));

        // Разделительная линия между четверостишиями задаётся через
        // border-bottom у каждого .verse-stanza, а не :last-child в CSS —
        // последнему четверостишию она не нужна, снимаем явно.
        const lastStanza = stanzas[stanzas.length - 1];
        if (lastStanza) {
            lastStanza.classList.add("verse-stanza-last");
        }
    }

    const verseBlock = document.querySelector(".verse-block");
    if (verseBlock) {
        buildVerse(verseBlock);
    }
}
