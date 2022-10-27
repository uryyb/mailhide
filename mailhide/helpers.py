import requests
import yaml
import hashlib

def load_config(filname="config.yaml"):
	stream = open(filname, 'r')
	return yaml.load(stream, Loader=yaml.FullLoader)

def hash_email(addr):
	# need to enable handling collisions
	return hashlib.sha1(addr.encode()).hexdigest()

def obfuscate_email(email_addr):
	# should move this to it's own function
    elst = email_addr.split("@")
    if len(elst[0]) > 2:
        return elst[0][0] + "...@" + elst[1]
    else:
        return "...@" + elst[1]

def verify(private_key, response, client_ip):
	recaptcha_url = "https://www.recaptcha.net/recaptcha/api/siteverify"
	payload = {"secret":private_key,
		"response":response,
		"remoteip":client_ip}
	r = requests.get(recaptcha_url, params=payload)
	r_data = r.json()
	return r_data["success"]
