from yta_image.parser import ImageParser
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from typing import Union
from abc import ABC, abstractmethod

import numpy as np
import ollama


class ImageDescriptor(ABC):
    """
    Class to describe images.
    """

    @abstractmethod
    def describe(
        image: Union[str, Image.Image, np.ndarray]
    ) -> str:
        """
        Describe the provided 'image' using an engine
        capable of it.
        """
        pass

class BlipImageDescriptor(ImageDescriptor):
    """
    Class to describe an image using the Blip engine, which
    is from Salesforce and will use pretrained models that are
    stored locally in 'C:/Users/USER/.cache/huggingface/hub',
    loaded in memory and used to describe it.

    The process could take from seconds to a couple of minutes
    according to the system specifications.
    """

    def describe(
        image: Union[str, Image.Image, np.ndarray]
    ) -> str:
        image = ImageParser.to_pillow(image)

        # models are stored in C:\Users\USERNAME\.cache\huggingface\hub
        processor = BlipProcessor.from_pretrained('Salesforce/blip-image-captioning-base')
        model = BlipForConditionalGeneration.from_pretrained('Salesforce/blip-image-captioning-base')
        inputs = processor(image, return_tensors = 'pt')
        out = model.generate(**inputs)
        description = processor.decode(out[0], skip_special_tokes = True)

        # TODO: Fix strange characters. I received 'a red arrow pointing up
        # to the right [SEP]' response from describing an image. What is the
        # '[SEP]' part? What does it mean? I don't want that in response.
        return description
    
class LlavaImageDescriptor(ImageDescriptor):
    """
    Class to describe an image using the Llava engine
    through the 'ollama' python package.
    """

    def describe(image_filename: str):
        """
        THIS METHOD IS NOT WORKING YET.

        TODO: This is not working because of my pc limitations.
        It cannot load the resources due to memory capacity.
        """
        res = ollama.chat(
            model = 'llava',
            messages = [
                {
                    'role': 'user',
                    'content': 'Describe this image',
                    'images': [
                        image_filename
                    ]
                }
            ]
        )

        response_content = res['message']['content']

        return response_content