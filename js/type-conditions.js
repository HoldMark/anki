document.addEventListener("DOMContentLoaded", () => {
});  // для запуска кода после загрузки DOM

{
    let list_of_pronouns = ['I', 'He', 'She', 'It', 'They', 'We', 'You'];
    let sentence_type = ['affirmative sentences', 'negative sentences', 'interrogative sentences', 'interrogative-negative sentences in a formal style', 'interrogative-negative sentences in an informal style', 'interrogative sentences with a question word']
    let list_of_tenses = [
        'Past Continuous',
        'Present Continuous',
        'Future Continuous'
    ]
    let usages = {
        'Past Continuous': ['to talk about actions and states in progress (happening) around a **particular time** in the past', 'simultaneous/parallel actions', 'a longer action that was be in progress when another action occurred (interruption)', 'to describe something **temporary** that was happening in our life in the past', 'to emphasise that the action or state continued for a period of time in the past', 'used to add emotional coloring to continuously repeated (events/states)', 'used to add emotional coloring to constant, repeated, unplanned or undesired (events/states)', 'unnatural, unusual action or state that is temporary', 'to give a reason or context for an event', 'to talk about repeated ""background"" events in the past. It can suggest that the situation was temporary or subject to change', 'to create a background or atmosphere when telling a story - **(artistic)**'],
        'Present Continuous': ['to talk about events/state which are true **around the moment of speaking or now**', 'simultaneous/parallel actions that are occurring in a certain period of time', 'to describe actions which are repeated or regular, but which we believe to be temporary', 'to talk about a gradual change', 'to emphasize that the action or state is continuing for a certain period of time', 'unnatural, unusual action or state that is temporary', 'used to add emotional coloring to continuously repeated (actions/states)', 'used to add emotional coloring to constant, repeated, unplanned or undesired (actions/states)', 'to show that we have already decided something and usually that we have already made a plan or arrangements'],
        'Future Continuous': ['an action or state that is **expected** to last for a certain period of time', 'simultaneous/parallel actions that are expected to occur over a certain period of time', 'a longer action that will be in progress when another action occurs (interruption)', 'actions that will occur regularly or repeatedly in a specific period of time in the future', 'to emphasize that the action or state will continue for a period of time (it could be small period)', 'used to add emotional coloring to continuously repeated (events/states)', 'used to add emotional coloring to constant, repeated, unplanned or undesired (events/states)', 'unnatural, unusual action or state that is temporary', 'polite enquiries about someone’s plans or availability, or about scheduled arrangements', 'to create a background or atmosphere when telling a story - **(artistic)**']
    }


    let card_word = document.querySelector('.additional-conditions').getAttribute('data-word');
    let card_pos = document.querySelector('.additional-conditions').getAttribute('data-pos');
    let card_def = document.querySelector('.additional-conditions').getAttribute('data-def');

    function stringToNumber(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            hash += str.charCodeAt(i) * (i + 1);
        }
        return hash;
    }

    let hash_card = stringToNumber(card_word + card_pos + card_def);
    
    let currentDate = new Date();
    let today_num = currentDate.getDate();  // возвращает день месяца (от 1 до 31)
    let day_of_week = currentDate.getDay() + 1; // возвращает день недели (от 0 до 6, где 0 - воскресенье)
    let today_month = currentDate.getMonth() + 1; // возвращает месяц (от 0 до 11, где 0 - январь)
    
    
    let pronoun_index = (hash_card + today_num) % list_of_pronouns.length;
    let tense_index = (hash_card + today_num + day_of_week) % list_of_tenses.length;
    let usages_index = (hash_card + today_num + (day_of_week * today_month)) % usages[list_of_tenses[tense_index]].length;
    let sentence_type_index = (hash_card + (today_num * day_of_week)) % sentence_type.length;
    
    let card_pronoun = list_of_pronouns[pronoun_index];
    let card_tense = list_of_tenses[tense_index];
    let card_usage = usages[card_tense][usages_index];
    let card_sentence_type = sentence_type[sentence_type_index];
    
    document.querySelector('.condition_usage').innerHTML = card_usage;
    document.querySelector('.condition_tense').innerHTML = card_tense;
    document.querySelector('.condition_sentence_type').innerHTML = card_sentence_type;
    document.querySelector('.condition_pronoun').innerHTML = card_pronoun;

		







    
    // copy script

    document.querySelector('.copy-icon').addEventListener('click', () => {
        const input = document.getElementById('typeans');		
        const temp = document.createElement('textarea'); // Создаём временное textarea

        let word_line = 'word: ' + card_word + '\n';
        let pos_line = 'part of speach: ' + card_pos + '\n';
        let def_line = 'definiton: ' + card_def + '\n';
        let pronoun_line = 'pronoun: ' + card_pronoun + '\n\n';
        let sentence_line = 'my sentences: ' + input.value;

        all_lines = word_line + pos_line + def_line + pronoun_line + sentence_line;

        temp.value = all_lines;
        document.body.appendChild(temp);
    
        // Выделяем и копируем
        temp.select();
        try {
            const success = document.execCommand('copy');
                if (success) {
                var _ = 1 + 1;				 	
                // alert(all_lines);
                } else {
                // alert('Copy failed.');
                }
        } catch (err) {
            alert('Copy failed: ' + err);
        }
        // Удаляем временный элемент
        document.body.removeChild(temp);
    });

}