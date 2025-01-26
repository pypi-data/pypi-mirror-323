![banner](https://i.ibb.co/zrpfMXh/3-20250125121647.png)

# Документация для библиотеки `Gpt4Zero` (v0.1) <img src="https://cdn-icons-png.flaticon.com/512/3098/3098090.png" width="28">

## 1. Установка <a name="1-установка"></a>

```bash
pip install Gpt4Zero
```

---

## 2. Использование <a name="2-использование"></a>

### Быстрый старт
```python
from gpt4zero import AI_Client

client = AI_Client()
print(client.list_models())  # ['claude-sonnet-3.5', 'gpt-4o', 'gemini-1.5', 'deepseek-r1']
```

### Доступные модели
| Модель | Описание |
|--------|----------|
| **claude-sonnet-3.5** | Баланс скорости и качества |
| **gpt-4o** | Максимальная производительность |
| **gemini-1.5** | Быстрые ответы |
| **deepseek-r1** | Специализация на генерации кода |

---

## 3. Примеры использования <a name="3-примеры"></a>

### 3.1. Базовый запрос
```python
from gpt4zero import AI_Client

# Инициализация клиента
client = AI_Client()

# Формирование запроса
messages = [{
    "role": "user", 
    "content": "Объясни разницу между TCP и UDP протоколами"
}]

# Отправка запроса
response = client.chat(messages)

# Вывод результата
print("Ответ системы:\n", response)
```

### 3.2. Выбор конкретной модели
```python
from gpt4zero import AI_Client

client = AI_Client()

# Запрос к специализированной модели для генерации кода
messages = [{
    "role": "user", 
    "content": "Напиши функцию на Python для валидации email-адресов"
}]

response = client.chat(
    messages, 
    model="deepseek-r1"  # Явное указание модели
)

print("Сгенерированный код:\n", response)
```

### 3.3. Потоковая передача данных
```python
from gpt4zero import AI_Client

client = AI_Client()

# Запрос с активацией потокового режима
messages = [{
    "role": "user", 
    "content": "Подробно опиши процесс фотосинтеза в растениях"
}]

print("Получение ответа в реальном времени:")
for chunk in client.chat(messages, stream=True):
    print(chunk, end='', flush=True)  # Постепенная печать частей ответа
```

### 3.4. Работа с контекстом диалога
```python
from gpt4zero import AI_Client

client = AI_Client()

# История предыдущего общения
history = [
    {"role": "user", "content": "Как работает нейронная сеть?"},
    {"role": "assistant", "content": "Это математическая модель, имитирующая..."}
]

# Новый запрос в контексте предыдущего диалога
new_message = {
    "role": "user", 
    "content": "Приведи пример использования сверточных нейросетей"
}

response = client.chat(history + [new_message])
print("Расширенный ответ:\n", response)
```

### 3.5. Обработка ошибок
```python
from gpt4zero import AI_Client, APIError

client = AI_Client()

try:
    # Намеренно некорректный запрос
    response = client.chat([
        {"role": "user", "content": ""}  # Пустое сообщение
    ])
except APIError as e:
    print(f"Ошибка API: {e.code} - {e.message}")
except Exception as e:
    print(f"Системная ошибка: {str(e)}")
```

---

## Поддержка <a name="поддержка"></a>

<div align="left">
  <a href="https://t.me/termiss_it" target="_blank" rel="noopener">
    <img src="https://cdn-icons-png.flaticon.com/512/2111/2111646.png" 
         alt="Telegram"
         width="28"
         style="vertical-align: middle; margin-right: 10px;">
    Telegram-канал
  </a>
  ᅠ 
  <a href="https://github.com/qwez-source" target="_blank" rel="noopener">
    <img src="https://cdn-icons-png.flaticon.com/512/733/733553.png" 
         alt="GitHub"
         width="28"
         style="vertical-align: middle; margin-right: 10px;">
    GitHub автора
  </a>
</div>

---
*Версия 1.2 | Обновлено: 15 июля 2024*  

**Лицензия:** MIT  
**Статус:** Активно развивается