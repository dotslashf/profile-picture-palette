from colorthief import ColorThief
import numpy as np
from PIL import Image, ImageDraw
import math
import colorsys
import shutil
import requests
import os


class Thief:
    def __init__(self, user):
        self.user = user
        self.profile_image_url = user.profile_image_url_https
        self.file = None
        self.path = "./img/"
        self.palette = []

    def download_profile_image(self):
        url = self.profile_image_url
        url = url.replace('_normal', '')

        response = requests.get(url, stream=True)
        file = f"{self.user.screen_name}_original.png"
        try:
            with open(self.path + 'original/' + file, 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
        except FileNotFoundError as e:
            print(f"{e}, Creating the folder and save it")
            os.makedirs(self.path + 'original')
            with open(self.path + 'original/' + file, 'wb') as out_file:
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

    def generate_pattern(self, n_palette=5):
        color_thief = ColorThief(self.path + "original/" + self.file)

        palette = color_thief.get_palette(color_count=n_palette)
        palette.sort(key=lambda rgb: self.sort_luminance(rgb, 16))
        self.palette = palette

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
        try:
            palettes.save(self.path + 'palette/' + file)
        except FileNotFoundError as e:
            print(f"{e}, Creating the folder and save it")
            os.makedirs(self.path + 'palette')
            palettes.save(self.path + 'palette/' + file)

    def first_last_color_to_gradient(self):
        img = Image.new("RGB", (500, 500), "#FFFFFF")
        draw = ImageDraw.Draw(img)

        first_r, first_g, first_b = self.palette[0][0], self.palette[0][1], self.palette[0][2]
        last_r, last_g, last_b = self.palette[-1][0], self.palette[-1][1], self.palette[-1][2]

        r, g, b = (np.linspace(first_r, last_r, num=500),
                   np.linspace(first_g, last_g, num=500),
                   np.linspace(first_b, last_b, num=500))

        for i in range(500):
            # (0, i, 500, i) draw from top to bottom
            draw.line((0, i, 500, i), fill=(
                int(r[i]), int(g[i]), int(b[i])))

        file = self.file.replace('_original', '_first_last_to_gradient')
        try:
            img.save(self.path + 'first_last_to_gradient/' + file)
        except FileNotFoundError as e:
            print(f"{e}, Creating the folder and save it")
            os.makedirs(self.path + 'first_last_to_gradient')
            img.save(self.path + 'first_last_to_gradient/' + file)

    def palette_to_gradient(self):
        img = Image.new("RGB", (500, 500), "#FFFFFF")
        draw = ImageDraw.Draw(img)

        colors = {}
        for i in range(5):
            key = "color_" + str(i)
            value = self.palette[i]
            colors[key] = value

        rgb_step = {}
        for i in range(4):
            key = "rgb_" + str(i)
            value = (np.linspace(colors[f"color_{i}"][0],
                                 colors[f"color_{i+1}"][0], num=125),
                     np.linspace(colors[f"color_{i}"][1],
                                 colors[f"color_{i+1}"][1], num=125),
                     np.linspace(colors[f"color_{i}"][2],
                                 colors[f"color_{i+1}"][2], num=125))
            rgb_step[key] = value

        r_final = np.concatenate([rgb_step[f"rgb_{i}"][0] for i in range(4)])
        g_final = np.concatenate([rgb_step[f"rgb_{i}"][1] for i in range(4)])
        b_final = np.concatenate([rgb_step[f"rgb_{i}"][2] for i in range(4)])

        r_final = r_final.tolist()
        g_final = g_final.tolist()
        b_final = b_final.tolist()

        for i in range(500):
            # (0, i, 500, i) draw from top to bottom
            draw.line((0, i, 500, i), fill=(
                int(r_final[i]), int(g_final[i]), int(b_final[i])))

        file = self.file.replace('_original', '_palette_to_gradient')
        try:
            img.save(self.path + 'palette_to_gradient/' + file)
        except OSError as e:
            print(f"{e}, Creating the folder and save it")
            os.makedirs(self.path + 'palette_to_gradient')
            img.save(self.path + 'palette_to_gradient/' + file)

    def dominant_color(self):
        color_thief = ColorThief(self.path + "original/" + self.file)
        dominant = color_thief.get_color()

        w = 500
        h = 500

        img = Image.new("RGB", (w, h), color=dominant)
        file = self.file.replace('_original', '_dominant')
        try:
            img.save(self.path + 'dominant/' + file)
        except FileNotFoundError as e:
            print(f"{e}, Creating the folder and save it")
            os.makedirs(self.path + 'dominant')
            img.save(self.path + 'dominant/' + file)
