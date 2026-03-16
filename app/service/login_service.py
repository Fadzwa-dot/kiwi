class LoginError(Exception):
    pass

def login(username, password):
    # Dummy implementation for test compatibility
    if username == "admin" and password == "admin":
        return True
    raise LoginError("Invalid credentials")

def logout():
    return True
