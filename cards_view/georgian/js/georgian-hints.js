document.addEventListener("DOMContentLoaded", () => {
});

{
    // Transcription is masked by default (learning pronunciation shouldn't be
    // spoiled by reading it) — click the field to reveal it.
    document.querySelectorAll(".trans-hint-span").forEach(hintSpan => {
        if (!hintSpan.textContent.trim()) {
            hintSpan.style.display = "none";
            return;
        }

        hintSpan.addEventListener("click", () => {
            hintSpan.classList.add("trans-revealed");
        });
    });
}
