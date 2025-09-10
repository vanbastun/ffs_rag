import re
from re import Pattern

# Более читаемый паттерн для e‑mail
EMAIL_PATTERN: Pattern = re.compile(
    r"""
    [A-Za-z0-9._%+-]+      # имя пользователя
    @
    [A-Za-z0-9.-]+         # домен
    \.[A-Za-z]{2,}         # TLD
""",
    re.VERBOSE | re.IGNORECASE,
)

# Паттерн для телефонов (простая, но расширяемая версия)
PHONE_PATTERN: Pattern = re.compile(
    r"""
    \+?                    # возможный "+"
    \d                     # первая цифра
    [\d\-\s]{8,}           # остальные цифры/пробелы/дефисы (не менее 8 символов)
    \d                     # последняя цифра
""",
    re.VERBOSE,
)


def redact_pii(
    text: str, email_pattern: Pattern | None = None, phone_pattern: Pattern | None = None
) -> str:
    """
    Заменяет e‑mail и телефонные номера в тексте на маркеры.
    """
    email_pattern = email_pattern or EMAIL_PATTERN
    phone_pattern = phone_pattern or PHONE_PATTERN

    # Сначала заменяем e‑mail, чтобы не повредить телефоны внутри адреса
    text = email_pattern.sub("[EMAIL]", text)
    text = phone_pattern.sub("[PHONE]", text)
    return text
