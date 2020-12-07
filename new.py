import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session, url_for
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("id") is None:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
