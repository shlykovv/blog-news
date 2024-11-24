# Новостной портал

****News портал - проект позволяет:****

- Создавать, редактировать и удалять собственные новости
- Просматривать новости других пользователей
- Комментировать отзывы других участников портала
- Добавление в программы просмотра RSS ленты

### **Стек**
![python version](https://img.shields.io/badge/Python-3.11-green) ![django version](https://img.shields.io/badge/Django-4.1-green)

## Инструкции по установке

1. Клонируйте репозиторий и перейдите в него в командной строке:
```bash
git clone https://github.com/Vamp1r1309/blog-news.git
```
2. Создаем вируальное акружение venv:
```bash
python -m venv venv
```
```bash
source venv/Scripts/activate
```
3. Обновляем менеджер пакетов pip:
```bash
python -m pip install --upgrade pip
```
4. Установите зависимости из файла requirements.txt:
```bash
pip install -r requirements.txt
```
```bash
# * - примечание: в случае если что-то не установится или будет какая-то ошибка,
# то устанавливайте по одному пакету из файла requirements.txt
```
5. Заполните файл .env_prod и переименуйте его в .env или создайте собственный и заполните его:
```bash
cd mv .env_prod .env
```
```bash
touch .env
```
6. При создание собственного файла .env, заполните его следующими данными:
```bash
SECRET_KEY=
ALLOWED_HOSTS=*

EMAIL_HOST=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=
# * - примечание: хост должен быть ALLOWED_HOSTS=*
```
7. Выполните команду миграций:
```bash
python manage.py migrate
```
8. Запустите проект:
```bash
python manage.py runserver
```
<br>
