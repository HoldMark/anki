document.addEventListener("DOMContentLoaded", () => {
});  // для запуска кода после загрузки DOM

{
    // Оборачивает один пункт списка: видимый номер + текст под спойлером.
    function buildItem(node, index, interactive) {
        const item = document.createElement("div");
        item.className = "list-item";

        const number = document.createElement("span");
        number.className = "list-item-number";
        number.textContent = `${index}.`;

        const text = document.createElement("span");
        text.className = "list-item-text";
        text.innerHTML = node.innerHTML;

        item.appendChild(number);
        item.appendChild(text);

        if (interactive) {
            text.classList.add("list-item-text-hidden");
            // Каждый пункт переключается независимо — открытия всего списка разом нет.
            item.addEventListener("click", () => {
                text.classList.toggle("list-item-text-hidden");
                text.classList.toggle("list-item-text-revealed");
            });
        }

        return item;
    }

    function buildList(container) {
        const interactive = container.classList.contains("list-block-hidden");
        const childNodes = Array.from(container.childNodes);
        const items = childNodes.filter(
            (node) => node.nodeType === Node.ELEMENT_NODE && node.tagName === "P"
        );
        // Всё, что не завёрнуто в <p> — доп. текст, не входящий в пронумерованный список.
        const extraNodes = childNodes.filter((node) => !items.includes(node));
        const hasExtraContent = extraNodes.some((node) => node.textContent.trim());

        container.innerHTML = "";
        items.forEach((node, i) => {
            container.appendChild(buildItem(node, i + 1, interactive));
        });

        // Доп. текст показываем только на задней стороне карточки — на лицевой это был бы спойлер без номера.
        if (!interactive && hasExtraContent) {
            const extra = document.createElement("div");
            extra.className = "list-extra";
            extraNodes.forEach((node) => extra.appendChild(node));
            container.appendChild(extra);
        }
    }

    const listBlock = document.querySelector(".list-block");
    if (listBlock) {
        buildList(listBlock);
    }
}
