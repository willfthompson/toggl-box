import requests

AUTHCODE = "Your Auth Code"

response = requests.get((f'https://api.track.toggl.com/api/v8/workspaces/2148194/projects'), auth=(f'{AUTHCODE}', 'api_token'))

for e in response.json():
    print(f"{e['name']}  id={e['id']}")
