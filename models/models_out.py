from pydantic import BaseModel


class UserOut(BaseModel):
    id: int = None
    username: str = None
    email: str = None
    registration_date: str = None
