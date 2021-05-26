# yatube - расшарь себя!

## Описание
Социальная сеть онлайн дневников.


## Технологии
Python 3.8
Django 2.2.19


## Запуск проекта в dev-режиме
- Перейдите в конревой каталог проекта

- Установите и виртуальное окружение
```
python3 -m venv venv
```
- Настройте ваш IDE на работу с этим окружением
```
\VSC\->
	Preferences > Settings > закладка Workspace > в поиске "python.pythonPath"
                                    --> .\venv\Scripts\python.exe (для Windows)
									--> ./venv/bin/python3 (для LinuX)
```

- Запустите виртуальное окружение
```
	(Windows:) source venv/Scripts/activate
	(Linux:) source venv/bin/activate
	---------------------------------------
	Деактивация окружения: deactivate
```

- Установите зависимости из файла requirements.txt
```
pip install -r requirements.txt
``` 

- В папке с файлом manage.py выполните команду:
```
python3 manage.py runserver
```

- При возникновении ошибки (Ubuntu): "That port is already in use.",
	применить комманду: "sudo fuser -k 8000/tcp"


## Автор
Hash466
