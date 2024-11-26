class JWTTokenInvalid(Exception):
    def __init__(self):
        self.detail = "JWT Token invalid"


class JWTTokenExpired(Exception):
    def __init__(self):
        self.detail = "JWT Token expired"
