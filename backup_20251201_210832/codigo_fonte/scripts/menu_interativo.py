import requests

url = "https://gate.whapi.cloud/messages/interactive"

payload = {
    "header": { "text": "Este é o cabeçalho" },
    "body": { "text": "Este é o corpo" },
    "footer": { "text": "este é o rodape" },
    "action": { "buttons": [
            {
                "type": "url",
                "title": "Sim ",
                "id": "id1",
                "url": "google.com"
            },
            {
                "type": "url",
                "title": "Nao ",
                "id": "id2",
                "url": "cair fora"
            }
        ] },
    "type": "button",
    "to": "5518997366866"
}
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": "Bearer zH945tTAfUZ26vKhYH0VHYMf3BSoPHIu"
}

response = requests.post(url, json=payload, headers=headers)

print(response.text)