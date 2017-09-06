import re
import requests


class GarminException(Exception):
    pass


class GarminLoginException(GarminException):
    pass


class Garmin(object):

    login_url = "https://sso.garmin.com/sso/login?service=https%3A%2F%2Fconnect.garmin.com%2Fpost-auth%2Flogin"
    post_login_url = "https://connect.garmin.com/post-auth/login"
    activity_url = "https://connect.garmin.com/modern/proxy/activitylist-service/activities/search/activities?limit=20&start=0"

    def __init__(self):
        self._logged_in = False
        self._session = requests.Session()
        self._session.headers.update({'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36'})

    def login(self, username, password):

        # Initally make a get request to the login service to get a session id
        r = self._session.get(self.login_url)
        self._check_response(r, "fetching the base login URL")

        # Now we post the login details, along with some extra form information identified in manual inspection
        post_data = {
            "username": username,
            "password": password,
            "embed": "true",
            "lt" : "els1",
            "_eventId" : "submit",
            "displayNameRequired": "false"
        }

        r = self._session.post(self.login_url, post_data)
        self._check_response(r, 'posting the login data')

        # Finally, Garmin require us to make a further request with a ticket extracted from this response
        ticket_matches = re.findall(re.escape('?ticket=') + '[^"]*', r.text)
        if len(ticket_matches) != 1 or len(ticket_matches[0]) < len('?ticket='):
            raise GarminLoginException("Could not extract the ticket from the login response")

        url = self.post_login_url + ticket_matches[0]
        r = self._session.get(url)
        self._check_response(r, "confirming the Garmin ticket")

        self._logged_in = True

    def fetch_activities(self):
        if not self._logged_in:
            raise GarminException("Must be logged in to fetch activities")
        r = self._session.get(self.activity_url)
        self._check_response(r, "fetching the activity URL")
        return r.json()

    def download_activity(self):
        pass

    def _check_response(self, r, message):
        if r.status_code != 200:
            raise GarminLoginException(
                "Unsuccessful request when {}. Received response {:d}".format(message, r.status_code))
