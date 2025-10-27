document.addEventListener("DOMContentLoaded", () => {
});
{
    console.log('binding listener');
    if (!window._reviewShortcutBound) {
        window._reviewShortcutBound = true;
        document.addEventListener("keydown", function (e) {
            if (e.metaKey && e.key === "/") {
                e.preventDefault(); // optional, stops default action
                console.log("Shortcut triggered");
                requestTaskReview(); // run your action
            }
        });
    }

    function requestTaskReview() {
        // Сбор и отправка данных на проверку в python

        let fieldValue = document.querySelector("#typeans")?.value;

        let card_word = document.querySelector('.condition_block').getAttribute('data-word');
        let card_pos = document.querySelector('.condition_block').getAttribute('data-pos');
        let card_def = document.querySelector('.condition_block').getAttribute('data-def');

        let card_tense = document.querySelector('.condition_tense_value').innerHTML;
        let card_usage = document.querySelector('.condition_usage_value').innerHTML;
        let card_sentence_type = document.querySelector('.condition_sentence_type_value').innerHTML;
        let card_pronoun = document.querySelector('.condition_pronoun_value').innerHTML;

        console.log("Data collected for sending to Python");

    function sendDataToPython() {
        // Отправка данных в Python через pycmd
        data_to_python = JSON.stringify({
            action: "check grammar and other",
            word: card_word,
            pos: card_pos,
            definition: card_def,
            tense: card_tense,
            usage: card_usage,
            sentence_type: card_sentence_type,
            card_pronoun: card_pronoun,
            sentence: fieldValue,
        }); 
        pycmd(data_to_python);
        console.log("Sent to Python:", data_to_python);
      }
        sendDataToPython();
    }
    function receiveReviewResponse(result) {
        // Обработка полученного результата от Python
        console.log("Received from Python:", result);

        if (result.result): {
            alert("Error, please try again!");
            return;
        }

        let card_usage = document.querySelector('.condition_usage_value').innerHTML;
        let card_sentence_type = document.querySelector('.condition_sentence_type_value').innerHTML;
        let text = result.text;
        let is_word = result.is_word;
        let is_pos = result.is_part_of_speech;
        let is_definition = result.is_definition;
        let is_tense = result.is_tense;
        let is_usage = result.is_usage;
        let is_sentence_type = result.is_sentence_type;
        let is_pronoun = result.is_pronoun;

        let grammar_correctness = result.grammar_correctness;
        let correct_version = result.correct_version;
        let errors_with_grammar = result.errors_with_grammar;
        let style_suggestions = result.style_suggestions;
        let explanation_of_text = result.explanation_of_text;

        // изменение цвета - если true то #00671c, если false то #aa0a0a
        
        document.querySelector('.condition_tense > .condition_name').style.color = is_tense ? '#00671c' : '#aa0a0a';
        document.querySelector('.condition_pronoun > .condition_name').style.color = is_pronoun ? '#00671c' : '#aa0a0a';
        
        if (card_usage !== "null") {
            document.querySelector('.condition_usage > .condition_name').style.color = is_usage ? '#00671c' : '#aa0a0a';
        }
        if (card_sentence_type !== "null") {
            document.querySelector('.condition_sentence_type > .condition_name').style.color = is_sentence_type ? '#00671c' : '#aa0a0a';
        }
        
        // изменение цвета для word, pos, definition, correctness
        document.querySelector('.review_word > .review_name').style.color = is_word ? '#00671c' : '#aa0a0a';
        document.querySelector('.review_pos > .review_name').style.color = is_pos ? '#00671c' : '#aa0a0a';
        document.querySelector('.review_definition > .review_name').style.color = is_definition ? '#00671c' : '#aa0a0a';
        document.querySelector('.review_correctness > .review_name').style.color = grammar_correctness ? '#00671c' : '#aa0a0a';
        
        // отображение результата word, pos, definition, correctness
        document.querySelector('.review_word_value').innerHTML = is_word;
        document.querySelector('.review_pos_value').innerHTML = is_pos;
        document.querySelector('.review_definition_value').innerHTML = is_definition;
        document.querySelector('.review_correctness_value').innerHTML = grammar_correctness;

        
        // отображение блоков с ревью
        document.querySelector('.review_result_block').style.display = 'block';
        document.querySelector('.review_text_block').style.display = 'block';
        
        // отображение правильной версии
        if (!grammar_correctness) {
            document.querySelector('.correct_version').style.display = 'inline-block';
            document.querySelector('.review_correct_version_value').innerHTML = correct_version;
        }
        
        // вывод списка ошибок
        if (errors_with_grammar.length > 0) {

            document.querySelector('.grammar_errors').style.display = 'inline-block';
            let grammar_errors_html = document.querySelector('.review_grammar_errors_value');

            let ul = document.createElement('ul');
            errors_with_grammar.forEach(suggestion => {
                let li = document.createElement('li');
                li.textContent = suggestion;
                ul.appendChild(li);
            });
            
            grammar_errors_html.innerHTML = '';
            grammar_errors_html.appendChild(ul);
            
        }

        // вывод списка предложений по стилю
        if (style_suggestions.length > 0) {

            document.querySelector('.style_suggestions').style.display = 'inline-block';
            let style_suggestions_html = document.querySelector('.review_style_suggestions_value');

            let ul = document.createElement('ul');
            style_suggestions.forEach(suggestion => {
                let li = document.createElement('li');
                li.textContent = suggestion;
                ul.appendChild(li);
            });
            
            style_suggestions_html.innerHTML = '';
            style_suggestions_html.appendChild(ul);
            
        }

        // вывод объяснения
        document.querySelector('.explanation_of_text').style.display = 'inline-block';
        document.querySelector('.review_explanation_of_text_value').innerHTML = explanation_of_text;

        // вывод отправленного текста
        document.querySelector('.sent_text').style.display = 'inline-block';
        document.querySelector('.review_sent_text_value').innerHTML = text;
    }
}