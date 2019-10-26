import requests
import yaml

def load_config(filname="config.yaml"):
	stream = open(filname, 'r')
	return yaml.load(stream, Loader=yaml.FullLoader)

def verify(private_key, response, client_ip):
	recaptcha_url = "https://www.recaptcha.net/recaptcha/api/siteverify"
	payload = {"secret":private_key,
		"response":response,
		"remoteip":client_ip}
	r = requests.get(recaptcha_url, params=payload)
	r_data = r.json()
	return r_data["success"]