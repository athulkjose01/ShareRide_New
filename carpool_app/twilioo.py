import requests

url = "https://getitsms-whatsapp-apis.p.rapidapi.com/45"

querystring = {"your_number":"918078538160","your_message":"your message"}

payload = {
	"your_number": "917736435815",
	"your_message": "your message"
}
headers = {
	"x-rapidapi-key": "9c183280d1msh433b588b81e5e16p14e539jsn5efc866e1070",
	"x-rapidapi-host": "getitsms-whatsapp-apis.p.rapidapi.com",
	"Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers, params=querystring)

print(response.json())