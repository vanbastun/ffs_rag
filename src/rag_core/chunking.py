import re

# Компилируем паттерны один раз для скорости
_MD_SYMBOLS = re.compile(r"[#>*`_~\[\]\(\)!-]")
_WS = re.compile(r"\s+")


def simple_md_clean(text: str) -> str:
    """
    Убирает базовые markdown-символы и нормализует пробелы.
    """
    # Убираем служебные символы
    text = _MD_SYMBOLS.sub(" ", text)
    # Схлопываем все виды пробельных символов в один пробел
    return _WS.sub(" ", text).strip()


def fixed_chunk(text: str, size: int = 800, overlap: int = 100) -> list[str]:
    """
    Разбивает текст на перекрывающиеся чанки по словам.

    size    — длина чанка в токенах (словах)
    overlap — перекрытие между чанками (в токенах)
    """
    if size <= 0:
        raise ValueError("size must be positive")
    if overlap < 0:
        raise ValueError("overlap cannot be negative")
    if overlap >= size:
        raise ValueError("overlap must be smaller than size")

    tokens = text.split()
    step = size - overlap
    return [" ".join(tokens[i : i + size]) for i in range(0, len(tokens), step)]
