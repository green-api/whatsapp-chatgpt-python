# Библиотека WhatsApp GPT Bot для Python

- [Documentation in English](./README.md)

Современная библиотека для создания WhatsApp-бота с поддержкой состояний и интеграцией OpenAI GPT, построенная на базе
whatsapp-chatbot-python и GREEN-API.

## Особенности

- Интеграция с моделями OpenAI GPT для интеллектуальных ответов
- Поддержка различных моделей GPT (GPT-3.5, GPT-4, GPT-4o, o1)
- Мультимодальные возможности с поддержкой обработки изображений
- Транскрипция голосовых сообщений с использованием Whisper API
- Комплексная обработка различных типов медиа сообщений WhatsApp
- Архитектура промежуточного ПО (middleware) для настройки обработки сообщений и ответов
- Встроенное управление историей разговоров
- Система состояний, унаследованная от базовой библиотеки
- Поддержка Python type hints и подробные docstrings

## Установка

```bash
pip install whatsapp-chatgpt-python
```

Зависимости (`openai`, `whatsapp-chatbot-python` и `requests`) будут установлены автоматически.

### Предварительные требования

Перед использованием бота вам потребуется:

1. Зарегистрированный аккаунт на [GREEN-API](https://green-api.com/)
2. ID экземпляра и API-токен из вашего аккаунта GREEN-API
3. API-ключ OpenAI для доступа к GPT

## Быстрый старт

```python
from whatsapp_chatgpt_python import WhatsappGptBot

# Инициализация бота
bot = WhatsappGptBot(
    id_instance="ваш-id-экземпляра",
    api_token_instance="ваш-api-токен",
    openai_api_key="ваш-openai-api-ключ",
    model="gpt-4o",
    system_message="Вы - полезный ассистент."
)

# Запуск бота
bot.run_forever()
```

## Основные компоненты

### Конфигурация бота

Бот наследует все параметры конфигурации от базового класса `GreenAPIBot`, включая возможность настраивать параметры
экземпляра GREEN-API.

Полные параметры конфигурации для WhatsappGptBot:

```python
bot = WhatsappGptBot(
    # Обязательные параметры
    id_instance="ваш-id-экземпляра",
    api_token_instance="ваш-api-токен",
    openai_api_key="ваш-openai-api-ключ",

    # Опциональные GPT-специфические параметры
    model="gpt-4o",  # Модель по умолчанию
    max_history_length=10,  # Максимальное количество сообщений в истории разговора
    system_message="Вы - полезный ассистент.",  # Системное сообщение для установки поведения
    temperature=0.5,  # Температура для генерации ответов
    error_message="Извините, я не смог обработать ваш запрос. Пожалуйста, попробуйте снова.",
    session_timeout=1800,  # Таймаут сессии в секундах (30 минут)

    # Опциональные параметры из базового бота
    bot_debug_mode=False,  # Включить отладочные логи
    debug_mode=False,  # Включить режим отладки API
    raise_errors=True,  # Генерировать ли исключения при ошибках API
    settings={  # Настройки экземпляра GREEN-API
        "webhookUrl": "",  # Пользовательский URL для вебхука
        "webhookUrlToken": "",  # Токен безопасности для вебхука
        "delaySendMessagesMilliseconds": 500,  # Задержка между сообщениями
        "markIncomingMessagesReaded": "yes",  # Отмечать сообщения как прочитанные
        "incomingWebhook": "yes",  # Включить входящие вебхуки
        "keepOnlineStatus": "yes",  # Поддерживать статус онлайн в WhatsApp
        "pollMessageWebhook": "yes",  # Включить вебхуки для опросов
    }
)
```

### WhatsappGptBot

Основной класс для создания и управления вашим WhatsApp-ботом на базе OpenAI:

```python
from whatsapp_chatgpt_python import WhatsappGptBot

bot = WhatsappGptBot(
    id_instance="ваш-id-экземпляра",
    api_token_instance="ваш-api-токен",
    openai_api_key="ваш-openai-api-ключ",
    model="gpt-4o",
    system_message="Вы - полезный ассистент, специализирующийся на поддержке клиентов.",
    max_history_length=15,
    temperature=0.7,
    settings={
        "webhookUrl": "",
        "markIncomingMessagesReaded": "yes",
        "keepOnlineStatus": "yes",
        "delaySendMessagesMilliseconds": 500,
    }
)

# Запуск бота
bot.run_forever()
```

## Голосовые звонки

Бот может отвечать на голосовые звонки WhatsApp и звонить сам, разговаривая с человеком через модель OpenAI Realtime.
Речь звонящего идёт в модель, речь модели идёт в звонок, звонящий может перебить модель. Для звонков нужен Python 3.11
или новее, тариф GREEN-API со звонками и дополнительные зависимости:

```bash
pip install 'whatsapp-chatgpt-python[voice]'
```

```python
import re
from whatsapp_chatgpt_python import WhatsappGptBot, VoiceCallsConfig

bot = WhatsappGptBot(
    id_instance="your-instance-id",
    api_token_instance="your-api-token",
    openai_api_key="your-openai-api-key",
    system_message="You are a helpful assistant of a coffee shop.",
    voice_calls=VoiceCallsConfig(
        voice="marin",
        greeting="Greet the caller and ask how you can help.",
    ),
)


@bot.router.message(regexp=(r"call me", re.IGNORECASE))
def call_me(notification):
    bot.voice_call(notification.chat)


bot.run_forever()
```

- С заданным `voice_calls` бот отвечает на входящие звонки через модель. Чтобы только звонить, укажите
  `answer_incoming=False`. Если уведомления о входящих звонках выключены и `settings` не переданы, бот включает их при
  запуске.
- `bot.voice_call(chat_id)` звонит в чат и начинает разговор, когда человек ответит. Исходящие звонки работают только в
  чаты, которые писали или звонили за последние 72 часа. `bot.in_voice_call` показывает, идёт ли сейчас звонок.
- Одновременно идёт один звонок, в отдельном потоке, поэтому во время звонка бот продолжает отвечать на сообщения.
- Звонок заканчивается, когда человек кладёт трубку, или через `max_call_seconds`.

```python
@dataclass
class VoiceCallsConfig:
    model: str = "gpt-realtime-2.1"
    voice: str = "marin"  # marin, cedar, alloy, ash, ballad, coral, echo, sage, shimmer, verse
    instructions: Optional[str] = None  # system_message by default
    greeting: str = "Greet the caller briefly."
    answer_incoming: bool = True
    max_call_seconds: float = 600
    ring_seconds: float = 60
    vad: VoiceActivityConfig = VoiceActivityConfig()  # threshold 0.5, prefix_padding_ms 400,
    # silence_duration_ms 800, noise_reduction "near_field", "far_field" or None
```

## Обработка сообщений

Бот автоматически обрабатывает различные типы сообщений WhatsApp и преобразует их в формат, понятный моделям OpenAI.

### Поддерживаемые типы сообщений

- **Текст**: Обычные текстовые сообщения
- **Изображения**: Фотографии с опциональными подписями (поддерживается в моделях с возможностью обработки изображений)
- **Аудио**: Голосовые сообщения с автоматической транскрипцией
- **Видео**: Видеосообщения с подписями
- **Документы**: Вложенные файлы
- **Опросы**: Сообщения с опросами и обновлениями опросов
- **Местоположение**: Общий доступ к местоположению
- **Контакты**: Общий доступ к контактам

### Реестр обработчиков сообщений

Бот использует реестр обработчиков сообщений для обработки различных типов сообщений:

```python
# Доступ к реестру
registry = bot.message_handlers


# Создание пользовательского обработчика сообщений
class CustomMessageHandler(MessageHandler):
    def can_handle(self, notification):
        return notification.get_message_type() == "custom-type"

    async def process_message(self, notification, openai_client=None, model=None):
        # Обработка сообщения
        return "Обработанный контент"


# Регистрация пользовательского обработчика
bot.register_message_handler(CustomMessageHandler())

# Замена существующего обработчика
bot.replace_handler(TextMessageHandler, CustomTextHandler())
```

## Система промежуточного ПО (Middleware)

Система промежуточного ПО позволяет настраивать обработку сообщений перед отправкой в GPT и обработку ответов перед
отправкой пользователю.

### Добавление промежуточного ПО для сообщений

```python
# Обработка сообщений перед отправкой в GPT
def custom_message_middleware(notification, message_content, messages, session_data):
    # Добавление пользовательского контекста в разговор
    if notification.get_message_type() == "textMessage" and notification.chat.endswith("@c.us"):
        # Добавление контекста к сообщению
        enhanced_content = f"[Сообщение пользователя] {message_content}"

        return {
            "message_content": enhanced_content,
            "messages": messages
        }

    return {
        "message_content": message_content,
        "messages": messages
    }


# Добавление промежуточного ПО
bot.add_message_middleware(custom_message_middleware)
```

### Добавление промежуточного ПО для ответов

```python
# Обработка ответов GPT перед отправкой пользователю
def custom_response_middleware(response, messages, session_data):
    # Форматирование или изменение ответа
    formatted_response = response.replace("GPT", "Ассистент").strip()

    # Вы также можете изменить сообщения, которые будут сохранены в истории
    return {
        "response": formatted_response,
        "messages": messages
    }


# Добавление промежуточного ПО
bot.add_response_middleware(custom_response_middleware)
```

## Данные сессии

GPT-бот расширяет базовые данные сессии информацией, специфичной для разговора:

```python
@dataclass
class GPTSessionData:
    """Данные сессии для GPT-разговоров"""
    messages: List[Dict[str, Any]] = field(default_factory=list)
    last_activity: int = field(default_factory=lambda: int(time.time()))
    user_data: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
```

Вы можете получить доступ и изменить эти данные в вашем промежуточном ПО:

```python
def message_middleware(notification, content, messages, session_data):
    # Установка переменных контекста
    if "variables" not in session_data.context:
        session_data.context["variables"] = {}

    session_data.context["variables"]["last_interaction"] = int(time.time())

    return {"message_content": content, "messages": messages}
```

## Утилиты

Библиотека предоставляет несколько служебных функций для общих задач:

### Обработка медиафайлов

```python
from whatsapp_chatgpt_python import Utils

# Загрузка медиафайла из URL
temp_file = await Utils.download_media("https://example.com/image.jpg")

# Транскрипция аудио
from openai import OpenAI

openai_client = OpenAI(api_key="ваш-openai-api-ключ")
transcript = await Utils.transcribe_audio("/path/to/audio.ogg", openai_client)

# Очистка после обработки
import os

os.unlink(temp_file)
```

### Управление разговором

```python
from whatsapp_chatgpt_python import Utils

# Обрезка истории разговора
trimmed_messages = Utils.trim_conversation_history(
    messages,
    10,  # макс. кол-во сообщений
    True  # сохранить системное сообщение
)

# Подсчитать примерное количество токенов
estimated_tokens = Utils.estimate_tokens(messages)
```

## Поддерживаемые модели OpenAI

Библиотека поддерживает различные модели OpenAI:

### Модели GPT-4

- gpt-4
- gpt-4-turbo
- gpt-4-turbo-preview
- gpt-4-1106-preview
- gpt-4-0125-preview
- gpt-4-32k

### Модели GPT-4o

- gpt-4o (по умолчанию)
- gpt-4o-mini
- gpt-4o-2024-05-13

### Модели GPT-3.5

- gpt-3.5-turbo
- gpt-3.5-turbo-16k
- gpt-3.5-turbo-1106
- gpt-3.5-turbo-0125

### Модели o1

- o1
- o1-mini
- o1-preview

### Модели с поддержкой изображений

Следующие модели могут обрабатывать изображения:

- gpt-4o
- gpt-4o-mini
- gpt-4-vision-preview
- gpt-4-turbo
- gpt-4-turbo-preview

## Расширенная конфигурация

### Пользовательская обработка команд

Поскольку библиотека построена на whatsapp-chatbot-python, вы можете использовать все функции команд/фильтров базовой
библиотеки:

```python
@bot.router.message(command="help")
def help_handler(notification):
    help_text = (
        "🤖 *WhatsApp GPT Бот* 🤖\n\n"
        "Доступные команды:\n"
        "• */help* - Показать это сообщение помощи\n"
        "• */clear* - Очистить историю разговора\n"
        "• */info* - Показать информацию о боте"
    )
    notification.answer(help_text)


# Команда очистки истории разговора
@bot.router.message(command="clear")
def clear_history_handler(notification):
    chat_id = notification.chat

    # Получение данных сессии
    session_data = bot.get_session_data(chat_id)

    # Поиск системного сообщения, если оно существует
    system_message = None
    for msg in session_data.messages:
        if msg.get("role") == "system":
            system_message = msg
            break

    # Сброс сообщений, но сохранение системного сообщения
    if system_message:
        session_data.messages = [system_message]
    else:
        session_data.messages = []

    # Обновление сессии
    bot.update_session_data(chat_id, session_data)

    notification.answer("🗑️ История разговора очищена! Начнем заново.")
```

### Обход GPT для определенных команд

Вы можете создавать обработчики, которые не использую обработку GPT:

```python
@bot.router.message(command="weather")
def weather_handler(notification):
    notification.answer(
        "🌤️ Это заглушка ответа о погоде от пользовательского обработчика.\n\n"
        "В реальном боте здесь было бы обращение к API погоды.\n\n"
        "Этот обработчик демонстрирует пропуск обработки GPT."
    )
```

### Явная обработка GPT

Вы можете явно запросить обработку GPT после обработки сообщения:

```python
@bot.router.message(text_message="recommend")
def recommend_handler(notification):
    # Добавление префиксного сообщения
    notification.answer("Я дам вам рекомендацию. Дайте мне подумать...")
    # Запрос обработки GPT
    notification.process_with_gpt()
```

Вы также можете модифицировать сообщение перед отправкой его в GPT, используя параметр `custom_message`:

```python
# Обработчик эхо, который пересылает модифицированное сообщение в GPT
@bot.router.message(command="echo")
def echo_handler(notification):
    # Получаем сообщение после команды
    message_text = notification.message_text
    command_parts = message_text.split(maxsplit=1)

    if len(command_parts) > 1:
        echo_text = command_parts[1]
        notification.answer(f"Вы сказали: {echo_text}\n\nЯ спрошу GPT для получения дополнительной информации...")

        # Обработка с GPT, но передаем только фактическое сообщение (без команды)
        notification.process_with_gpt(custom_message=echo_text)
    else:
        notification.answer("Пожалуйста, укажите текст после команды /echo.")
```

Это полезно, когда вы хотите предварительно обработать сообщение перед его отправкой в GPT, например, удалить префиксы
команд, отформатировать текст или добавить контекст.

### Расширенная обработка сообщений

```python
# Проверка, поддерживает ли текущая модель изображения
if bot.supports_images():
    # Обработка рабочего процесса на основе изображений
    pass
```

## Полный пример бота

Вот полный пример WhatsApp GPT бота с пользовательскими обработчиками и промежуточным ПО:

```python
import os
import time
import logging
from whatsapp_chatgpt_python import (
    WhatsappGptBot,
    ImageMessageHandler,
    TextMessageHandler
)
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()
# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('whatsapp_chatgpt_python')

# Получение переменных окружения
ID_INSTANCE = os.environ.get("INSTANCE_ID")
API_TOKEN = os.environ.get("INSTANCE_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Инициализация бота
bot = WhatsappGptBot(
    id_instance=ID_INSTANCE,
    api_token_instance=API_TOKEN,
    openai_api_key=OPENAI_API_KEY,
    model="gpt-4o",  # Использует модель GPT-4o (которая поддерживает изображения)
    system_message="Вы - полезный ассистент. Будьте краткими и дружелюбными в своих ответах.",
    max_history_length=15,  # Хранить последние 15 сообщений в истории разговора
    temperature=0.7,  # Немного более творческие ответы
    session_timeout=1800,  # Сессии истекают после 30 минут неактивности
    error_message="Извините, ваше сообщение не удалось обработать.",  # Пользовательское сообщение об ошибке
)


# Пользовательский обработчик изображений с расширенными инструкциями
class EnhancedImageHandler(ImageMessageHandler):
    async def process_message(self, notification, openai_client=None, model=None):
        # Вызов метода родительского класса для получения базового результата
        result = await super().process_message(notification, openai_client, model)

        # Для текстовых ответов (не визуальные модели)
        if isinstance(result, str):
            return result.replace(
                "[The user sent an image",
                "[Пользователь отправил изображение. Проанализируйте, что может быть на нем, основываясь на подписи"
            )

        # Для моделей с поддержкой изображений, улучшаем текстовую инструкцию
        if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
            if result[0].get('type') == 'text':
                text = result[0].get('text', '')
                if text == "Analyzing this image":
                    result[0]['text'] = "Подробно опишите это изображение и то, что вы на нем видите."

        return result


# Пример пользовательского текстового обработчика
class EnhancedTextHandler(TextMessageHandler):
    async def process_message(self, notification, *args, **kwargs):
        # Получение текстового сообщения с помощью метода родительского класса
        text = await super().process_message(notification, *args, **kwargs)

        if not text:
            return text

        lower_text = text.lower()

        if any(term in lower_text for term in ['код', 'функция', 'скрипт', 'программа']):
            return f"🧑‍💻 ЗАПРОС НА КОД: {text}\n\n[Я отформатирую мой ответ с кодом с правильной подсветкой синтаксиса]"

        elif text.endswith('?') or text.lower().startswith(
                ('что', 'почему', 'как', 'когда', 'где', 'кто', 'можно', 'мог')):
            return f"❓ ВОПРОС: {text}\n\n[Я предоставлю четкий и исчерпывающий ответ]"

        return text


# Замена обработчиков по умолчанию на наши расширенные версии
bot.replace_handler(ImageMessageHandler, EnhancedImageHandler())
bot.replace_handler(TextMessageHandler, EnhancedTextHandler())


# Промежуточное ПО для логирования всех сообщений и добавления информации о трекинге
def logging_middleware(notification, message_content, messages, session_data):
    user_id = notification.sender
    if isinstance(message_content, str):
        content_display = message_content[:100] + "..." if len(message_content) > 100 else message_content
    else:
        content_display = "сложный контент (вероятно, содержит медиа)"

    logger.info(f"Сообщение от {user_id}: {content_display}")

    # Добавление информации о трекинге в контекст сессии
    if not session_data.context.get("variables"):
        session_data.context["variables"] = {}

    session_data.context["variables"].update({
        "last_interaction": int(time.time()),
        "message_count": session_data.context.get("variables", {}).get("message_count", 0) + 1
    })

    # Возвращаем неизмененный контент и сообщения
    return {"message_content": message_content, "messages": messages}


# Промежуточное ПО для форматирования ответов перед отправкой пользователю
def formatting_middleware(response, messages, session_data):
    # Форматируем ответ, добавляя подпись в конце длинных сообщений
    formatted_response = response.strip()

    # Не добавляем подпись к коротким ответам
    if len(formatted_response) > 100 and not formatted_response.endswith("_"):
        message_count = session_data.context.get("variables", {}).get("message_count", 0)
        formatted_response += f"\n\n_Сообщение #{message_count} • Работает на GPT_"

    return {"response": formatted_response, "messages": messages}


# Добавление промежуточного ПО
bot.add_message_middleware(logging_middleware)
bot.add_response_middleware(formatting_middleware)


# Обработчик команды /clear для сброса истории разговора
@bot.router.message(command="clear")
def clear_history_handler(notification):
    chat_id = notification.chat

    # Получение данных сессии
    session_data = bot.get_session_data(chat_id)

    # Поиск системного сообщения, если оно существует
    system_message = None
    for msg in session_data.messages:
        if msg.get("role") == "system":
            system_message = msg
            break

    # Сброс сообщений, но сохранение системного сообщения
    if system_message:
        session_data.messages = [system_message]
    else:
        session_data.messages = []

    # Обновление сессии
    bot.update_session_data(chat_id, session_data)

    notification.answer("🗑️ История разговора очищена! Начнем заново.")


# Обработчик команды /help для отображения доступных команд
@bot.router.message(command="help")
def help_handler(notification):
    help_text = (
        "🤖 *WhatsApp GPT Бот* 🤖\n\n"
        "Доступные команды:\n"
        "• */help* - Показать это сообщение помощи\n"
        "• */clear* - Очистить историю разговора\n"
        "• */info* - Показать информацию о боте\n"
        "• */weather* - Пример обработчика, пропускающего GPT\n\n"
        "Вы можете отправлять текст, изображения, аудио и многое другое. Я буду интеллектуально отвечать на ваши сообщения."
    )
    notification.answer(help_text)


# Добавление команды info
@bot.router.message(command="info")
def info_handler(notification):
    chat_id = notification.chat
    session_data = bot.get_session_data(chat_id)

    # Получение статистики сессии
    message_count = len(session_data.messages) - 1  # Вычитаем системное сообщение
    if message_count < 0:
        message_count = 0

    vision_capable = "Да" if bot.supports_images() else "Нет"

    info_text = (
        "📊 *Информация о боте* 📊\n\n"
        f"Модель: {bot.get_model()}\n"
        f"Поддержка изображений: {vision_capable}\n"
        f"Сообщений в текущей сессии: {message_count}\n"
        f"Максимальная длина истории: {bot.max_history_length}\n"
        f"Таймаут сессии: {bot.session_timeout} секунд\n\n"
        "Чтобы очистить текущий разговор, используйте */clear*"
    )
    notification.answer(info_text)


# Пример обработчика погоды, пропускающего обработку GPT
@bot.router.message(command="weather")
def weather_handler(notification):
    notification.answer(
        "🌤️ Это заглушка ответа о погоде от пользовательского обработчика.\n\n"
        "В реальном боте здесь было бы обращение к API погоды.\n\n"
        "Этот обработчик демонстрирует пропуск обработки GPT."
    )


# Запуск бота
if __name__ == "__main__":
    logger.info("Запуск WhatsApp GPT Бота...")
    logger.info(f"Используемая модель: {bot.get_model()}")
    bot.run_forever()
```

## Лицензия

MIT

## Используемые технологии

Эта библиотека построена на основе:

- [whatsapp-chatbot-python](https://github.com/green-api/whatsapp-chatbot-python) - Базовая библиотека WhatsApp-бота
- [GREEN-API](https://green-api.com/) - Сервис API WhatsApp для интеграции ботов
- [OpenAI API](https://openai.com/) - Для интеграции моделей GPT
