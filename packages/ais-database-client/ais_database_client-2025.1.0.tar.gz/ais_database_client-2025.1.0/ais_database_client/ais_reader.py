# Library to read AIS data from Space-Eye postgres server.
# AIS data can be selected within boundingbox and timeframe

import requests

class AisReader():
    """
    Reads AIS data from database and presents information in various ways
    """

    AIS_DATABASE_HOST="https://ais.space-eye.info"
    SET_KEY_URL=f"{AIS_DATABASE_HOST}/api/set_keys/"
    INTERPOLATE_URL=f"{AIS_DATABASE_HOST}/api/interpolate/"
    TOKEN_URL=f"{AIS_DATABASE_HOST}/api/token/"
    REFRESH_TOKEN_URL=f"{AIS_DATABASE_HOST}/api/token/refresh/"
    MMSI_URL=f"{AIS_DATABASE_HOST}/api/mmsi/"
    LATEST_URL=f"{AIS_DATABASE_HOST}/api/latest_dates/"
    POLYGON_URL=f"{AIS_DATABASE_HOST}/api/polygon/"

    # pylint: disable=too-many-arguments
    def __init__(self,
                 user,
                 password,
                 ) -> None:
        """
        Establish database connection
        """
        self.keys = ('mmsi', 'vessel_name', 'vessel_type', 'nav_status',
            'heading', 'dt_pos_utc', 'flag_country', 'destination',
            'latitude', 'longitude')
        
        self.user = user
        self.password = password
        
        self.session = requests.Session()
        self.refresh_token=None
        self._set_token()

    def _get_bearer_token(self):
        """
        Retrieves the bearer token required for API authentication.

        Returns:
            - dict: Success flag and either token or error details.
        """
        if self.refresh_token:
            url=self.REFRESH_TOKEN_URL
            payload={"refresh": self.refresh_token}
        else:
            url=self.TOKEN_URL
        
            payload = {
                "username": self.user,
                "password": self.password,  # Test with incorrect credentials if necessary
            }

        try:
            # Send POST request for token
            response = requests.post(
                url,
                json=payload,
                #headers={"Content-Type": "application/json"},
            )
            if response.status_code == 401:
                if self.refresh_token is not None:
                    self.refresh_token = None
                    self._get_bearer_token()

            response.raise_for_status()
            response = response.json()
            # Return token if successful
            token = response["access"]
            if "refresh" in response.keys():
                self.refresh_token = response["refresh"]
            return {"success": True, "token": token}
        
        except requests.exceptions.RequestException as e:
            # Handle request errors, with fallback if JSON parsing fails
            try:
                error_details = response.json()
            except ValueError:
                error_details = {"message": response.text}

            return {
                "success": False,
                "error": "Token request failed",
                "details": error_details,
            }
        
    def _set_token(self):
        response = self._get_bearer_token()
        if response['success']:
            token = response['token']
            self.session.headers.update({"Authorization": f"Bearer {token}"})
        else:
            raise Exception(response['error'],response['details'])
        
    def get_mmsi(self, mmsis : list, from_time:str, to_time:str):
        payload = {"mmsis": mmsis,
                   'from_time':from_time,
                   'to_time':to_time}
        response = self.session.post(self.MMSI_URL, json=payload)
        print(response.text)
        if response.status_code == 401:
            self._set_token()
            response = self.session.post(self.MMSI_URL, json=payload)
        response.raise_for_status()
        return response.json()

    def get_latest_dates(self):
        """
        Returns the date and time of the last update from UNGP.
        """
        payload = {}
        response = self.session.post(self.LATEST_URL, json=payload)
        if response.status_code == 401:
            self._set_token()
            response = self.session.post(self.LATEST_URL, json=payload)
        response.raise_for_status()
        return response.json()

    def get_interpolated(self,time,polygon,space_buffer=12000,time_buffer=30):
        payload={
            "polygon":polygon,
            "target_time":time,
            "space_buffer":space_buffer,
            "time_buffer":time_buffer
        }
        response = self.session.post(self.INTERPOLATE_URL, json=payload)
        if response.status_code == 401:
            self._set_token()
            response = self.session.post(self.INTERPOLATE_URL, json=payload)
        response.raise_for_status()
        return response.json()


    def get_polygon(self):
        pass

    def set_keys(self, keys:list) -> dict:
        """
        Minimum keys that are always returned:
        [
            "mmsi",
            "vessel_name",
            "longitude",
            "latitude",
            "dt_pos_utc",
        ]
        """

        payload={
            "keys":keys
        }
        response = self.session.post(self.SET_KEY_URL, json=payload)
        if response.status_code == 401:
            self._set_token()
            response = self.session.post(self.SET_KEY_URL, json=payload)
        print(response.text)
        response.raise_for_status()
        return response.json()
