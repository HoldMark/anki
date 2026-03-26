# Anki

Набор аддонов и утилит для [Anki](https://apps.ankiweb.net/) (v25.9.2), заточенных под изучение английского языка.

## Аддоны

### error_freeze

Заморозка кнопок оценки при неверном вводе на карточках с `{{type:FieldName}}`.

- Если ответ набран неверно — кнопки блокируются на время (по умолчанию 1 секунда), после чего пользователь сам выбирает оценку
- Нажатие `Again (1)` никогда не замораживается
- Можно ограничить работу аддона конкретными колодами через конфиг (**Tools → Add-ons → error_freeze → Config**)

```json
{
    "decks": ["English::Vocabulary", "Math"]
}
```

Пустой список `[]` — аддон работает для всех колод.

---

### review_grammar

AI-ревью грамматики прямо в процессе повторения карточек.

- Генерирует задание к карточке со словом: случайное время, тип предложения, местоимение
- Отправляет написанное предложение в Google Gemini и возвращает структурированный фидбек (правильность, ошибки, пояснение)
- Требует Gemini API ключ в переменных окружения

## Установка аддонов

Скопировать папку нужного аддона в директорию Anki:

| OS      | Путь                                                        |
|---------|-------------------------------------------------------------|
| macOS   | `~/Library/Application Support/Anki2/<профиль>/addons21/`  |
| Windows | `%APPDATA%\Anki2\<профиль>\addons21\`                       |
| Linux   | `~/.local/share/Anki2/<профиль>/addons21/`                  |

Перезапустить Anki.

## Разработка

```bash
# Линтер + форматтер
make lint

# Только форматтер
make formater

# Только линтер
make linter
```

**Python**: 3.13+
**Зависимости**: `pip install -r requirements.txt`


### License

This project is dual-licensed:

| Use case | License | Cost |
|---|---|---|
| Open-source project | [GPL v3](LICENSE) | Free |
| Personal / educational use | [GPL v3](LICENSE) | Free |
| Closed-source / commercial product | [Commercial](LICENSE-COMMERCIAL.md) | Contact author |

---

### Open Source

Free to use under the [GNU GPL v3](LICENSE) — but you must
open-source your own code too.

### Commercial

If you use this in a proprietary or closed-source product,
you need a commercial license.

Contact: **prodius.mark@gmail.com**
GitHub: [@HoldMark](https://github.com/HoldMark)

---

By contributing to this project, you agree to the [CLA](CLA.md).

---

Copyright (C) 2026 HoldMark (MarkelloFx2) <prodius.mark@gmail.com>

