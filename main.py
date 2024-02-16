import time
from mail import get_email


# if __name__ == "__main__":
#     get_email()  # Однократный запуск


if __name__ == "__main__":
    while True:
        get_email()
        time.sleep(20)  # Через 20 секунд - следующая итерация
