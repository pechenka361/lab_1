from PIL import Image
import matplotlib.pyplot as plt
import numpy as np


def plot_color_images(image_path, output_path):
    img = Image.open(image_path)
    img_array = np.array(img)

    r, g, b = img_array[:, :, 0], img_array[:, :, 1], img_array[:, :, 2]

    plt.figure(figsize=(10, 5))
    plt.subplot(1, 3, 1)
    plt.hist(r.ravel(), bins=256, color='red')
    plt.title('Red chanel')
    plt.xlim([0, 256])

    plt.subplot(1, 3, 2)
    plt.hist(r.ravel(), bins=256, color='green')
    plt.title('Green chanel')
    plt.xlim([0, 256])

    plt.subplot(1, 3, 3)
    plt.hist(r.ravel(), bins=256, color='blue')
    plt.title('Blue chanel')
    plt.xlim([0, 256])
    
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

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
                new_height = int(width/aspect_ratio)
                new_width = int(width)
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
