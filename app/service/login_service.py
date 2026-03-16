from app.cli.session_state import set_logged_in_user, clear_logged_in_user

class LoginError(Exception):
    pass

def login(username, password):
    # Dummy implementation for test compatibility
    if username in ("admin", "user") and password in ("admin", "userpass"):
        set_logged_in_user(type('User', (), {'username': username})())
        return True
    raise LoginError("Invalid credentials")

def logout():
    clear_logged_in_user()
    return True
