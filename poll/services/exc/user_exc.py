class UserNotFound(Exception):
    def __init__(self, user_id: int):
        self.detail = f"User with ID {user_id} not found."


class UserAlreadyExist(Exception):
    def __init__(self, user_email: str):
        self.detail = f"User with {user_email} already exist."


class UserNotAuthenticated(Exception):
    def __init__(self):
        self.detail = "Incorrect email or password"


class UserForbidden(Exception):
    def __init__(self):
        self.detail = "Access to the requested resource is forbidden."


class UserNotMemberError(Exception):
    def __init__(
        self,
    ):
        self.detail = f"User is not a member of the company."
