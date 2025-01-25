from yta_image.parser import ImageParser
from yta_general_utils.temp import create_temp_filename
from yta_general_utils.downloader import Downloader
from yta_general_utils.url import encode_url_parameter
from typing import Union


def generate_image_with_pollinations(
    prompt: str,
    output_filename: Union[str, None] = None
):
    # TODO: Improve 'output_filename' handling
    if output_filename is None:
        output_filename = create_temp_filename('ai_pollinations.png')
    
    prompt = encode_url_parameter(prompt)

    # TODO: Make some of these customizable
    WIDTH = 1920
    HEIGHT = 1080
    # TODO: This seed should be a random value or
    # I will receive the same image with the same
    # prompt
    SEED = 43
    MODEL = 'flux'

    url = f'https://pollinations.ai/p/{prompt}?width={WIDTH}&height={HEIGHT}&seed={SEED}&model={MODEL}'

    image_filename = Downloader.download_image(url, output_filename)
    
    image = ImageParser.to_pillow(image_filename) if image is not None else None

    return image, output_filename

"""
    Check because there is also a model available for
    download and to work with it (as they say here
    https://pollinations.ai/):

    # Using the pollinations pypi package
    ## pip install pollinations

    import pollinations as ai

    model_obj = ai.Model()

    image = model_obj.generate(
        prompt=f'Awesome and hyperrealistic photography of a vietnamese woman... {ai.realistic}',
        model=ai.flux,
        width=1038,
        height=845,
        seed=43
    )
    image.save('image-output.jpg')

    print(image.url)
    """