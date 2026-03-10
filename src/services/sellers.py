__all__ = ["SellerService"]

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.sellers import Seller
from src.schemas.sellers import IncomingSeller, UpdateSeller


class SellerService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_seller(self, seller: IncomingSeller) -> Seller:
        new_seller = Seller(
            first_name=seller.first_name,
            last_name=seller.last_name,
            e_mail=seller.e_mail,
            password=seller.password,
        )
        self.session.add(new_seller)
        await self.session.flush()
        return new_seller

    async def get_all_sellers(self) -> list[Seller]:
        query = select(Seller)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_single_seller(self, seller_id: int) -> Seller | None:
        query = select(Seller).where(Seller.id == seller_id).options(selectinload(Seller.books))
        result = await self.session.execute(query)
        return result.scalars().first()

    async def update_seller(self, seller_id: int, seller_data: UpdateSeller) -> Seller | None:
        if seller := await self.session.get(Seller, seller_id):
            if seller_data.first_name is not None:
                seller.first_name = seller_data.first_name
            if seller_data.last_name is not None:
                seller.last_name = seller_data.last_name
            if seller_data.e_mail is not None:
                seller.e_mail = seller_data.e_mail
            await self.session.flush()
            return seller

    async def delete_seller(self, seller_id: int) -> bool:
        query = select(Seller).where(Seller.id == seller_id).options(selectinload(Seller.books))
        result = await self.session.execute(query)
        seller = result.scalars().first()

        if seller:
            await self.session.delete(seller)
            return True
        return False
