import requests
import json


#function is used to calculate the closest person's location from a given 
#user's location using the Google Maps Distance Matrix API.
def find_closest_person(user_lat, user_lng, people_list):
    api_key = "<API KEY HERE>"
    closest_person = None
    closest_distance = float('inf')
    
    # Format the origins and destinations for the API request
    origins = f"{user_lat},{user_lng}"
    destinations = "|".join([f"{person[0]},{person[1]}" for person in people_list])
    
    # Create the URL for the API request
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={origins}&destinations={destinations}&key={api_key}"
    
    # Send the API request and parse the response
    response = requests.get(url)
    data = json.loads(response.text)
    
    if data['status'] != 'OK':
        # Print the error message if the API request fails
        print(f"Error: {data['status']}")
        return None
    
    for i, row in enumerate(data['rows'][0]['elements']):
        if row['status'] != 'OK':
            # Print the error message if the distance calculation fails for a person
            print(f"Error: {row['status']} for person {i}")
            continue
        
        distance = row['distance']['value']
        if distance < closest_distance:
            # Update the closest person if a closer person is found
            closest_distance = distance
            closest_person = people_list[i]
    
    return closest_person


