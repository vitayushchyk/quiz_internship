class UserNotFound(Exception):
    def __init__(self, user_id: int):
        self.detail = f"User with ID {user_id} not found."


class UserAlreadyExist(Exception):
    def __init__(self, user_email: str):
        self.detail = f"User with {user_email} already exist."


class UserNotAuthenticated(Exception):
    def __init__(
        self,
    ):
        self.detail = "Incorrect email or password"


class UserForbidden(Exception):
    def __init__(self):
        self.detail = "You cannot delete this profile"
