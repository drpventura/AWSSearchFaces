from PIL import Image, ImageDraw
from io import BytesIO
from typing import Dict


def create_pillow_img(img) -> Image:
    """
    Creates and returns a Pillow image from the given image bytes
    :param img: either the bytes of the image, or the filename or URL
    """
    if type(img) == str:
        from image_loaders import get_image
        img = get_image(img)
    return Image.open(BytesIO(img))


def bbox_to_coords(bbox: Dict[str, float], img_width: int, img_height: int):
    """
    Given a bounding box (dictionary) from Rekognition
    returns the corresponding coords
    suitable for use with ImageDraw rectangle
    :param bbox: (a dictionary) that contains the bounding box from Rekognition
    :param img_width: the overall width of the image
    :param img_height: the overall height of the image
    :return: the corresponding coords suitable for use with ImageDraw rectangle
    """
    upper_left_x = bbox['Left'] * img_width
    upper_y = bbox['Top'] * img_height
    bottom_right_x = upper_left_x + (bbox['Width'] * img_width)
    bottom_y = upper_y + (bbox['Height'] * img_height)
    return [upper_left_x, upper_y, bottom_right_x, bottom_y]


def draw_box(img, bbox: Dict[str, float])-> Image:
    if type(img) == str:
        from image_loaders import get_image
        img = create_pillow_img(get_image(img))

    # Get the size of the image
    (img_width, img_height) = img.size

    # create a ImageDraw object to allow drawing on the image
    draw = ImageDraw.Draw(img)

    # draw the rectangle
    draw.rectangle(bbox_to_coords(bbox, img_width, img_height),
                   outline=(0, 200, 0))

    # clean up the ImageDraw object
    del draw

    # return the img, allows draw_box to be chained with .show()
    return img
