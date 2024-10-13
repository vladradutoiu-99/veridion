import pandas as pd

header = ['domain']

class Parser:
    def __init__(self, path):
        self.path = path

    def parse(self):
        return pd.read_csv(self.path)

