from flask import Flask, render_template, request, Response, flash
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, TextAreaField, IntegerField
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

import net as neuronet

app = Flask(__name__)
bootstrap = Bootstrap(app)

SECRET_KEY = "d090728025bb514707d794d4d2aeffd9"
app.config["SECRET_KEY"] = SECRET_KEY
app.config["RECAPTCHA_USE_SSL"] = False
app.config["RECAPTCHA_PUBLIC_KEY"] = "6LdEcBYrAAAAAH3o_kMpRMuSeJD5pvMUVGJ6ojw7"
app.config["RECAPTCHA_PRIVATE_KEY"] = "6LdEcBYrAAAAAC97LUi7cPMPV8v4EUo7N-78QQBA"
app.config["RECAPTCHA_OPTIONS"] = {"theme": "white"}


@app.route("/")
def hello():
    return " <html><head></head> <body> Hello World! </body></html>"


@app.route("/data_to")
def data_to():
    some_pars = {"user": "Ivan", "color": "red"}
    some_str = "Hello my dear friends!"
    some_value = 10

    return render_template(
        "simple.html", some_str=some_str, some_value=some_value, some_pars=some_pars
    )


class NetForm(FlaskForm):
    openid = StringField("openid", validators=[DataRequired()])
    upload = FileField(
        "Load image",
        validators=[
            FileRequired(),
            FileAllowed(["jpg", "png", "jpeg"], "Image only!0"),
        ],
    )
    recaptcha = RecaptchaField()
    submit = SubmitField("send")


@app.route("/net", methods=["GET", "POST"])
def net():
    form = NetForm()
    filename = None
    neurodic = {}
    if form.validate_on_submit():
        filename = os.path.join("./static", secure_filename(form.upload.data.filename))
        fcount, fimage = neuronet.read_image_file(10, "./static")
        decode = neuronet.getresult(fimage)

        for elem in decode:
            neurodic[elem[0][1]] = elem[0][2]

        form.upload.data.save(filename)
    return render_template(
        "net.html", form=form, image_name=filename, neurodic=neurodic
    )


@app.route("/apinet", methods=["GET", "POST"])
def apinet():
    neurodic = {}
    if request.mimetype == "application/json":
        data = request.get_json()
    filebytes = data["imagebin"].encode("utf-8")
    cfile = base64.b64decode(filebytes)
    img = Image.open(BytesIO(cfile))
    decode = neuronet.getresult([img])
    neurodic = {}
    for elem in decode:
        neurodic[elem[0][1]] = str(elem[0][2])
        print(elem)
    ret = json.dumps(neurodic)
    resp = Response(response=ret, status=200, mimetype="application/json")
    return resp

@app.route("/apixml", methods=['GET', 'POST'])
def apixml():
    dom = ET.parse("./static/xml/file.xml")
    xslt = ET.parse("./static/xml/file.xslt")
    transform = ET.XSLT(xslt)
    newhtml = transform(dom)
    strfile = ET.tostring(newhtml)
    return strfile

class ResizeForm(FlaskForm):
    upload = FileField(
        "Загрузите изображение",
        validators=[
            FileRequired(message="Файл обязателен!"),
            FileAllowed(["jpg", "png", "jpeg", "gif"], message="Разрешены только изображения (JPG, PNG, JPEG, GIF)!"),
        ],
    )
    percent = IntegerField(
        "Проценты (%)",
        validators=[Optional(), NumberRange(min=1, max=500, message="Введите значение от 1 до 500")],
    )
    width = IntegerField(
        "Ширина (px)",
        validators=[Optional(), NumberRange(min=1, max=5000, message="Введите знаячение от 1 до 5000")],
    )
    height = IntegerField(
        "Высота (px)",
        validators=[Optional(), NumberRange(min=1, max=5000, message="Введите значение от 1 до 5000")],
    )
    submit = SubmitField("Загрузить")

def resize_image(image_path, output_path, mode, percent=None, width=None, height=None, keep_aspect_ratio=True):
    with Image.open(image_path) as img: 
        if mode == "percent":
            if percent is None:
                raise ValueError("необходимо указать процент для изменения размера")
            new_width = int(img.width*percent / 100)
            new_height = int(img.height*percent / 100)
        elif mode == "pixels":
            if keep_aspect_ratio:
                aspect_ratio = img.width/img.height
                if width / height > aspect_ratio:
                    new_width = int(height*aspect_ratio)
                else:
                    new_height = int(width/aspect_ratio)
            else:
                if width is None or height is None:
                    raise ValueError("Необходимо указать ширину и высоту для изменения размера")
                else:
                    new_width = width
                    new_height = height

        else: 
            raise ValueError("Неверный режим изменения размера")
        
        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        resized_img.save(output_path)

@app.route("/image_resize", methods=['GET', 'POST'])
def image_resize():
    form = ResizeForm()
    filename = None
    resized_filename = None

    if form.validate_on_submit():
        upload_folder = "./static"
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        uploaded_file = form.upload.data
        if uploaded_file:
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
            file_extension = uploaded_file.filename.rsplit('.', 1)[-1].lower()
            if file_extension not in allowed_extensions:
                flash("Недопустимый формат файла. Разрешены только PNG, JPG, JPEG, GIF.", "danger")
                return render_template("resize.html", form=form, image_name=filename)

            # Сохранение файла
            try:
                filename = secure_filename(uploaded_file.filename)
                original_path = os.path.join(upload_folder, filename)
                uploaded_file.save(original_path)
                mode = request.form.get("resize_mode")
                percent = form.percent.data
                width = form.width.data
                height = form.height.data
                keep_aspect_ratio = request.form.get("keep_aspect_ratio") == "on"

                name, ext = os.path.splitext(filename)
                resized_filename = f"{name}_resized{ext}"
                resize_path = os.path.join(upload_folder, resized_filename)

                resize_image(
                    image_path=original_path,
                    output_path=resize_path,
                    mode=mode,
                    percent=percent,
                    width=width,
                    height=height,
                    keep_aspect_ratio=keep_aspect_ratio
                )
                flash("Изображение успешно изменено.", "success")
            except Exception as e:
                flash(f"Ошибка при изменении изображения: {e}", "danger")
        else:
            flash("Файл не был загружен.", "warning")

    return render_template("resize.html", form=form, image_name=filename)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
