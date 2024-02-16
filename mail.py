import spacy
import email
import re
import smtplib
import imaplib
import logging
from email.header import decode_header
from email.mime.text import MIMEText

from config import IMAP, LOGIN, PASSWORD
from service import extract_keywords, generate_response


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def send_response(response_text: str, recipient_email: str) -> None:
    """
    Отправляет ответ на указанный адрес электронной почты.

    Parameters:
    - response_text (str): Текст ответа.
    - recipient_email (str): Адрес получателя.

    Returns:
    - None
    """
    # Учетные данные для отправки письма
    sender_email = LOGIN
    password = PASSWORD

    # recipient_email = "xxx@mail.ru"  # Для теста, юзер для вопроса и ответа

    # Формируем текст ответа
    subject = 'Ответ на ваш вопрос'
    message = response_text

    # Формируем MIME-структуру письма
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email

    try:
        # Устанавливаем соединение с сервером SMTP (как пример - для mail.ru)
        with smtplib.SMTP_SSL('smtp.mail.ru', 465) as server:
            server.login(sender_email, password)  # Авторизация на сервере
            server.sendmail(sender_email, recipient_email, msg.as_string())  # Отправка письма

        logger.info("Ответ успешно отправлен на адрес %s", recipient_email)
    except Exception as e:
        logger.error("Ошибка при отправке ответа: %s", str(e))


def get_email() -> None:
    """
    Получает и обрабатывает непрочитанные сообщения из почтового ящика.

    Returns:
    - None
    """
    mail = imaplib.IMAP4_SSL(IMAP)
    mail.login(LOGIN, PASSWORD)
    mail.select("inbox")

    # Ищем все непрочитанные сообщения
    status, messages = mail.search(None, "(UNSEEN)")

    for num in messages[0].split():
        # Получаем данные о письме
        _, msg_data = mail.fetch(num, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                body = ""
                # Декодируем письмо
                msg = email.message_from_bytes(response_part[1])
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding or "utf-8")
                    logger.info("Тема письма: %s", subject)

                # Извлекаем текст письма
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True)
                            logger.info("Текст письма (декодированный): %s", body.decode("utf-8"))
                else:
                    body = msg.get_payload(decode=True)
                    logger.info("Текст письма (декодированный): %s", body.decode("utf-8"))

                # Логика обработки письма (нужно извлечь только текст):
                full_text = body.decode("utf-8")
                pattern = re.compile(r"(.+?)\s*--", re.DOTALL)
                match = pattern.search(full_text)
                if match:
                    text = match.group(1).strip()
                    # Теперь email_text содержит только текст письма без лишних символов
                    logger.info("Текст письма после извлечения: %s", text)
                else:
                    text = ""
                    logger.warning("Не удалось извлечь текст письма.")
                # Отправляем ответ

                keywords = extract_keywords(text)
                response = generate_response(keywords)
                send_response(response, msg["From"])

    # Закрываем соединение
    mail.logout()
