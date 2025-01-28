import logging
from abc import abstractmethod

import requests
from django.core.cache import cache
from requests_oauthlib import OAuth2Session
from requests.exceptions import RequestException
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_401_UNAUTHORIZED

from .oauth2_client_factory import OAuth2ClientFactory
from ..utils import config


class AbstractOAuth2APIClient:
    MAX_RETRIES = 3
    SKEW_TIME = 120
    ACCESS_TOKEN_CACHE_KEY_TEMPLATE = "{}_OAUTH2_ACCESS_TOKEN"

    @abstractmethod
    def get_app_name(self) -> str:
        pass

    def get_idp_config(self) -> dict:
        return {
            "authorization_endpoint": f'{config('OAUTH2.IDP.BASE_URL')}/{config('OAUTH2.IDP.AUTHORIZATION_ENDPOINT')}',
            "token_endpoint": f'{config('OAUTH2.IDP.BASE_URL')}/{config("OAUTH2.IDP.TOKEN_ENDPOINT")}',
        }

    @abstractmethod
    def get_app_config(self) -> dict:
        pass

    def get_idp_client(self) -> OAuth2Session:
        return OAuth2ClientFactory.build(
            self.get_idp_config(),
            self.get_app_config()
        )

    def get_access_token_cache_key(self) -> str:
        return self.ACCESS_TOKEN_CACHE_KEY_TEMPLATE.format(self.get_app_name())

    def invoke_with_retry(self, callback):
        retries = 0
        while retries < self.MAX_RETRIES:
            try:
                return callback(self)
            except RequestException as ex:
                logging.warning("Retrying due to RequestException...")
                retries += 1
                if retries >= self.MAX_RETRIES:
                    if ex.response and ex.response.status_code == HTTP_404_NOT_FOUND:
                        return None
                    raise
                self.clean_access_token()
                logging.warning(f"Retry attempt {retries}: {ex}")
            except Exception as ex:
                self.clean_access_token()
                logging.error(f"Unhandled exception: {ex}")
                raise

    def get_access_token(self, raw_request: bool = False) -> str:
        logging.debug("AbstractOAuth2Api::get_access_token")
        cache_key = self.get_access_token_cache_key()
        token = cache.get(cache_key)

        if not token:
            try:
                logging.debug("AbstractOAuth2Api::get_access_token - Access token not found in cache, requesting new token...")
                app_config = self.get_app_config()

                if raw_request:
                    data = {
                        'grant_type': 'client_credentials',
                        'client_id': app_config.get('client_id', ''),
                        'client_secret': app_config.get('client_secret', ''),
                        'scope': app_config.get('scopes', '').split()
                    }

                    response = requests.post(
                        f'{config('OAUTH2.IDP.BASE_URL')}/{config('OAUTH2.IDP.TOKEN_ENDPOINT')}',
                        data=data)

                    if response.status_code == 200:
                        token_response = response.json()
                    else:
                        raise RequestException(response=response)
                else:
                    client = self.get_idp_client()
                    token_response = client.fetch_token(
                        token_url=f'{config('OAUTH2.IDP.BASE_URL')}/{config('OAUTH2.IDP.TOKEN_ENDPOINT')}',
                        client_secret=app_config.get('client_secret', '')
                    )

                token = token_response["access_token"]
                expires_in = token_response.get("expires_in", 3600)
                ttl = max(0, expires_in - self.SKEW_TIME)

                if ttl > 0:
                    cache.set(cache_key, token, ttl)

                logging.debug(f"AbstractOAuth2Api::get_access_token - New access token obtained: {token}, expires in {ttl} seconds.")
            except RequestException as ex:
                logging.warning(f"RequestException: {ex}")
                if ex.response and ex.response.status_code == HTTP_401_UNAUTHORIZED:
                    cache.delete(cache_key)
                raise

        logging.debug(f"AbstractOAuth2Api::Returning cached access token: {token}")
        return token

    def clean_access_token(self):
        cache_key = self.get_access_token_cache_key()
        cache.delete(cache_key)

