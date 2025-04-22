from flask import Flask, render_template, request, Response, flash, send_from_directory, redirect, url_for
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Optional, NumberRange
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
import os
import base64
from PIL import Image
from io import BytesIO
import json
import lxml.etree as ET

# Импортируем пользовательские модули для работы с нейросетью и изображениями
import net as neuronet
import image_operation

# Создаем экземпляр Flask-приложения
app = Flask(__name__)

# Инициализируем Bootstrap для использования в шаблонах
bootstrap = Bootstrap(app)

# Устанавливаем секретный ключ для защиты сессий и CSRF
SECRET_KEY = "d090728025bb514707d794d4d2aeffd9"
app.config["SECRET_KEY"] = SECRET_KEY

# Конфигурация reCAPTCHA для защиты форм от ботов
app.config["RECAPTCHA_USE_SSL"] = False
app.config["RECAPTCHA_PUBLIC_KEY"] = "6LdEcBYrAAAAAH3o_kMpRMuSeJD5pvMUVGJ6ojw7"
app.config["RECAPTCHA_PRIVATE_KEY"] = "6LdEcBYrAAAAAC97LUi7cPMPV8v4EUo7N-78QQBA"
app.config["RECAPTCHA_OPTIONS"] = {"theme": "white"}

@app.route("/hello_world")
def hello():
    return " <html><head></head> <body> Hello World! </body></html>"

# Маршрут для передачи данных в шаблон
@app.route("/data_to")
def data_to():
    # Создаем данные для передачи в шаблон
    some_pars = {"user": "Ivan", "color": "red"}  # Словарь с параметрами
    some_str = "Hello my dear friends!"  # Строка
    some_value = 10  # Числовое значение

    # Передаем данные в шаблон simple.html
    return render_template(
        "simple.html", 
        some_str=some_str, 
        some_value=some_value, 
        some_pars=some_pars
    )

# Маршрут для скачивания файла
@app.route('/download/<filename>')
def download_file(filename):
    """
    Маршрут для скачивания файла.
    :param filename: Имя файла для скачивания.
    """
    upload_folder = "./static"  # Путь к папке с файлами
    
    # Проверяем, существует ли файл
    if not os.path.exists(os.path.join(upload_folder, filename)):
        flash("Файл не найден.", "danger")  # Сообщение об ошибке
        return redirect(url_for('image_resize'))  # Перенаправление на страницу изменения размера
    
    # Отправляем файл для скачивания
    return send_from_directory(
        directory=upload_folder,
        path=filename,
        as_attachment=True  # Файл будет скачиваться, а не отображаться в браузере
    )

# Форма для загрузки изображения и проверки через reCAPTCHA
class NetForm(FlaskForm):
    openid = StringField("openid", validators=[DataRequired()])  # Поле для ввода текста (обязательное)
    upload = FileField(
        "Load image",  # Поле для загрузки файла
        validators=[
            FileRequired(),  # Файл обязателен
            FileAllowed(["jpg", "png", "jpeg"], "Image only!")  # Разрешены только изображения
        ],
    )
    recaptcha = RecaptchaField()  # Поле reCAPTCHA для защиты от ботов
    submit = SubmitField("send")  # Кнопка отправки формы

# Маршрут для работы с нейросетью
@app.route("/net", methods=["GET", "POST"])
def net():
    form = NetForm()  # Создаем экземпляр формы
    filename = None  # Переменная для имени файла
    neurodic = {}  # Словарь для хранения результатов работы нейросети

    # Если форма отправлена и прошла валидацию
    if form.validate_on_submit():
        # Сохраняем загруженный файл
        filename = os.path.join("./static", secure_filename(form.upload.data.filename))
        
        # Читаем изображение и получаем результаты от нейросети
        fcount, fimage = neuronet.read_image_file(10, "./static")
        decode = neuronet.getresult(fimage)

        # Заполняем словарь результатами работы нейросети
        for elem in decode:
            neurodic[elem[0][1]] = elem[0][2]

        # Сохраняем загруженный файл
        form.upload.data.save(filename)

    # Передаем данные в шаблон net.html
    return render_template(
        "net.html", 
        form=form, 
        image_name=filename, 
        neurodic=neurodic
    )

# API для работы с нейросетью через JSON
@app.route("/apinet", methods=["GET", "POST"])
def apinet():
    neurodic = {}  # Словарь для хранения результатов работы нейросети

    # Проверяем, что запрос содержит данные в формате JSON
    if request.mimetype == "application/json":
        data = request.get_json()  # Получаем данные из запроса

        # Декодируем изображение из Base64
        filebytes = data["imagebin"].encode("utf-8")
        cfile = base64.b64decode(filebytes)
        img = Image.open(BytesIO(cfile))  # Открываем изображение с помощью PIL

        # Получаем результаты от нейросети
        decode = neuronet.getresult([img])
        for elem in decode:
            neurodic[elem[0][1]] = str(elem[0][2])  # Заполняем словарь результатами

        # Преобразуем результаты в JSON и возвращаем ответ
        ret = json.dumps(neurodic)
        resp = Response(response=ret, status=200, mimetype="application/json")
        return resp

