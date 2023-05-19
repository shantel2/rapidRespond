import requests

def get_location_by_address(address):
    """
    This function returns the latitude and longitude of a given address using the Google Maps API
    :param address: Address in string format
    :return: latitude and longitude 
    """
    api_key = "<API Key Here>"
    url = 'https://maps.googleapis.com/maps/api/geocode/json?address={}&key={}'.format(address, api_key)
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'OK':
            result = data['results'][0]
            location = result['geometry']['location']
            return location['lat'], location['lng']
    return "None"