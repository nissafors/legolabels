import requests
import os
import shutil
import json
from PIL import Image
import numpy as np

class Part:
    """Get info about parts from Rebrickable.
    
    Attributes:
        cache_dir (str): Path to cache storage.

    Args:
        api_key (str): Your rebrickable API key.
        api_url (str): Base URL of the rebrickable API.
    """

    cache_dir = '.legolabels/cache'

    def __init__(self, api_key, api_url='https://rebrickable.com/api/v3'):
        self._api_key = api_key
        self._api_url = api_url

    def get_img(self, part):
        """Get path to img file.

        Args:
            part (int|str): The part number.
        Returns:
            str: Path to image file or empty string on error.
        """
        if self._download_part(part):
            dirname = self._part_dir_name(part)
            files = os.listdir(self._part_dir_name(part))
            for file in files:
                if file.startswith('img.'):
                    return os.path.join(dirname, file)
        return ''

    def _download_part(self, part):
        """Download part data and save to [cache_dir]/[part_nr]/info.json and  [cache_dir]/[part_nr]/img.[img_ext]."""
        part_cache_dir = self._part_dir_name(part)
        # Is it already in cache?
        if os.path.exists(part_cache_dir):
            return True
        # Download part info via rebrickable API
        url = self._append_slash(self._api_url) + self._append_slash('lego/parts') + self._append_slash(str(part))
        headers = {'Accept': 'application/json', 'Authorization': 'key ' + self._api_key}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return False
        json_dict = response.json()
        # Download image of part
        response = requests.get(json_dict['part_img_url'])
        if response.status_code != 200:
            return False
        # Save to cache
        try:
            os.makedirs(part_cache_dir)
        except FileExistsError:
            pass
        try:
            with open(os.path.join(part_cache_dir, 'info.json'), 'w') as f:
                f.write(json.dumps(json_dict))
            img_filename = 'img' + os.path.splitext(json_dict['part_img_url'])[1]
            with open(os.path.join(part_cache_dir, img_filename), 'wb') as f:
                f.write(response.content)
        except Exception:
            shutil.rmtree(part_cache_dir, ignore_errors=True)
            return False
        return True

    def _part_dir_name(self, part):
        """Construct path name for part."""
        return os.path.normpath(os.path.join(self.cache_dir, part))

    def _append_slash(self, string):
        """Append a slash to a string if it doesn't already end with one."""
        endl = '' if string[-1] == '/' else '/'
        return string + endl


class PartImage:
    """Tools to handle images of parts from Rebrickable.
    
    Attributs:
        img (PIL.Image.Image): RGB image represenation.
    """

    def __init__(self, img_path):
        """Create a new PartImage from path.
        
        Args:
            img_path: Path to image file.
        """
        self.img = Image.open(img_path).convert('RGB')

    def crop(self):
        """Remove same-colored border around part."""
        np_img = np.array(self.img)
        bg_color = np_img[0,0,0:]
        while np.all(bg_color == np_img[0,0:,0:]):
            np_img = np_img[1:,0:,0:]
        while np.all(bg_color == np_img[-1,0:,0:]):
            np_img = np_img[:-1,0:,0:]
        while np.all(bg_color == np_img[0:,0,0:]):
            np_img = np_img[0:,1:,0:]
        while np.all(bg_color == np_img[0:,-1,0:]):
            np_img = np_img[0:,:-1,0:]
        self.img = Image.fromarray(np_img)
