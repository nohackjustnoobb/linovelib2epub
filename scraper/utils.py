from PIL import Image
from io import BytesIO


def resp2image(resp):
    img = Image.open(BytesIO(resp.content))

    if img.format not in ["PNG", "JPEG"]:
        png_image = BytesIO()
        img.save(png_image, format="PNG")
        return (png_image.getvalue(), "png")

    return (resp.content, img.format.lower())


class Progress:
    pass
