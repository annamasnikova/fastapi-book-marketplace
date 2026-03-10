from pydantic import BaseModel

from .books import ReturnedBook

__all__ = [
    "IncomingSeller",
    "ReturnedSeller",
    "ReturnedSellerWithBooks",
    "ReturnedAllSellers",
    "UpdateSeller",
]


class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    e_mail: str


class IncomingSeller(BaseSeller):
    password: str


class ReturnedSeller(BaseSeller):
    id: int


class ReturnedSellerWithBooks(ReturnedSeller):
    books: list[ReturnedBook] = []


class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]


class UpdateSeller(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    e_mail: str | None = None
