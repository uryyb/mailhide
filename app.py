from flask import Flask, render_template, request, jsonify, \
                    redirect, Response, url_for, abort
import requests

# flask app setup
app = Flask(__name__)
app.secret_key = "update_me"

hidden_address = "email@example.com"
captcha_secret_key = "SECRET"
recaptcha_url = "https://www.recaptcha.net/recaptcha/api/siteverify"

def verify(response, client_ip):
	payload = {"secret":captcha_secret_key,
		"response":response,
		"remoteip":client_ip}
	r = requests.get(recaptcha_url, params=payload)
	r_data = r.json()
	return r_data["success"]

@app.route("/", methods=["GET"])
def home():
    return render_template("home.html")

@app.route("/validate", methods=["POST"])
def validate():
	data = None
	client_ip = request.remote_addr
	captcha_response = request.form['g-recaptcha-response']
	if verify(captcha_response, client_ip):
		data = {"status":True,
			"msg":"Here's the email you were looking for",
			"email":hidden_address}
	else:
		data = {"status":False,
			"msg":"reCAPTCHA test failed."}
	return render_template("validate.html", data=data)

if __name__ == "__main__":
	app.run(debug=True)