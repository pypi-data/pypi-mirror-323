import requests
import importlib.resources
import base64
from .login import token


class Client:
    def __init__(self, model='gpt-4o'):
        self.url = 'http://5.35.46.26:10500/chat'
        self.model = model
        self.system_prompt = (
            'Всегда форматируй все формулы и символы в Unicode или ASCII. '
            'Не используй LaTeX или другие специальные вёрстки. '
            'Пиши по-русски.'
        )

    def get_response(self, message):
        headers = {
            "Authorization": f"Bearer {token}",
            'Content-Type': 'application/json'
        }
        
        if self.model in ['o1-mini', 'o1-preview']:
            messages = [{'role': 'user', 'content': f"{self.system_prompt}\n{message}"}]
        else:
            messages = [
                {'role': 'system', 'content': self.system_prompt},
                {'role': 'user', 'content': message}
            ]

        data = {
            'model': self.model,
            'messages': messages
        }

        response = requests.post(self.url, headers=headers, json=data)
        
        return response.json()['choices'][0]['message']['content']


def read_txt_file(file_name):
    with importlib.resources.open_text('danya.data', file_name) as file:
        content = file.read()
    return content


def ask(message, m=1):
    """
    Отправляет запрос к модели и возвращает ответ.

    Параметры:
        message (str): Текст запроса, который нужно отправить модели.
        m (int): Номер модели, которую нужно использовать. 
                 Поддерживаемые значения:
                 1 - 'gpt-4o'(по умолчанию)
                 2 - 'o1-mini'
                 3 - 'o1-preview'
                 4 - 'gpt-4o-mini'

    Возвращает:
        str: Ответ модели на заданное сообщение.
    """
    model_map = {1: 'gpt-4o', 2: 'o1-mini', 3: 'o1-preview', 4: 'gpt-4o-mini'}
    client = Client()
    if m in model_map:
        client.model = model_map[m]
    return client.get_response(message)

def get(a='а'):
    """
    Возвращает содержимое одного из предопределённых текстовых файлов с ДЗ, семинарами и теорией.

    Параметры:
        a (str): Имя автора файла.
                     - 'а' для Тёмы
                     - 'д' для Дани
                     - 'м' для Миши
    Возвращает:
        str: Содержимое выбранного файла.
    """
    authors = {'а': 'artyom', 'д': 'danya', 'м': 'misha'}
    a = a.lower().replace('d', 'д').replace('a', 'а').replace('m', 'м')
    author_name = authors.get(a, 'artyom')
    filename = f"{author_name}_{'dl'}.txt"
    
    return read_txt_file(filename)
        
