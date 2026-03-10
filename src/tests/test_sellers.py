import pytest
from fastapi import status
from sqlalchemy import select

from src.models.books import Book
from src.models.sellers import Seller

API_V1_URL_PREFIX = "/api/v1/seller"


# Тест на создание продавца
@pytest.mark.asyncio()
async def test_create_seller(async_client):
    data = {
        "first_name": "Ivan",
        "last_name": "Ivanov",
        "e_mail": "ivan@example.com",
        "password": "secret123",
    }
    response = await async_client.post(f"{API_V1_URL_PREFIX}/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    resp_seller_id = result_data.pop("id", None)
    assert resp_seller_id is not None, "Seller id not returned from endpoint"

    assert result_data == {
        "first_name": "Ivan",
        "last_name": "Ivanov",
        "e_mail": "ivan@example.com",
    }

    # Проверяем, что пароль НЕ возвращается в ответе
    assert "password" not in response.json()


# Тест на получение списка всех продавцов
@pytest.mark.asyncio()
async def test_get_all_sellers(db_session, async_client):
    seller1 = Seller(
        first_name="Ivan",
        last_name="Ivanov",
        e_mail="ivan@example.com",
        password="secret123",
    )
    seller2 = Seller(
        first_name="Petr",
        last_name="Petrov",
        e_mail="petr@example.com",
        password="secret456",
    )

    db_session.add_all([seller1, seller2])
    await db_session.flush()

    response = await async_client.get(f"{API_V1_URL_PREFIX}/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["sellers"]) == 2

    # Проверяем, что пароль НЕ возвращается
    for seller in response.json()["sellers"]:
        assert "password" not in seller

    assert response.json() == {
        "sellers": [
            {
                "id": seller1.id,
                "first_name": "Ivan",
                "last_name": "Ivanov",
                "e_mail": "ivan@example.com",
            },
            {
                "id": seller2.id,
                "first_name": "Petr",
                "last_name": "Petrov",
                "e_mail": "petr@example.com",
            },
        ]
    }


# Тест на получение одного продавца с книгами
@pytest.mark.asyncio()
async def test_get_single_seller(db_session, async_client):
    seller = Seller(
        first_name="Ivan",
        last_name="Ivanov",
        e_mail="ivan@example.com",
        password="secret123",
    )

    db_session.add(seller)
    await db_session.flush()

    book1 = Book(author="Pushkin", title="Eugeny Onegin", year=2021, pages=104, seller_id=seller.id)
    book2 = Book(author="Lermontov", title="Mziri", year=2022, pages=108, seller_id=seller.id)

    db_session.add_all([book1, book2])
    await db_session.flush()

    response = await async_client.get(f"{API_V1_URL_PREFIX}/{seller.id}")

    assert response.status_code == status.HTTP_200_OK

    result = response.json()

    # Проверяем, что пароль НЕ возвращается
    assert "password" not in result

    assert result["id"] == seller.id
    assert result["first_name"] == "Ivan"
    assert result["last_name"] == "Ivanov"
    assert result["e_mail"] == "ivan@example.com"
    assert len(result["books"]) == 2


# Тест на получение несуществующего продавца
@pytest.mark.asyncio()
async def test_get_single_seller_with_wrong_id(async_client):
    response = await async_client.get(f"{API_V1_URL_PREFIX}/999999")

    assert response.status_code == status.HTTP_404_NOT_FOUND


# Тест на обновление продавца
@pytest.mark.asyncio()
async def test_update_seller(db_session, async_client):
    seller = Seller(
        first_name="Ivan",
        last_name="Ivanov",
        e_mail="ivan@example.com",
        password="secret123",
    )

    db_session.add(seller)
    await db_session.flush()

    data = {
        "first_name": "Petr",
        "last_name": "Petrov",
        "e_mail": "petr@example.com",
    }

    response = await async_client.put(f"{API_V1_URL_PREFIX}/{seller.id}", json=data)

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result["first_name"] == "Petr"
    assert result["last_name"] == "Petrov"
    assert result["e_mail"] == "petr@example.com"
    assert "password" not in result


# Тест на обновление несуществующего продавца
@pytest.mark.asyncio()
async def test_update_seller_with_wrong_id(async_client):
    data = {
        "first_name": "Petr",
    }

    response = await async_client.put(f"{API_V1_URL_PREFIX}/999999", json=data)

    assert response.status_code == status.HTTP_404_NOT_FOUND


# Тест на удаление продавца (вместе с книгами)
@pytest.mark.asyncio()
async def test_delete_seller(db_session, async_client):
    seller = Seller(
        first_name="Ivan",
        last_name="Ivanov",
        e_mail="ivan@example.com",
        password="secret123",
    )

    db_session.add(seller)
    await db_session.flush()

    book = Book(author="Pushkin", title="Eugeny Onegin", year=2021, pages=104, seller_id=seller.id)
    db_session.add(book)
    await db_session.flush()

    response = await async_client.delete(f"{API_V1_URL_PREFIX}/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Проверяем, что продавец удален
    await db_session.flush()
    result = await db_session.execute(select(Seller).where(Seller.id == seller.id))
    assert result.scalars().first() is None

    # Проверяем, что книги продавца тоже удалены
    books_result = await db_session.execute(select(Book).where(Book.seller_id == seller.id))
    assert books_result.scalars().all() == []


# Тест на удаление несуществующего продавца
@pytest.mark.asyncio()
async def test_delete_seller_with_wrong_id(async_client):
    response = await async_client.delete(f"{API_V1_URL_PREFIX}/999999")

    assert response.status_code == status.HTTP_404_NOT_FOUND
