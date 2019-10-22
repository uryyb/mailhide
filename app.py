from flask import Flask, render_template, request, jsonify, \
                    redirect, Response, url_for, abort
import helpers

config_dic = helpers.load_config()

# flask app setup
app = Flask(__name__)
app.secret_key = config_dic["app_secret_key"]


@app.route("/", methods=["GET"])
def home():
    return render_template("home.html", public_key=config_dic["captcha_public_key"])

@app.route("/validate", methods=["POST"])
def validate():
	data = None
	client_ip = request.remote_addr
	captcha_response = request.form['g-recaptcha-response']
	if helpers.verify(config_dic["captcha_private_key"], captcha_response, client_ip):
		data = {"status":True,
			"msg":"Here's the email you were looking for",
			"email":config_dic["hidden_address"]}
	else:
		data = {"status":False,
			"msg":"reCAPTCHA test failed."}
	return render_template("validate.html", data=data)

@app.route("/_validate", methods=["POST"])
def ajax_validate():
	data = None
	client_ip = request.remote_addr
	captcha_response = request.form['g-recaptcha-response']
	if helpers.verify(config_dic["captcha_private_key"], captcha_response, client_ip):
		data = {"status":True,
			"msg":"Here's the email you were looking for",
			"email":config_dic["hidden_address"]}
	else:
		data = {"status":False,
			"msg":"reCAPTCHA test failed."}
	return jsonify(data)

if __name__ == "__main__":
	app.run(debug=True)