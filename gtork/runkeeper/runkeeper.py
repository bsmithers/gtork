import requests


class RunkeeperException(Exception):
    pass


class Runkeeper(object):
    api_url = 'http://api.runkeeper.com'

    def __init__(self, access_token):
        self.access_token = access_token

    def get_name(self):
        r = self._get('profile', 'application/vnd.com.runkeeper.Profile+json')
        j = r.json()
        return j['name']

    def upload_activity(self, json_data):
        self._post_json('fitnessActivities', 'application/vnd.com.runkeeper.NewFitnessActivity+json', json_data)

    def _get(self, endpoint, accept):
        headers = {}
        headers['Authorization'] = 'Bearer ' + self.access_token
        headers['Accept'] = accept
        url = Runkeeper.api_url + '/' + endpoint
        return Runkeeper._do_request(requests.get, url, headers=headers)

    def _post_json(self, endpoint, content_type, content):
        headers = {}
        headers['Authorization'] = 'Bearer ' + self.access_token
        headers['Content-type'] = content_type
        url = Runkeeper.api_url + '/' + endpoint
        Runkeeper._do_request(requests.post, url, headers=headers, json=content)
        return True

    @staticmethod
    def complete_authorisation(code, redirect_uri, client_id, client_secret):
        client_id = client_id
        client_secret = client_secret

        post_data = {}
        post_data["grant_type"] = "authorization_code"
        post_data["code"] = code
        post_data["client_id"] = client_id
        post_data["client_secret"] = client_secret
        post_data["redirect_uri"] = redirect_uri

        r = Runkeeper._do_request(requests.post, "https://runkeeper.com/apps/token", data=post_data)
        response = r.json()
        return response["access_token"]

    @staticmethod
    def _do_request(fn, *args, **kwargs):
        try:
            r = fn(*args, **kwargs)
            r.raise_for_status()
            return r
        except requests.RequestException as e:
            raise RunkeeperException("Couldn't communicate with Runkeeper. Received exception {}".format(e))