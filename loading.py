from pygame import image as Image
from pygame import Surface, error


def load_image(path: str) -> Surface:
    try:
        img = Image.load(path)
        return img
    except error:
        print("can not load spritesheet " + path)
        #raise SystemExit(error)
        return


map = load_image("map.png")
