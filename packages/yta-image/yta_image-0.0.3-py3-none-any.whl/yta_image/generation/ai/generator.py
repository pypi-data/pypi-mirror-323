"""
AI Image generation file that contains the classes
capable to generate AI images. These classes will
raise Exceptions if the parameters are not provided
and will use internal functionality to do it.

Programmer help: The classes implement parameter
validation and raise exceptions, but the other files
from which other methods are imported do not 
implement them, so make sure you pass the right
and expected parameters. This should be the ideal
structure to keep in code, but you know... I write
code very fast so I can't go back and review and
refactor code often... So sorry about that :P
"""
from yta_image.generation.ai.prodia import generate_image_with_prodia
from yta_image.generation.ai.pollinations import generate_image_with_pollinations
from yta_general_utils.programming.parameter_validator import PythonValidator
from abc import ABC, abstractmethod
from typing import Union


class AIImageGenerator(ABC):
    """
    Abstract class to be inherited by any specific
    AI image generator.
    """

    @abstractmethod
    def generate_image(
        self,
        prompt: str,
        output_filename: Union[str, None] = None
    ):
        """
        Generate an image with the given 'prompt' and
        store it locally if 'output_filename' is 
        provided.
        """
        pass

class ProdiaAIImageGenerator(AIImageGenerator):
    """
    Prodia AI image generator.
    """

    def generate_image(
        self,
        prompt: str,
        output_filename: Union[str, None] = None
    ):
        """
        Generate an AI image and return 2 values, the
        image read with pillow and the final output
        filename used to store the image locally.
        """
        # TODO: Validate params and raise exception
        image, output_filename = generate_image_with_prodia(prompt, output_filename)

        return image, output_filename
    
class PollinationsAIImageGenerator(AIImageGenerator):
    """
    Pollinations AI image generator.

    This is using the Pollinations platform wich
    contains an AI image generator API and 
    open-source model.

    Source: https://pollinations.ai/
    """

    def generate_image(
        self,
        prompt: str,
        output_filename: Union[str, None] = None
    ):
        """
        Generate an image with the Pollinations AI image generation model
        using the provided 'prompt' and stores it locally as 
        'output_filename'.
        """
        # TODO: Validate params and raise exception
        if not PythonValidator.is_string(prompt):
            raise Exception('Provided "prompt" parameter is not a valid prompt.')
        
        image, output_filename = generate_image_with_pollinations(prompt, output_filename)

        return image, output_filename

    