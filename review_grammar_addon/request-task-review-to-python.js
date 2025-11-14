document.addEventListener("DOMContentLoaded", () => {
    // Fuck camelCase;
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

        let cardWord = document.querySelector('.condition-block').getAttribute('data-word');
        let cardPos = document.querySelector('.condition-block').getAttribute('data-pos');
        let cardDef = document.querySelector('.condition-block').getAttribute('data-def');

        let cardTense = document.querySelector('.condition-tense-value').innerHTML;
        let cardUsage = document.querySelector('.condition-usage-value').innerHTML;
        let cardSentenceType = document.querySelector('.condition-sentence-type-value').innerHTML;
        let cardPronoun = document.querySelector('.condition-pronoun-value').innerHTML;

        console.log("Data collected for sending to Python");

    function sendDataToPython() {
        // Отправка данных в Python через pycmd
        dataToPython = JSON.stringify({
            action: "check grammar and other",
            word: cardWord,
            pos: cardPos,
            definition: cardDef,
            tense: cardTense,
            usage: cardUsage,
            sentence_type: cardSentenceType,
            card_pronoun: cardPronoun,
            sentence: fieldValue,
        }); 
        pycmd(dataToPython);
        console.log("Sent to Python:", dataToPython);
      }
        sendDataToPython();
    }
    function receiveReviewResponse(result) {
        // Обработка полученного результата от Python
        console.log("Received from Python:", result);

        if (result.result) {
            alert("Error, please try again!");
            return;
        }

        let cardUsage = document.querySelector('.condition-usage-value').innerHTML;
        let cardSentenceType = document.querySelector('.condition-sentence-type-value').innerHTML;
        let text = result.text;
        let isWord = result.isWord;
        let isPos = result.is_part_of_speech;
        let isDefinition = result.is_definition;
        let isTense = result.is_tense;
        let isUsage = result.is_usage;
        let isSentenceType = result.is_sentence_type;
        let isPronoun = result.is_pronoun;

        let grammarCorrectness = result.grammar_correctness;
        let correctVersion = result.correct_version;
        let errorsWithGrammar = result.errors_with_grammar;
        let styleSuggestions = result.style_suggestions;
        let explanationOfText = result.explanation_of_text;

        // изменение цвета - если true то #00671c, если false то #aa0a0a
        
        document.querySelector('.condition-tense > .condition-name').style.color = isTense ? '#00671c' : '#aa0a0a';
        document.querySelector('.condition-pronoun > .condition-name').style.color = isPronoun ? '#00671c' : '#aa0a0a';
        
        if (cardUsage !== "null") {
            document.querySelector('.condition-usage > .condition-name').style.color = isUsage ? '#00671c' : '#aa0a0a';
        }
        if (cardSentenceType !== "null") {
            document.querySelector('.condition-sentence-type > .condition-name').style.color = isSentenceType ? '#00671c' : '#aa0a0a';
        }
        
        // изменение цвета для word, pos, definition, correctness
        document.querySelector('.review-word > .review-name').style.color = isWord ? '#00671c' : '#aa0a0a';
        document.querySelector('.review-pos > .review-name').style.color = isPos ? '#00671c' : '#aa0a0a';
        document.querySelector('.review-definition > .review-name').style.color = isDefinition ? '#00671c' : '#aa0a0a';
        document.querySelector('.review-correctness > .review-name').style.color = grammarCorrectness ? '#00671c' : '#aa0a0a';
        
        // отображение результата word, pos, definition, correctness
        document.querySelector('.review-word-value').innerHTML = isWord;
        document.querySelector('.review-pos-value').innerHTML = isPos;
        document.querySelector('.review-definition-value').innerHTML = isDefinition;
        document.querySelector('.review-correctness-value').innerHTML = grammarCorrectness;

        
        // отображение блоков с ревью
        document.querySelector('.review-result-block').style.display = 'block';
        document.querySelector('.review-text-block').style.display = 'block';
        
        // отображение правильной версии
        if (!grammarCorrectness) {
            document.querySelector('.correct-version').style.display = 'inline-block';
            document.querySelector('.review-correct-version-value').innerHTML = correctVersion;
        }
        
        // вывод списка ошибок
        if (errorsWithGrammar.length > 0) {

            document.querySelector('.grammar-errors').style.display = 'inline-block';
            let grammarErrorsHtml = document.querySelector('.review-grammar-errors-value');

            let ul = document.createElement('ul');
            errorsWithGrammar.forEach(suggestion => {
                let li = document.createElement('li');
                li.textContent = suggestion;
                ul.appendChild(li);
            });
            
            grammarErrorsHtml.innerHTML = '';
            grammarErrorsHtml.appendChild(ul);
            
        }

        // вывод списка предложений по стилю
        if (styleSuggestions.length > 0) {

            document.querySelector('.style-suggestions').style.display = 'inline-block';
            let styleSuggestionsHtml = document.querySelector('.review-style-suggestions-value');

            let ul = document.createElement('ul');
            styleSuggestions.forEach(suggestion => {
                let li = document.createElement('li');
                li.textContent = suggestion;
                ul.appendChild(li);
            });
            
            styleSuggestionsHtml.innerHTML = '';
            styleSuggestionsHtml.appendChild(ul);
            
        }

        // вывод объяснения
        document.querySelector('.explanation-of-text').style.display = 'inline-block';
        document.querySelector('.review-explanation-of-text-value').innerHTML = explanationOfText;

        // вывод отправленного текста
        document.querySelector('.sent-text').style.display = 'inline-block';
        document.querySelector('.review-sent-text-value').innerHTML = text;
    }
}