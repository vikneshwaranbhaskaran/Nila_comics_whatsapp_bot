import requests
import json
import os

token = "EAAO0IoXio38BSHT6z2Hypghb0vZCqgMfVu1JEb3mZAUp1xWjaw0ZApxEANfO7ZBremg0fSFfZAKKBGFZCaPqM0C75p5GyZCl3ZB5kOnmmA8BJNQGCjFv96Jz6CwAMde4szIxOcTOANoN3e5NB0eWc2c9ZBzexIEOYwJEEUnsMVx1FU5ZBLkiKsefZBl9MAG1j7QdIyCXAZDZD"
phone_id = "1158362710703670"
version = "v25.0"

url = f"https://graph.facebook.com/{version}/{phone_id}/media"

headers = {
    "Authorization": f"Bearer {token}"
}

file_path = "app/static/samples/tamil/media__1785344373084.jpg"

files = {
    "file": (os.path.basename(file_path), open(file_path, "rb"), "image/jpeg")
}
data = {
    "messaging_product": "whatsapp"
}

response = requests.post(url, headers=headers, files=files, data=data)
print(response.status_code)
print(response.text)

