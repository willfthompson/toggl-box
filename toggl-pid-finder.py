import requests
response = requests.get((f'https://api.track.toggl.com/api/v8/workspaces/2148194/projects'), auth=('9ff7813fb8fc6b53cb2a7101875e85e8', 'api_token'))

print(response.json())
