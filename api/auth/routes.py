from flask import request, Blueprint
import auth.controllers as Controllers

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST'])
def register():
    return Controllers.register()

@auth.route('/login', methods=['POST'])
def login():
    return Controllers.login()

@auth.route('/refresh', methods=['POST'])
def refresh():
    return Controllers.refresh()

@auth.route('/change-email', methods=['PATCH'])
def change_email():
    return Controllers.change_email()

@auth.route('/change-password', methods=['PATCH'])
def change_password():
    return Controllers.change_password()

@auth.route('/logout', methods=['POST'])
def logout():
    return Controllers.logout()

@auth.route('/delete-account', methods=['DELETE'])
def delete_account():
    return Controllers.delete_account()