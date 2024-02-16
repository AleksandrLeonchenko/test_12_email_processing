import spacy
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_keywords(text: str) -> list:
    """
    Извлекает ключевые слова из текста, приводя леммы к нижнему регистру.

    Parameters:
    - text (str): Входной текст.

    Returns:
    - list: Список извлеченных ключевых слов.
    """
    nlp = spacy.load("ru_core_news_sm")
    doc = nlp(text)

    # Извлекаем леммы слов и приводим их к нижнему регистру
    keywords = [token.lemma_.lower() for token in doc if not token.is_stop and token.is_alpha]
    logger.info("Извлеченные ключевые слова: %s", keywords)

    return keywords


def load_response_dict() -> dict:
    """
    Загружает словарь ответов из файла.

    Returns:
    - dict: Словарь с ключевыми словами и ответами.
    """
    with open("response_dict.json", "r", encoding="utf-8") as file:
        response_dict = json.load(file)
    return response_dict


def generate_response(keywords: list) -> str:
    """
    Генерирует ответ на основе ключевых слов.

    Parameters:
    - keywords (list): Список ключевых слов.

    Returns:
    - str: Сгенерированный ответ.
    """
    response_dict = load_response_dict()
    # Поиск совпадения в словаре
    for key_words, response in response_dict.items():
        if all(keyword in keywords for keyword in key_words.split(',')):
            logger.info("Найдено совпадение в словаре. Ключевые слова: %s, Ответ: %s", key_words, response)
            return response

    # Если ХОТЯ БЫ ОДНО из ключевых слов не совпало, возвращаем общий ответ (так точнее ответ)
    default_response = "Спасибо за ваше обращение. Мы свяжемся с вами в ближайшее время."
    logger.info("Совпадений в словаре не найдено. Возвращен общий ответ: %s", default_response)
    return default_response
