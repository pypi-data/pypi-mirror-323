import tomlkit
from django.conf import settings


def message_return(language: str, data: str) -> bool:
    print(settings.LANGUAGE_DIR)
    return True