import os
from difflib import SequenceMatcher


class Search:
    def __init__(self, base_path, threshold=0.7):
        """
        Initialization search
        :param base_path Basic folder that will be scanned in searching for text files
        :param threshold Similarity of the request with a fragment of the text
        """
        self.base_path = base_path
        self.threshold = threshold

    def similar(self, a, b):
        """
        Checks whether two lines are similar to the threshold of similarity.
        """

        return SequenceMatcher(None, a, b).ratio() >= self.threshold

    @staticmethod
    def read_txt(file_path):
        """
        Reading the contents of a text file.
        """
        content = ""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            pass
        return content.lower()

    def search(self, query, path=None):
        """
        It searches for files and folders that correspond to the request.

        :param query: Request string.
        :param path: Basic folder
        :return: List of ways to found files and folders.
        """

        if path:
            self.base_path = path

        matches = []

        for root, _, files in os.walk(self.base_path):
            # Check the files
            for file in files:
                # We check the similarity with the name of the file
                file_path = os.path.join(root, file)
                if self.similar(file, query):
                    matches.append(file_path)
                    continue

                # Check the contents of the file
                content = ""
                if file.lower().endswith('.txt'):
                    content += self.read_txt(file_path)

                for a in content.split('\n'):
                    if self.similar(a, query):
                        matches.append(file_path)
                        break

        return matches