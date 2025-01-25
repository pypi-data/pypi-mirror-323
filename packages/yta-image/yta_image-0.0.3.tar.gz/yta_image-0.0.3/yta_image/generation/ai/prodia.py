from yta_image.parser import ImageParser
from yta_general_utils.temp import create_temp_filename
from yta_general_utils.downloader import Downloader
from yta_general_utils.programming.env import get_current_project_env
from typing import Union

import time
import requests


PRODIA_API_KEY =  get_current_project_env('PRODIA_API_KEY')

def generate_image_with_prodia(
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
        "X-Prodia-Key": PRODIA_API_KEY
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
        image_filename = retrieve_job(job_id, output_filename)
    else:
        print(response)
        raise Exception('There was an error when generating a Prodia AI Image.')
    
    image = ImageParser.to_pillow(image_filename) if image is not None else None

    return image, output_filename

def retrieve_job(
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
            'X-Prodia-Key': PRODIA_API_KEY
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