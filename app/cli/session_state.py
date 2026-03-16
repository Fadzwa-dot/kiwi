def get_logged_in_user():
    return "admin"

_logged_in_user = None

def get_logged_in_user():
    global _logged_in_user
    return _logged_in_user

def set_logged_in_user(user):
    global _logged_in_user
    _logged_in_user = user

def clear_logged_in_user():
    global _logged_in_user
    _logged_in_user = None
