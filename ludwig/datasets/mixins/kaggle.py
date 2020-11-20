import os
from kaggle.api.kaggle_api_extended import KaggleApi


class KaggleMixin:
    """A mixin to abstract away the details of the kaggle API which includes
    the ability to authenticate against the kaggle API, list the various datasets
    and finally download the dataset"""

    def __init__(self):
        """We instantiate a handle to the API and authenticate here, the requirements
        for authentication are that Kaggle API requires an API token:
        1) Go to the Account Tab ( https://www.kaggle.com/<username>/account )
        and click ‘Create API Token’.  A file named kaggle.json will be downloaded.
        2) Move this file in to ~/.kaggle/  folder in Mac and Linux or to C:\Users\<username>\.kaggle\ on windows.
        This is required for authentication and do not skip this step."""
        api = KaggleApi()
        api.authenticate()

    def list_downloads(self) -> list:
        """In kaggle they use the term competitions, here we list all
        competition objects associated with the titanic data and return that as a list
        :Return:
            a list of competition objects associated with Titanic"""
        return self.api.competitions_list(search="titanic")

    def download_raw_dataset(self):
        """
        Download the raw dataset and extract the contents of the zip file and
        store that in the cache location.
        """
        os.makedirs(self.raw_temp_path, exist_ok=True)
        # Download all files for a competition
        # Signature: competition_download_files(competition, path=None, force=False, quiet=True)
        self.api.competition_download_files('titanic', path=self.raw_temp_path)
        os.rename(self.raw_temp_path, self.raw_dataset_path)
