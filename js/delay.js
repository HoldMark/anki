document.addEventListener("DOMContentLoaded", () => {
});
{
    let blocked = false;

    // функция для включения блокировки
    function blockKeys(ms = 2000) {
        blocked = true;
        setTimeout(() => blocked = false, ms);
    }

    // блокируем клавиши 1–4 при необходимости
    document.addEventListener('keydown', (e) => {
        if (["1", "2", "3", "4"].includes(e.key) && blocked) {
            console.log("button was pressed");
            e.preventDefault();
            e.stopPropagation();
            return false;
        }
    });

    function checkAnswer() {
        let is_incorrect = document.querySelector('#typearrow');
        console.log(is_incorrect);

        if (is_incorrect) {
            console.log("delay pressing the buttons for some time");
            blockKeys(3000); // блокируем клавиши на 3 секунды
        }
    }
    checkAnswer()
}