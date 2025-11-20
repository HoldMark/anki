document.addEventListener("DOMContentLoaded", () => {
});  // для запуска кода после загрузки DOM

{
    // copy script

    document.querySelector(".copy-icon").addEventListener('click', () => {
        const input = document.getElementById('typeans');
        const temp = document.createElement('textarea'); // Создаём временное textarea

        // before review

        let cardWord = document.querySelector('.condition-block').getAttribute('data-word');
        let cardPos = document.querySelector('.condition-block').getAttribute('data-pos');
        let cardDef = document.querySelector('.condition-block').getAttribute('data-def');

        let cardTenseElement = document.querySelector(".condition-tense-value");
        let cardUsageElement = document.querySelector(".condition-usage-value");
        let cardSentenceTypeElement = document.querySelector(".condition-sentence-type-value");
        let cardPronounElement = document.querySelector(".condition-pronoun-value");

        // after review

        let reviewWordEl = document.querySelector(".review-word-value");
        let reviewPosEl = document.querySelector(".review-pos-value");
        let reviewDefEl = document.querySelector(".review-definition-value");
        let reviewCorrectnessEl = document.querySelector(".review-correctness-value");

        let reviewCorrectVersionEl = document.querySelector(".review-correct-version-value");
        let reviewExplanationOfTextEl = document.querySelector(".review-explanation-of-text-value");

        let reviewGrammarErrorsEls = document.querySelectorAll(".review-grammar-errors-value li");
        let reviewStyleSuggestionsEls = document.querySelectorAll(".review-style-suggestions-value li");

        // сборка строк

        let inputText = "text: " + input.value + "\n";

            // word
        let wordLine = "word: " + cardWord + "\n";
        let posLine = "part of speech: " + cardPos + "\n";
        let defLine = "definition: " + cardDef + "\n";

            // condition
        let tenseLine = "tense: " + (cardTenseElement ? cardTenseElement.innerHTML : '') + "\n";
        let usageLine = "usage: " + (cardUsageElement ? cardUsageElement.innerHTML : '') + "\n";
        let sentenceTypeLine = "sentence type: " + (cardSentenceTypeElement ? cardSentenceTypeElement.innerHTML : '') + "\n";
        let pronounLine = "pronoun: " + (cardPronounElement ? cardPronounElement.innerHTML : '') + "\n";

            // review
        let reviewWordLine = "review word: " + (reviewWordEl ? reviewWordEl.innerHTML : '') + "\n";
        let reviewPosLine = "review pos: " + (reviewPosEl ? reviewPosEl.innerHTML : '') + "\n";
        let reviewDefLine = "review definition: " + (reviewDefEl ? reviewDefEl.innerHTML : '') + "\n";
        let reviewCorrectnessLine = "review correctness: " + (reviewCorrectnessEl ? reviewCorrectnessEl.innerHTML : '') + "\n";

        let reviewCorrectVersionLine = reviewCorrectVersionEl.innerHTML ? "correct version: " + reviewCorrectVersionEl.innerHTML  + "\n" : '';
        let reviewExplanationOfTextLine = "explanation of text: " + (reviewExplanationOfTextEl ? reviewExplanationOfTextEl.innerHTML : '') + "\n";

        let reviewGrammarErrorsLines = reviewGrammarErrorsEls.length > 0 ? "grammar errors: " : "";
        if (reviewGrammarErrorsEls.length > 0) {
            if (reviewGrammarErrorsEls.length > 1) {
                reviewGrammarErrorsLines += "\n\t";
            }
            for (let i = 0; i < reviewGrammarErrorsEls.length; i++) {

                if (i == reviewGrammarErrorsEls.length - 1 && reviewGrammarErrorsEls.length > 1) {  // последний элемент
                    reviewGrammarErrorsLines +=  i + 1 + ". " + reviewGrammarErrorsEls[i].innerHTML + "\n\n";
                }

                else if (i == reviewGrammarErrorsEls.length - 1) {  // один элемент
                    reviewGrammarErrorsLines += reviewGrammarErrorsEls[i].innerHTML + "\n\n";
                }

                else {  // остальные элементы
                    reviewGrammarErrorsLines +=  i + 1 + ". " + reviewGrammarErrorsEls[i].innerHTML + "\n\t";
                }

            }
        }

        let reviewStyleSuggestionLines = "style suggestions: ";
        if (reviewStyleSuggestionsEls.length > 0) {
            if (reviewStyleSuggestionsEls.length > 1) {
                reviewStyleSuggestionLines += "\n\t";
            }
            for (let i = 0; i < reviewStyleSuggestionsEls.length; i++) {
                if (i == reviewStyleSuggestionsEls.length - 1 && reviewStyleSuggestionsEls.length > 1) {  // последний элемент
                    reviewStyleSuggestionLines += i + 1 + ". " + reviewStyleSuggestionsEls[i].innerHTML + "\n\n";
                }
                else if (i == reviewStyleSuggestionsEls.length - 1) {  // один элемент
                    reviewStyleSuggestionLines += reviewStyleSuggestionsEls[i].innerHTML + "\n\n";
                }
                else {  // остальные элементы
                    reviewStyleSuggestionLines += i + 1 + ". " + reviewStyleSuggestionsEls[i].innerHTML + "\n\t";
                }

            }
        }

        // сборка строки
        beforeReviewText = inputText + "\n" + wordLine + posLine + defLine + "\n" + tenseLine + usageLine + sentenceTypeLine + pronounLine + "\n";
        afterReviewText = reviewWordLine + reviewPosLine + reviewDefLine + reviewCorrectnessLine + "\n" + reviewGrammarErrorsLines + reviewStyleSuggestionLines + reviewCorrectVersionLine + reviewExplanationOfTextLine;

        allLines = beforeReviewText + afterReviewText;

        temp.value = allLines;
        document.body.appendChild(temp);

        // Выделяем и копируем
        temp.select();
        try {
            const success = document.execCommand('copy');
                if (success) {
                    console.log(allLines);
                    console.log('Copy successful!');
                } else {
                    console.log('Copy failed!');
                }
        } catch (err) {
            alert('Copy failed: ' + err);
        }
        // Удаляем временный элемент
        document.body.removeChild(temp);
    });

}