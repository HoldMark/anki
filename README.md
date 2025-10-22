# Anki

крутое описание проекта, которое когда-нибудь кто-то напишет

### Структура монорепы

```
.
├── create_task_addon  # Создает задание для написания предложения
│	 ├── __init__.py
│	 ├── create_task.py
│	 ├── english_data.py
│	 ├── request_task_from_python.js
│	 └── requirements.txt
├── delay_addon  # Плагин для задержки кнопок оценок (не реализовано)
│	 └── delay.py
├── html_css
│	 ├── common.css
│	 ├── definition  # Карточка с определением слова
│	 │	 ├── back.html
│	 │	 └── front.html
│	 ├── sentence_typing  # Карточка с написанием предложения
│	 │	 ├── back.html
│	 │	 └── front.html
│	 ├── typing  # Карточка с написанием слова
│	 │	 ├── back.html
│	 │	 └── front.html
│	 └── word  # Карточка со словом
│	     ├── back.html
│	     └── front.html
├── js  # JS
│	 ├── delay.js
│	 ├── remove_all_empty_li.js
│	 ├── sentence_examples.js
│	 └── type_conditions.js
├── parse_words  # Парсит слова из Сambridge Dictionary
│	 ├── check.xlsx
│	 ├── data
│	 │	 ├── ex.py
│	 │	 ├── list_words.py
│	 │	 ├── replace_test.py
│	 │	 └── test.py
│	 ├── exc.py
│	 ├── main.py
│	 └── utils.py
├── review_gramma_addon  # Проверяет предложение через LLM
│	 ├── __init__.py
│	 ├── data
│	 │	 ├── base_request_data.py
│	 │	 ├── base_response_mobel.py
│	 │	 ├── models.py
│	 │	 ├── parse_data.py
│	 │	 └── prompts.py
│	 ├── gemini_client.py
│	 └── request_task_review_to_python.js
└── review_gramma_js
    └── send_req.js
```