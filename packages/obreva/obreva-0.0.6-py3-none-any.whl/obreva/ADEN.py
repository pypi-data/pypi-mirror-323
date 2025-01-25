from PIL import Image, ImageDraw, ImageFilter
import math
import random
import time

def create_cosmic_gradient(width, height):
    """Создает градиент космических цветов с туманностями и пылевыми облаками."""
    image = Image.new("RGB", (width, height))
    pixels = image.load()

    total_pixels = width * height
    processed_pixels = 0
    start_time = time.time()
    
    for y in range(height):
        for x in range(width):
          #  Случайные цвета для звезд
           if random.random() < 0.00003:
               pixels[x, y] = (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255))
           else:
            t = y / height

            r = int(255 * (0.2 + 0.8 * math.sin(t * 2 * math.pi / 2 + 0.5 * math.pi) ** 2) ** 1.5)
            g = int(255 * (0.1 + 0.9 * math.sin(t * 2 * math.pi / 2 + 0.4 * math.pi) ** 2) ** 1.5)
            b = int(255 * (0.3 + 0.7 * math.sin(t * 2 * math.pi / 2 + 0.2 * math.pi) ** 2) ** 1.5)
            # Туманности (неправильные)
            
            dx = x - width // 2
            dy = y - height // 2
            dist_center = math.sqrt(dx**2 + dy**2)
            if random.random() < 0.005 * math.exp(- (dist_center/ (width/3))**2):
                r = int(0.75 * r + 255 / 4)
                g = int(0.75 * g + 255 / 4)
                b = int(0.75 * b + 255 / 4)
           
           
            # Пылевые облака
            if random.random() < 0.0005:
              intensity = random.random()*150
              r = int(max(0,min(255,r - intensity/1.5)))
              g = int(max(0,min(255,g - intensity)))
              b = int(max(0,min(255,b - intensity*1.5)))
            
            pixels[x, y] = (r, g, b)

           processed_pixels += 1
           if processed_pixels % (total_pixels // 100) == 0:
              percent = int((processed_pixels / total_pixels) * 100)
              elapsed_time = time.time() - start_time
              print(f"Загрузка градиента: {percent}% ({elapsed_time:.2f} секунд)", end="\r")
    print("\nЗагрузка градиента завершена.")
    return image


def gamma_correct(color, gamma=2.2):
    """Применяет гамма-коррекцию к RGB-цвету."""
    r, g, b = color
    r = int(255 * (r / 255) ** (1 / gamma))
    g = int(255 * (g / 255) ** (1 / gamma))
    b = int(255 * (b / 255) ** (1 / gamma))
    return (r, g, b)
    
def draw_black_hole(width, height, black_hole_x, black_hole_y, radius, initial_image=None, upscale_factor = 2):
    """Рисует черную дыру и ее искривление пространства.
    Args:
        width (int): Ширина изображения.
        height (int): Высота изображения.
        black_hole_x (int): X-координата центра черной дыры.
        black_hole_y (int): Y-координата центра черной дыры.
        radius (int): Радиус черной дыры (эффект искривления).
        initial_image (PIL.Image): Исходное изображение для искажения.
        upscale_factor (float): Во сколько раз увеличиваем изображение при рисовании.
    """
    
    upscaled_width = int(width * upscale_factor)
    upscaled_height = int(height * upscale_factor)
    upscaled_black_hole_x = int(black_hole_x * upscale_factor)
    upscaled_black_hole_y = int(black_hole_y * upscale_factor)
    upscaled_radius = int(radius * upscale_factor)
    
    blur_radius = 0.4 * upscale_factor


    if initial_image is None:
        upscaled_image = create_cosmic_gradient(upscaled_width, upscaled_height)
    else:
        upscaled_image = initial_image.resize((upscaled_width, upscaled_height), resample=Image.BILINEAR).copy()
    
    pixels = upscaled_image.load()

    total_pixels = upscaled_width * upscaled_height
    processed_pixels = 0
    start_time = time.time()
    
    for x in range(upscaled_width):
        for y in range(upscaled_height):
            dx = x - upscaled_black_hole_x
            dy = y - upscaled_black_hole_y
            dist = math.sqrt(dx**2 + dy**2)
        
            if dist < upscaled_radius:  # Внутри черной дыры заменяем черным цветом на градиент
              
               # Искривление пространства вокруг черной дыры
                if dist > 0:
                   distortion_factor = (upscaled_radius / dist) ** 1.7
                else:
                   distortion_factor = 0
                   
                # Вычисление угла
                angle = math.atan2(dy, dx)

                # Искажаем пиксель в сторону черной дыры
                new_x = int(upscaled_black_hole_x + dx * (1 - distortion_factor))
                new_y = int(upscaled_black_hole_y + dy * (1 - distortion_factor))

                # Обеспечиваем, что координаты остаются в пределах изображения
                
                # Создаем эффект "зацикленности" по горизонтали
                new_x = new_x % upscaled_width
                
                if 0 <= new_x < upscaled_width and 0 <= new_y < upscaled_height:
                   try:
                      pixels[x, y] = gamma_correct(pixels[new_x, new_y])
                   except IndexError:
                        pass
                
            else:
            # Искривление пространства вокруг черной дыры
                if dist > 0:
                     distortion_factor = (upscaled_radius / dist) ** 1.7
                else:
                     distortion_factor = 0

                # Вычисление угла
                angle = math.atan2(dy, dx)
                
                # Искажаем пиксель в сторону черной дыры
                new_x = int(upscaled_black_hole_x + dx * (1 - distortion_factor))
                new_y = int(upscaled_black_hole_y + dy * (1 - distortion_factor))
                
                # Создаем эффект "зацикленности" по горизонтали
                new_x = new_x % upscaled_width


                # Обеспечиваем, что координаты остаются в пределах изображения
                if 0 <= new_x < upscaled_width and 0 <= new_y < upscaled_height:
                    try:
                         pixels[x, y] = gamma_correct(pixels[new_x, new_y])
                    except IndexError:
                         pass
        processed_pixels += 1
        if processed_pixels % (total_pixels // 100) == 0:
          percent = int((processed_pixels / total_pixels) * 100)
          elapsed_time = time.time() - start_time
          print(f"Загрузка: {percent}% ({elapsed_time:.2f} секунд)", end="\r")
    
    upscaled_image = upscaled_image.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    image = upscaled_image.resize((width, height), resample=Image.BILINEAR) # уменьшаем обратно с фильтрацией
    image = image.filter(ImageFilter.UnsharpMask(radius=1, percent=120))
    
    return image
width = 1024
height = 1000
def start():
    black_hole_x = width // 2
    black_hole_y = height // 2
    radius = min(width, height) // 4
    image = draw_black_hole(width, height, black_hole_x, black_hole_y, radius, upscale_factor=3)
    image.save("black_hole.png")
    image.show()
    print("\nИзображение черной дыры сохранено в black_hole.png")
