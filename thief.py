from colorthief import ColorThief
import numpy as np
from PIL import Image, ImageDraw
import math
import colorsys
import shutil
import requests


class Thief:
    def __init__(self, user):
        self.user = user
        self.profile_image_url = user['url']
        self.file = None
        self.path = "./img/"

    def download_profile_image(self):
        url = self.profile_image_url
        url = url.replace('_normal', '')

        response = requests.get(url, stream=True)
        file = f"{self.user['screen_name']}_original.png"
        with open(self.path + file, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)

        self.file = file

    def sort_luminance(self, rgb, repetitions=1):
        r = rgb[0]
        g = rgb[1]
        b = rgb[2]

        lum = math.sqrt(.241 * r + .691 * g + .068 * b)

        h, _, v = colorsys.rgb_to_hsv(r, g, b)

        h2 = int(h * repetitions)
        lum2 = int(lum * repetitions)
        v2 = int(v * repetitions)

        if h2 % 2 == 1:
            v2 = repetitions - v2
            lum = repetitions - lum

        return (h2, lum2, v2)

    def generate_pattern(self, n_palette):
        color_thief = ColorThief(self.path + self.file)

        palette = color_thief.get_palette(color_count=n_palette)
        palette.sort(key=lambda rgb: self.sort_luminance(rgb, 16))
        print(palette)

        w = 500
        h = w // n_palette

        list_colors = [Image.new("RGB", (w, h), color=i)
                       for i in palette]

        min_shape = sorted([(np.sum(i.size), i.size)
                            for i in list_colors])[0][1]
        palettes = np.vstack((np.asarray(i.resize(min_shape))
                              for i in list_colors))

        palettes = Image.fromarray(palettes)

        file = self.file.replace('_original', '_palette')
        palettes.show()
        return palettes.save(self.path + file)

    def step_gradient(self, color, mid_color, final_color):
        img = Image.new("RGB", (500, 500), "#FFFFFF")
        draw = ImageDraw.Draw(img)

        r, g, b = color[0], color[1], color[2]
        r_mid, g_mid, b_mid = mid_color[0], mid_color[1], mid_color[2]
        r_final, g_final, b_final = final_color[0], final_color[1], final_color[2]

        r_start_to_mid = np.linspace(r, r_mid, num=150)
        g_start_to_mid = np.linspace(g, g_mid, num=150)
        b_start_to_mid = np.linspace(b, b_mid, num=150)

        r_mid_to_final = np.linspace(r_mid, r_final, num=350)
        g_mid_to_final = np.linspace(g_mid, g_final, num=350)
        b_mid_to_final = np.linspace(b_mid, b_final, num=350)

        r_final = [*r_start_to_mid, *r_mid_to_final]
        g_final = [*g_start_to_mid, *g_mid_to_final]
        b_final = [*b_start_to_mid, *b_mid_to_final]

        list_color = [r_final, g_final, b_final]

        for i in range(500):
            # (0, i, 500, i) draw from top to bottom
            draw.line((0, i, 500, i), fill=(
                int(list_color[0][i]), int(list_color[1][i]), int(list_color[2][i])))

        img.show()
