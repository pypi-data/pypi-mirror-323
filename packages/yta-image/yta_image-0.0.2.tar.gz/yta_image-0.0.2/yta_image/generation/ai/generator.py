from yta_image.parser import ImageParser
from yta_general_utils.programming.env import get_current_project_env
from yta_general_utils.temp import create_temp_filename
from yta_general_utils.downloader import Downloader
from yta_general_utils.url import encode_url_parameter
from yta_general_utils.programming.parameter_validator import PythonValidator
from abc import ABC, abstractmethod
from typing import Union

import time
import requests


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

    _PRODIA_API_KEY =  get_current_project_env('PRODIA_API_KEY')

    def generate_image(
        self,
        prompt: str,
        output_filename: Union[str, None] = None
    ):
        # TODO: Raise exception
        if not prompt:
            return None
        
        # If you comment this and uncomment the one below it works
        # seed = randint(1000000000, 9999999999)
        # response = requests.get('https://api.prodia.com/generate?new=true&prompt=' + prompt + '&model=absolutereality_v181.safetensors+%5B3d9d4d2b%5D&steps=20&cfg=7&seed=' + str(seed) + '&sampler=DPM%2B%2B+2M+Karras&aspect_ratio=square')
        payload = {
            'new': True,
            'prompt': prompt,
            #'model': 'absolutereality_v181.safetensors [3d9d4d2b]',   # this model works on above request, not here
            'model': 'sd_xl_base_1.0.safetensors [be9edd61]',
            #'negative_prompt': '',
            'steps': 20,
            'cfg_scale': 7,
            'seed': 2328045384,
            'sampler': 'DPM++ 2M Karras',
            'width': 1344,
            'height': 768
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "X-Prodia-Key": self._PRODIA_API_KEY
        }
        url = 'https://api.prodia.com/v1/sdxl/generate'
        response = requests.post(url, json = payload, headers = headers)
        response = response.json()

        # TODO: Improve 'output_filename' handling
        if output_filename is None:
            output_filename = create_temp_filename('tmp_prodia.png')

        # When requested it is queued, so we ask for it until it is done
        if "status" in response and response['status'] == 'queued':
            job_id = response['job']
            image_filename = self._retrieve_job(job_id, output_filename)
        else:
            print(response)
            raise Exception('There was an error when generating a Prodia AI Image.')
        
        image = ImageParser.to_pillow(image_filename) if image is not None else None

        return image, output_filename

    def _retrieve_job(
        self,
        job_id: str,
        output_filename: Union[str, None] = None
    ):
        """
        Makes a request for the image that is being
        generated with the provided 'job_id'.

        It has a loop to wait until it is done. This
        code is critic because of the loop.
        """
        url = f'https://api.prodia.com/v1/job/{str(job_id)}'

        headers = {
            'accept': 'application/json',
            'X-Prodia-Key': self._PRODIA_API_KEY
        }

        response = requests.get(url, headers = headers)
        response = response.json()
        #print(response)

        # TODO: Do a passive waiting
        is_downloadable = True

        if response['status'] != 'succeeded':
            is_downloadable = False

        # TODO: Implement a tries number
        while not is_downloadable:
            time.sleep(5)
            print('Doing a request in loop')

            # We do the call again
            response = requests.get(url, headers = headers)
            response = response.json()
            print(response)
            if 'imageUrl' in response:
                is_downloadable = True

        image_url = response['imageUrl']

        return Downloader.download_image(image_url, output_filename)
    
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
        if not PythonValidator.is_string(prompt):
            raise Exception('Provided "prompt" parameter is not a valid prompt.')
        
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