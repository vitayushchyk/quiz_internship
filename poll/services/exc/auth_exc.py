class JWTTokenInvalid(Exception):
    def __init__(self):
        self.detail = "JWT Token invalid"


class JWTTokenExpired(Exception):
    def __init__(self):
        self.detail = "JWT Token expired"


class Unauthenticated(Exception):
    def __init__(self):
        self.detail = "Requires authentication"


class Unauthorized(Exception):
    def __init__(self):
        self.detail = "Requires unauthorized"
