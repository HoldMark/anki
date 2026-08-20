document.addEventListener("DOMContentLoaded", () => {
});

{
    // accordion: open by default, click a header to collapse/expand its block.
    // Shared by every .basic-block that has a .collapsible-header (images, other meanings, ...).
    document.querySelectorAll(".collapsible-header").forEach(header => {
        const block = header.closest(".basic-block");
        // word-tree.js marks a failed parse as word-tree-error and leaves it non-interactive.
        if (!block || block.classList.contains("word-tree-error")) {
            return;
        }

        header.addEventListener("click", () => {
            block.classList.toggle("collapsed");
        });
    });
}
