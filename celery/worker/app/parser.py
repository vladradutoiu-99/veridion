import pandas as pd

from app.restschema import CrawlResponse
from app.utils.logging_module.logger import logger

import numpy as np

headers = ['domain', 'company_commercial_name', 'company_legal_name', 'company_all_available_names']

class Parser:
    def __init__(self, path):
        self.path = path
        self.df = pd.read_csv(self.path)

    def add_data(self, response: CrawlResponse):
        domain = response.URL.split('/')[2]
        company_name = self.df[self.df['domain'] == domain]['company_commercial_name'].values
        # check if company name is available in the dataframe and is not empty or nan or None
        if company_name and not pd.isnull(company_name[0]) and company_name[0] != 'nan' and company_name[0] != 'None':
            response.company_commercial_name = company_name[0]
        company_commercial_name = self.df[self.df['domain'] == domain]['company_commercial_name'].values
        if company_commercial_name and not pd.isnull(company_commercial_name[0]) and company_commercial_name[0] != 'nan' and company_commercial_name[0] != 'None':
            response.company_commercial_name = company_commercial_name[0]
        company_legal_name = self.df[self.df['domain'] == domain]['company_legal_name'].values
        if company_legal_name and not pd.isnull(company_legal_name[0]) and company_legal_name[0] != 'nan' and company_legal_name[0] != 'None':
            response.company_legal_name = company_legal_name[0]

        return response