# API для преобразования XML в HTML с использованием XSLT
@app.route("/apixml", methods=['GET', 'POST'])
def apixml():
    # Парсим XML и XSLT файлы
    dom = ET.parse("./static/xml/file.xml")  # Исходный XML
    xslt = ET.parse("./static/xml/file.xslt")  # XSLT для преобразования
    transform = ET.XSLT(xslt)  # Создаем объект трансформации
    newhtml = transform(dom)  # Применяем трансформацию

    # Преобразуем результат в строку и возвращаем его
    strfile = ET.tostring(newhtml)
    return strfile

# Форма для изменения размера изображения
class ResizeForm(FlaskForm):
    upload = FileField(
        "Загрузите изображение",  # Поле для загрузки файла
        validators=[
            FileRequired(message="Файл обязателен!"),  # Файл обязателен
            FileAllowed(["jpg", "png", "jpeg", "gif"], message="Разрешены только изображения (JPG, PNG, JPEG, GIF)!"),
        ],
    )
    percent = IntegerField(
        "Проценты (%)",  # Поле для изменения размера в процентах
        validators=[Optional(), NumberRange(min=1, max=500, message="Введите значение от 1 до 500")],
    )
    width = IntegerField(
        "Ширина (px)",  # Поле для изменения ширины
        validators=[Optional(), NumberRange(min=1, max=5000, message="Введите значение от 1 до 5000")],
    )
    height = IntegerField(
        "Высота (px)",  # Поле для изменения высоты
        validators=[Optional(), NumberRange(min=1, max=5000, message="Введите значение от 1 до 5000")],
    )
    submit = SubmitField("Загрузить")  # Кнопка отправки формы

# Маршрут для изменения размера изображения
@app.route("/", methods=['GET', 'POST'])
def image_resize():
    form = ResizeForm()  # Создаем экземпляр формы

    # Инициализация переменных
    original_image = None  # Оригинальное изображение
    resized_image = None  # Измененное изображение
    original_histogram = None  # Гистограмма оригинального изображения
    resized_histogram = None  # Гистограмма измененного изображения

    # Если форма отправлена и прошла валидацию
    if form.validate_on_submit():
        upload_folder = "./static"  # Папка для сохранения файлов
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)  # Создаем папку, если она не существует

        uploaded_file = form.upload.data  # Получаем загруженный файл
        if uploaded_file:
            try:
                # Сохраняем оригинальный файл
                original_filename = secure_filename(uploaded_file.filename)
                original_path = os.path.join(upload_folder, original_filename)
                uploaded_file.save(original_path)

                # Определяем режим изменения размера
                mode = request.form.get("resize_mode")  # Режим изменения размера
                percent = form.percent.data  # Проценты
                width = form.width.data  # Ширина
                height = form.height.data  # Высота
                keep_aspect_ratio = request.form.get("keep_aspect_ratio") == "on"  # Сохранение пропорций

                # Генерируем имя для измененного файла
                name, ext = os.path.splitext(original_filename)
                resized_filename = f"{name}_resized{ext}"
                resized_path = os.path.join(upload_folder, resized_filename)

                # Изменяем размер изображения
                image_operation.resize_image(
                    image_path=original_path,
                    output_path=resized_path,
                    mode=mode,
                    percent=percent,
                    width=width,
                    height=height,
                    keep_aspect_ratio=keep_aspect_ratio
                )

                # Сохраняем графики распределения цветов
                original_histogram_name = f"{name}_histogram_original.png"
                original_histogram_path = os.path.join(upload_folder, original_histogram_name)
                image_operation.plot_color_images(original_path, original_histogram_path)

                resized_histogram_name = f"{name}_histogram_resized.png"
                resized_histogram_path = os.path.join(upload_folder, resized_histogram_name)
                image_operation.plot_color_images(resized_path, resized_histogram_path)

                flash("Изображение успешно изменено.", "success")  # Сообщение об успехе

                # Обновляем переменные для отображения
                original_image = original_filename
                resized_image = resized_filename
                original_histogram = original_histogram_name
                resized_histogram = resized_histogram_name

            except Exception as e:
                flash(f"Ошибка при изменении изображения: {e}", "danger")  # Сообщение об ошибке
        else:
            flash("Файл не был загружен.", "warning")  # Сообщение о том, что файл не загружен

    # Проверка существования файлов перед передачей в шаблон
    if original_image and os.path.exists(os.path.join("./static", original_image)):
        original_image = original_image
    else:
        original_image = None

    if resized_image and os.path.exists(os.path.join("./static", resized_image)):
        resized_image = resized_image
    else:
        resized_image = None

    if original_histogram and os.path.exists(os.path.join("./static", original_histogram)):
        original_histogram = original_histogram
    else:
        original_histogram = None

    if resized_histogram and os.path.exists(os.path.join("./static", resized_histogram)):
        resized_histogram = resized_histogram
    else:
        resized_histogram = None

    # Передаем данные в шаблон resize.html
    return render_template(
        "resize.html",
        form=form,
        original_image=original_image,
        resized_image=resized_image,
        original_histogram=original_histogram,
        resized_histogram=resized_histogram
    )

# Запуск приложения
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)  # Запуск приложения на локальном сервере