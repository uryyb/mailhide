from flask import escape, render_template, request, flash, \
                    redirect, Response, url_for, abort, jsonify
from flask_login import UserMixin, current_user, \
                            login_required, login_user, logout_user
from urllib.parse import urlparse, urljoin
from mailhide import app, config_dic, db, login_manager, logger
from mailhide.forms import LoginForm, RegistForm, HideMailForm
from mailhide import helpers, models
import bcrypt

# the user model (flask login)
class User(UserMixin):

    def __init__(self, id):
        user_data = models.DBUser.query.filter_by(id=id).first()
        self.id = id
        self.name = user_data.username
        self.email = user_data.email
        
    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.email)


# snippet to check if the url is safe
# http://flask.pocoo.org/snippets/62/
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and \
           ref_url.netloc == test_url.netloc
           

@app.route("/", methods=["GET"])
def home():
    if config_dic['debug']:
        host_domain = config_dic['external_host'] + ':' + str(config_dic['external_port'])
    else:
        host_domain = config_dic['external_host']
    form = HideMailForm(request.form)
    return render_template("home.html", form=form, host_domain=host_domain)

@app.route("/_hide_address", methods=["POST"])
def ajax_hide_address():
    form = HideMailForm(request.form)
    if request.method == "POST" and form.validate():
        hv = helpers.hash_email(form.address.data)
        email_addr = form.address.data
        try:
            # should move this to it's own function
            elst = email_addr.split("@")
            if len(elst[0]) > 2:
                de = elst[0][0] + "...@" + elst[1]
            else:
                de = "...@" + elst[1]

            hidden_address = models.Emails.query.filter_by(email_hash=hv).first()
            if hidden_address is not None:
                return jsonify({'msg':'congrats', 
                        'hash':hidden_address.email_hash, 'addr':de })
            addr = models.Emails(db_user_id=current_user.id, email=email_addr, email_hash=hv)
            db.session.add(addr)
            db.session.commit()
            
            return jsonify({'msg':'congrats', 'hash':hv, 'addr':de })
        except:
            return jsonify({'msg':'uh oh! something went wrong.'})
    return jsonify({'msg':'uh oh! something went wrong.'})


@app.route("/h/<hashkey>", methods=["GET"])
def hidden(hashkey):
    return render_template("hidden.html", 
                public_key=config_dic["captcha_public_key"],
                hashkey=hashkey)


# an example protected url
@app.route("/account")
@login_required
def account():
    hidden_addresses = models.Emails.query.filter_by(db_user_id=current_user.id).all()
    return render_template("account.html", hidden_addresses=hidden_addresses)


# register here
@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if current_user.is_anonymous:
        form = RegistForm(request.form)
        if request.method == "POST" and form.validate():
            try:
                user = models.DBUser(username=form.username.data, 
                    email=form.email.data, 
                    password=bcrypt.hashpw(form.password.data.encode("utf-8"), bcrypt.gensalt()))
                db.session.add(user)
                db.session.commit()
                return redirect(url_for("login"))
            except:
                # need to improve this error handling
                error = "Username or email already in use."
        return render_template("register.html", form=form, error=error)
    else:
        return redirect(url_for("home"))

# login here
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if current_user.is_anonymous:
        form = LoginForm(request.form)
        if request.method == "POST" and form.validate():
            username = form.username.data
            password = form.password.data.encode("utf-8")
            user_data = models.DBUser.query.filter_by(username=username).first()
            if user_data and bcrypt.checkpw(password, user_data.password):
                user = User(user_data.id)
                login_user(user)
                flash("You were successfully logged in")
                next = request.args.get("next")
                if not is_safe_url(next):
                    return abort(400)

                return redirect(next or url_for("home"))
            else:
                error = "Login failed"
        return render_template("login.html", form=form, error=error)
    else:
        return "Already logged in."


# log the user out
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


# handle failed login
@app.errorhandler(401)
def page_not_found(e):
    return "Login failed"


# callback to reload the user object        
@login_manager.user_loader
def load_user(userid):
    return User(userid)

# validate recaptcha response
@app.route("/validate", methods=["POST"])
def validate():
    data = None
    client_ip = request.remote_addr
    captcha_response = request.form['g-recaptcha-response']
    hashkey = request.form['hashkey']
    if helpers.verify(config_dic["captcha_private_key"], captcha_response, client_ip):
        #hide just a single address for now
        if "hidden_address" in config_dic:
            hidden_address = config_dic["hidden_address"]
        else:
            hidden_address = models.Emails.query.filter_by(email_hash=hashkey).first().email
        data = {"status":True,
            "msg":"Here's the email you were looking for",
            "email":hidden_address}
    else:
        data = {"status":False,
            "msg":"reCAPTCHA test failed."}
    return render_template("validate.html", data=data)

@app.route("/_validate", methods=["POST"])
def ajax_validate():
    # need to validate and make sure form data is safe
    data = None
    client_ip = request.remote_addr
    captcha_response = request.form['g-recaptcha-response']
    hashkey = request.form['hashkey']
    if helpers.verify(config_dic["captcha_private_key"], captcha_response, client_ip):
        #hide just a single address for now
        if "hidden_address" in config_dic:
            hidden_address = config_dic["hidden_address"]
        else:
            hidden_address = models.Emails.query.filter_by(email_hash=hashkey).first().email
        data = {"status":True,
            "msg":"Here's the email you were looking for",
            "email":hidden_address}
    else:
        data = {"status":False,
            "msg":"reCAPTCHA test failed."}
    return jsonify(data)
    