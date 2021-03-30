import datetime
import glob
import io
import json
import logging
import os
import pprint
import random
import traceback
import urllib
from copy import deepcopy
from itertools import chain

import numpy as np
import pandas as pd
import requests
from tqdm import tqdm

logger = logging.getLogger(__name__)


class GoDataAPI(object):
    def __init__(self, api_url, outbreak_id, username, password):
        self.outbreak_id = outbreak_id
        self.api_url = api_url
        self.outbreak_url = self.api_url + f"outbreaks/{self.outbreak_id}/"
        self.username = username
        self.password = password

    def login(self):
        r = requests.post(f"{self.api_url}oauth/token", json={
            "username": self.username,
            "password": self.password,
        })
        if 'response' in r.json():
            token = r.json()['response']['access_token']
        else:
            try:
                token = r.json()['access_token']
            except ValueError:
                raise ValueError("Unable to login with given credentials")
        self.token_string = f'?access_token={token}'

    @staticmethod
    def encode_query(query):
        return urllib.parse.quote_plus(json.dumps(query))

    @staticmethod
    def replaceNAs(df):
        return df.fillna(np.nan).replace([np.nan], [None])

    def get_count(self, kind, params={}):
        querystring = self.encode_query(params)

        if kind == "audit-logs":
            base_url = f"{self.api_url}/{kind}"
        else:
            base_url = f"{self.outbreak_url}{kind}"

        resp = requests.get(
            f"{base_url}/count{self.token_string}&where={querystring}"
        )

        return resp.json()['count']

    def get_items(self, kind, offset=0, limit=None, batch=1000, params={}):
        if limit is None:
            if kind == "events":
                limit = 10000
            else:
                limit = self.get_count(kind, params.get("where", {}))
                logger.debug(f"got limit={limit} from API")

        iterations = (limit - offset - 1) // batch + 1
        logger.debug(f"limit={limit},offset={offset},batch={batch},params={params}")

        if kind == "audit-logs":
            base_url = f"{self.api_url}/{kind}{self.token_string}"
        else:
            base_url = f"{self.outbreak_url}{kind}{self.token_string}"

        res = []
        for i in tqdm(range(iterations), miniters=iterations/5):
            query = {
                'limit': batch,
                'offset': batch*i,
                **params
            }
            logger.debug(f"subrequest: {query}")
            query_string = urllib.parse.quote_plus(json.dumps(query))

            r = requests.get(
                f"{base_url}&filter={query_string}"
            )
            res.extend(r.json())
        gd_all_df = pd.DataFrame(res)
        

        return self.replaceNAs(gd_all_df)
