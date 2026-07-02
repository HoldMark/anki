document.addEventListener("DOMContentLoaded", () => {
});  // для запуска кода после загрузки DOM

{
    const hintsSpan = document.querySelector('.hints-span');
    const hideHintsSpan = document.querySelector('.hide-hints-span');

    // Если один из элементов отсутствует в DOM — ничего не делаем.
    if (hintsSpan && hideHintsSpan) {
        const hintText = hideHintsSpan.textContent.trim();

        // Поле подсказки пустое — скрываем весь блок «Hints:».
        if (!hintText) {
            hintsSpan.style.display = 'none';

        // Подсказка заканчивается на «;» — текст скрыт под спойлером.
        // CSS делает текст прозрачным с серым фоном (.hide-hints-span),
        // клик раскрывает его.
        } else if (hintText.endsWith(';')) {
            hintsSpan.style.cursor = 'pointer';
            hintsSpan.addEventListener('click', () => {
                // Убираем маскировку: фон исчезает, цвет текста становится обычным.
                hideHintsSpan.style.background = 'none';
                hideHintsSpan.style.color = '#000';
            });

        // Подсказка есть, но без «;» — показываем текст сразу, без спойлера.
        } else {
            hideHintsSpan.style.background = 'none';
            hideHintsSpan.style.color = '#000';
        }
    }
}
