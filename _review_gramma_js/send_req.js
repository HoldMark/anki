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
}

class GeminiClient {
    URL = "https://generativelanguage.googleapis.com/v1beta/models/";
    BASEMODEL = "gemini-2.5-flash";
    API_KEY = ""; // Need to set this up in the .env file

    generateContent(data) {
        console.log("generateContent: get data", data);
        let headers = {
            "Content-Type": "application/json",
            'x-goog-api-key': this.API_KEY,
        }

        fetch(this.URL + this.BASEMODEL + ":generateContent", {
            method: "POST",
            headers: headers,
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error(error));
    }
}

function getBaseRequestData(text) {
    const baseRequestData = {
        contents: [
            {
                parts: [
                    {
                        text: JSON.stringify(text)
                    }
                ],
                role: "user"
            }
        ],
        systemInstruction: {
        parts: [
            {
                text: `
                        You are a distinguished professor of English linguistics.
                        Your task is to analyze the provided English text according to the input data and produce a structured JSON response strictly matching the ReviewResponseModel format below.
                        Focus on grammar correctness, linguistic accuracy, and semantic alignment with the provided word and parameters.
                        Respond only in English.

                        You must check the following:
                        1. Word presence – verify if the given word (or its grammatical form) appears in the text.
                        2. Part of speech – confirm the word is used with the correct part of speech.
                        3. Definition – ensure the meaning of the word in the text matches the provided definition.
                        4. Tense – verify there is at least one sentence using the given tense.
                        5. Usage – check if the text demonstrates the correct use case or context (if provided).
                        6. Sentence type – verify the presence of the specified sentence type (e.g., interrogative, declarative, imperative, exclamatory).
                        7. Pronoun – confirm the presence of the specified pronoun.
                        8. Grammar – check overall grammar correctness of the text (ignore stylistic or lexical preferences).

                        In addition:
                        1. If any errors are found, list them clearly in "errors_with_grammar" with short explanations.
                        2. "correct_version" – the text corrected for grammar.
                        3. "style_suggestions" – 2–4 stylistic improvements (variants in conversational, formal, or everyday tone).
                        4. "explanation_of_text" – a short summary of what the text is about.
                        5. Usage and sentence type may be missing. Do not fail if they are absent.
                        6. You must output valid JSON strictly following schema.
                    `
            }
      ],
      role: "user"
        },
        generationConfig: {
            responseMimeType: "application/json",
            responseSchema: {
                properties: {
                    text: { title: "Text", type: "STRING" },
                    is_word: { title: "Is Word", type: "BOOLEAN" },
                    is_part_of_speech: { title: "Is Part Of Speech", type: "BOOLEAN" },
                    is_definition: { title: "Is Definition", type: "BOOLEAN" },
                    is_tense: { title: "Is Tense", type: "BOOLEAN" },
                    is_usage: { title: "Is Usage", type: "BOOLEAN" },
                    is_sentence_type: { title: "Is Sentence Type", type: "BOOLEAN" },
                    is_pronoun: { title: "Is Pronoun", type: "BOOLEAN" },
                    correct_version: { title: "Correct Version", type: "STRING" },
                    grammar_correctness: { title: "Grammar Correctness", type: "BOOLEAN" },
                    errors_with_grammar: {
                        items: { type: "STRING" },
                        title: "Errors With Grammar",
                        type: "ARRAY"
                    },
                    style_suggestions: {
                        items: { type: "STRING" },
                        title: "Style Suggestions",
                        type: "ARRAY"
                    },
                    explanation_of_text: { title: "Explanation Of Text", type: "STRING" }
                },
                property_ordering: [
                    "text",
                    "is_word",
                    "is_part_of_speech",
                    "is_definition",
                    "is_tense",
                    "is_usage",
                    "is_sentence_type",
                    "is_pronoun",
                    "correct_version",
                    "grammar_correctness",
                    "errors_with_grammar",
                    "style_suggestions",
                    "explanation_of_text"
                ],
                required: [
                    "text",
                    "is_word",
                    "is_part_of_speech",
                    "is_definition",
                    "is_tense",
                    "is_usage",
                    "is_sentence_type",
                    "is_pronoun",
                    "correct_version",
                    "grammar_correctness",
                    "errors_with_grammar",
                    "style_suggestions",
                    "explanation_of_text"
                ],
                title: "ReviewResponseModel",
                type: "OBJECT"
            }
        }
    };

    return baseRequestData;
}

// let example = {
//     "word": "snatch",
//     "pos": "verb",
//     "definition":"to take hold of something suddenly and roughly",
//     "tense":"present perfect",
//     "usage":"to emphasise that something is done or achieved, often before the expected time",
//     "sentence_type":"null",
//     "card_pronoun":"I",
//     "sentence":"I've already snatched it"
// };

let example_data = getBaseRequestData(example);
let client = new GeminiClient();
client.generateContent(example_data);
