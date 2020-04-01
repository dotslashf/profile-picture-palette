from colorthief import ColorThief
import numpy as np
from PIL import Image

color_thief = ColorThief('./img/test.png')

dominant_color = color_thief.get_color(quality=1)

palette = color_thief.get_palette(color_count=5)

list_imgs = [Image.new("RGB", (500, 100), color=i) for i in palette]

min_shape = sorted([(np.sum(i.size), i.size) for i in list_imgs])[0][1]
imgs_comb = np.vstack((np.asarray(i.resize(min_shape)) for i in list_imgs))

imgs_comb = Image.fromarray(imgs_comb)
imgs_comb.show()
