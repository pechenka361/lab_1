from flask import Flask, render_template, request, Response, flash
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
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
        "Load image",
        validators=[
            FileRequired(),
            FileAllowed(["jpg", "png", "jpeg"], "Image only!0"),
        ],
    )
    recaptcha = RecaptchaField()
    submit = SubmitField("send")

@app.route("/image_resize", methods=['GET', 'POST'])

def image_resize():
    form = ResizeForm()
    filename = None

    if form.validate_on_submit():
        # Проверка наличия директории ./static
        upload_folder = "./static"
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)  # Создаем директорию, если её нет

        # Получение файла из формы
        uploaded_file = form.upload.data
        if uploaded_file:
            # Проверка расширения файла
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
            file_extension = uploaded_file.filename.rsplit('.', 1)[-1].lower()
            if file_extension not in allowed_extensions:
                flash("Недопустимый формат файла. Разрешены только PNG, JPG, JPEG, GIF.", "danger")
                print("Недопустимый формат файла. Разрешены только PNG, JPG, JPEG, GIF.", "danger")
                return render_template("resize.html", form=form, image_name=filename)

            # Сохранение файла
            try:
                filename = os.path.join(upload_folder, secure_filename(uploaded_file.filename))
                uploaded_file.save(filename)
                flash("Файл успешно загружен.", "success")
                print("Файл успешно загружен.", "success")
            except Exception as e:
                flash(f"Ошибка при сохранении файла: {e}", "danger")
                print(f"Ошибка при сохранении файла: {e}", "danger")
        else:
            flash("Файл не был загружен.", "warning")
            print("Файл не был загружен.", "warning")

    return render_template("resize.html", form=form, image_name=filename)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
