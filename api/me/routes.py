from flask import request, Blueprint
import me.controllers as Controllers

me = Blueprint('me', __name__)

@me.route('/')
def get_me():
    return Controllers.get_me()

@me.route('/profile', methods=['PATCH'])
def edit_profile():
    return Controllers.edit_profile()

@me.route('/preferences', methods=['PATCH'])
def edit_preferences():
    return Controllers.edit_preferences()

@me.route('/results')
def get_results():
    return Controllers.get_results()