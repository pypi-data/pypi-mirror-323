import uuid

import requests
from flask import (current_app, flash, get_flashed_messages, 
                   redirect, render_template, request, session, url_for, g)
from flask import Blueprint
from flask_login import (current_user, login_user, logout_user, LoginManager)
from jtlutil.flask.flaskapp import insert_query_arg
from jtlutil.jwtencode import decrypt_token, encrypt_token

from .flaskapp import User

auth_bp = Blueprint("auth", __name__)

login_manager = LoginManager()
login_manager.init_app(auth_bp)
login_manager.login_view = 'auth.login'
login_manager = auth_bp.login_manager = login_manager


@auth_bp.login_manager.user_loader
def load_user(user_id):
    current_app.logger.info(f"Request to load  user with ID: {user_id}")

    if "user" in session:
        current_app.logger.info(f"User data  already in session")
        user_data = session["user"]
        return User(user_data)

    return None





def get_session_user(app,session_id):
    
    enc_key = bytes.fromhex(current_app.app_config['ENCRYPTION_KEY'])
    
    t = encrypt_token(session_id, enc_key)
    
    auth_server_url = current_app.app_config["AUTH_SERVER_URL"]
    user_endpoint = f"{auth_server_url}/user"
    params = {"ssoid": t}
    
    response = requests.get(user_endpoint, params=params)
    
    if response.status_code == 200:
        user_data = response.json()
        
        return user_data
    else:
        current_app.logger.error(f"Failed to fetch user data: {response.status_code} {response.text}")
        return None

def load_user(app):
    """When the authentication server redirects back to the app here, it will include a query
    parameter `ssoid` which is the encrypted session ID. This function decrypts
    the session ID and loads the user data into the session. We can look up this
    session id in the cache and load the user data into the session.
    """

    query_args = request.args.to_dict()
    ssoid = query_args.get("ssoid")
    
    if ssoid:
        # Decrypt it
        session_id = decrypt_token(
            ssoid, bytes.fromhex(app.app_config["ENCRYPTION_KEY"])
        )
        user_data = get_session_user(app, session_id)
        session["user"] = user_data
        
        user = User(user_data)

        login_user(user)
        


@auth_bp.route("/login")
def login():

    login_url = insert_query_arg(
        current_app.app_config["AUTH_SERVER_URL"]+"/login",
        "redirect",
        url_for("index", _external=True),
    )
    current_app.logger.info(f"Redirecting to login server at {login_url}")

    get_flashed_messages()

    return redirect(login_url)


@auth_bp.route("/logout")
def logout():

    current_app.logger.info(f"User {current_user.id} logging out")

    #uncache_user(session["session_id"])
    session.clear()
    logout_user()
    current_app.logger.info(f"ser logged out")

    flash("You have been logged out.", "info")
    return redirect(url_for("index"))

