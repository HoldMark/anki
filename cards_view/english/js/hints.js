document.addEventListener("DOMContentLoaded", () => {
});  // для запуска кода после загрузки DOM
{
    const hintsSpan = document.querySelector('.hints-span');
    const hideHintsSpan = document.querySelector('.hide-hints-span');

    if (hintsSpan && hideHintsSpan) {
        if (!hideHintsSpan.textContent.trim()) {
            hintsSpan.style.display = 'none';
            console.log('Hide hints span');
        } else {
            hintsSpan.addEventListener('click', () => {
                hideHintsSpan.style.background = 'none';
                hideHintsSpan.style.color = '#000';
                console.log('Show hints span');
            });
        }
    }
}
