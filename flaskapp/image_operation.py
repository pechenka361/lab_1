from PIL import Image
import matplotlib.pyplot as plt
import numpy as np

def plot_color_images(image_path, output_path):
    """
    Функция для построения гистограмм распределения цветов изображения.
    
    :param image_path: Путь к исходному изображению.
    :param output_path: Путь для сохранения графика с гистограммами.
    """
    # Открываем изображение с помощью PIL
    img = Image.open(image_path)
    
    # Преобразуем изображение в массив NumPy для удобной работы с каналами RGB
    img_array = np.array(img)

    # Разделяем массив на отдельные каналы (красный, зеленый, синий)
    r, g, b = img_array[:, :, 0], img_array[:, :, 1], img_array[:, :, 2]

    # Создаем новую фигуру для графиков размером 10x5
    plt.figure(figsize=(10, 5))

    # Гистограмма для красного канала
    plt.subplot(1, 3, 1)  # Создаем первый подграфик (1 строка, 3 столбца, 1-й график)
    plt.hist(r.ravel(), bins=256, color='red')  # Строим гистограмму значений красного канала
    plt.title('Red channel')  # Заголовок графика
    plt.xlim([0, 256])  # Устанавливаем пределы оси X (значения пикселей от 0 до 255)

    # Гистограмма для зеленого канала
    plt.subplot(1, 3, 2)  # Создаем второй подграфик (1 строка, 3 столбца, 2-й график)
    plt.hist(g.ravel(), bins=256, color='green')  # Строим гистограмму значений зеленого канала
    plt.title('Green channel')  # Заголовок графика
    plt.xlim([0, 256])  # Устанавливаем пределы оси X

    # Гистограмма для синего канала
    plt.subplot(1, 3, 3)  # Создаем третий подграфик (1 строка, 3 столбца, 3-й график)
    plt.hist(b.ravel(), bins=256, color='blue')  # Строим гистограмму значений синего канала
    plt.title('Blue channel')  # Заголовок графика
    plt.xlim([0, 256])  # Устанавливаем пределы оси X

    # Настройка макета графиков для избежания пересечений
    plt.tight_layout()
    
    # Сохраняем график в указанный файл
    plt.savefig(output_path)
    
    # Закрываем график, чтобы освободить память
    plt.close()


def resize_image(image_path, output_path, mode, percent=None, width=None, height=None, keep_aspect_ratio=True):
    """
    Функция для изменения размера изображения.
    
    :param image_path: Путь к исходному изображению.
    :param output_path: Путь для сохранения измененного изображения.
    :param mode: Режим изменения размера ("percent" или "pixels").
    :param percent: Процент изменения размера (используется только при mode="percent").
    :param width: Новая ширина изображения (используется только при mode="pixels").
    :param height: Новая высота изображения (используется только при mode="pixels").
    :param keep_aspect_ratio: Флаг для сохранения пропорций изображения (по умолчанию True).
    """
    # Открываем изображение с помощью PIL
    with Image.open(image_path) as img:
        # Определяем новый размер изображения в зависимости от режима
        if mode == "percent":
            # Если выбран режим изменения размера в процентах
            if percent is None:
                raise ValueError("Необходимо указать процент для изменения размера")
            
            # Вычисляем новые ширину и высоту как процент от оригинальных размеров
            new_width = int(img.width * percent / 100)
            new_height = int(img.height * percent / 100)
        
        elif mode == "pixels":
            # Если выбран режим изменения размера в пикселях
            if keep_aspect_ratio:
                # Если нужно сохранить пропорции изображения
                aspect_ratio = img.width / img.height  # Соотношение сторон
                if width is not None:
                    # Вычисляем высоту на основе заданной ширины и соотношения сторон
                    new_height = int(width / aspect_ratio)
                    new_width = int(width)
                elif height is not None:
                    # Вычисляем ширину на основе заданной высоты и соотношения сторон
                    new_width = int(height * aspect_ratio)
                    new_height = int(height)
            else:
                # Если не нужно сохранять пропорции
                if width is None or height is None:
                    raise ValueError("Необходимо указать ширину и высоту для изменения размера")
                new_width = width
                new_height = height
        
        else:
            # Если указан неверный режим изменения размера
            raise ValueError("Неверный режим изменения размера")

        # Изменяем размер изображения с использованием фильтра LANCZOS для лучшего качества
        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Сохраняем измененное изображение в указанный файл
        resized_img.save(output_path)