document.addEventListener("DOMContentLoaded", () => {
});
{
    // Получаем данные о текущей карточке
    let cardWord = document.querySelector('.condition-block').getAttribute('data-word');
    let cardPos = document.querySelector('.condition-block').getAttribute('data-pos');
    let cardDef = document.querySelector('.condition-block').getAttribute('data-def');


    function requestForTask() {
        // Отправка данных в Python через pycmd
        dataToSend = JSON.stringify({
            action: "task_for_card_with_eng_word",
            word: cardWord,
            pos: cardPos,
            definition: cardDef
        });
        pycmd(dataToSend);
        console.log("Sent to Python:", dataToSend);
    }

    function receiveTask(result) {
        // Получение результата и вставка в HTML

        console.log("Received from Python:", result);
        
        let cardTense = result.tense;
        let cardTenseLink = result.obsidian_link;
        let cardUsage = result.usage ? result.usage : "null";
        let cardSentence = result.sentence_type ? result.sentence_type : "null";
        let cardPronoun = result.pronoun;

        document.querySelector('.condition-tense-value').innerHTML = cardTense;
        document.querySelector('.condition-tense-value').setAttribute("href", cardTenseLink);
        document.querySelector('.condition-usage-value').innerHTML = cardUsage;
        document.querySelector('.condition-sentence-type-value').innerHTML = cardSentence;
        document.querySelector('.condition-pronoun-value').innerHTML = cardPronoun;

        console.log("Implemented data in HTML");
    }

    requestForTask();
}
