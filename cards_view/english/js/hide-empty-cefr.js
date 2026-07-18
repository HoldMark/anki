document.addEventListener("DOMContentLoaded", () => {
});

{
    // show the cefr block (and its divider) only when the cefr field has content

    const definitionTextBlock = document.querySelector('.definition-text-block');
    const cefrSpan = document.querySelector('.cefr-span');

    if (definitionTextBlock && cefrSpan) {
        if (cefrSpan.textContent.trim()) {
            definitionTextBlock.classList.add('has-cefr');
        } else {
            cefrSpan.style.display = 'none';
        }
    }
}
