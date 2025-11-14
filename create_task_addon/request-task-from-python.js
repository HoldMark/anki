document.addEventListener("DOMContentLoaded", () => {
});
{
    // Получаем данные о текущей карточке
    let card_word = document.querySelector('.condition-block').getAttribute('data-word');
    let card_pos = document.querySelector('.condition-block').getAttribute('data-pos');
    let card_def = document.querySelector('.condition-block').getAttribute('data-def');


    function requestForTask() {
        // Отправка данных в Python через pycmd
        data_to_send = JSON.stringify({
            action: "task_for_card_with_eng_word",
            word: card_word,
            pos: card_pos,
            definition: card_def
        });
        pycmd(data_to_send);
        console.log("Sent to Python:", data_to_send);
    }

    function receiveTask(result) {
        // Получение результата и вставка в HTML

        console.log("Received from Python:", result);
        
        let card_tense = result.tense;
        let card_tense_link = result.obsidian_link;
        let card_usage = result.usage ? result.usage : "null";
        let card_sentence = result.sentence_type ? result.sentence_type : "null";
        let card_pronoun = result.pronoun;

        document.querySelector('.condition-tense-value').innerHTML = card_tense;
        document.querySelector('.condition-tense-value').setAttribute("href", card_tense_link);
        document.querySelector('.condition-usage-value').innerHTML = card_usage;
        document.querySelector('.condition-sentence-type-value').innerHTML = card_sentence;
        document.querySelector('.condition-pronoun-value').innerHTML = card_pronoun;

        console.log("Implemented data in HTML");
    }

    requestForTask();
}
