"""
This is a module in which I keep some code
that could be not preserved in next versions.
"""
from yta_image.parser import ImageParser
from PIL import Image
from typing import Union


# TODO: Remove this method in a few commits if still
# not used
def image_has_transparency(image: Union[Image.Image, str]):
    """
    Checks if the provided image (read with pillow) has transparency.
    This method returns True if yes or False if not.
    """
    image = ImageParser.to_pillow(image)

    if image.info.get("transparency", None) is not None:
        return True
    if image.mode == "P":
        transparent = image.info.get("transparency", -1)
        for _, index in image.getcolors():
            if index == transparent:
                return True
    elif image.mode == "RGBA":
        extrema = image.getextrema()
        if extrema[3][0] < 255:
            return True

    return False