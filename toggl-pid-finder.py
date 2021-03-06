import requests
response = requests.get((f'https://api.track.toggl.com/api/v8/workspaces/2148194/projects'), auth=('Your auth code', 'api_token'))

print(response.json())
