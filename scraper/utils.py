from PIL import Image
from io import BytesIO


# TODO use original image
def resp2image(resp):
    img = Image.open(BytesIO(resp.content))
    png_image = BytesIO()
    img.save(png_image, format="PNG")

    return png_image.getvalue()
