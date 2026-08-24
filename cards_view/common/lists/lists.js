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
        const items = Array.from(container.childNodes).filter(
            (node) => node.nodeType === Node.ELEMENT_NODE && node.tagName === "P"
        );

        container.innerHTML = "";
        items.forEach((node, i) => {
            container.appendChild(buildItem(node, i + 1, interactive));
        });
    }

    const listBlock = document.querySelector(".list-block");
    if (listBlock) {
        buildList(listBlock);
    }
}
