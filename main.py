# GET /books - получение списка книг
# POST /books - создание
# PUT/PATCH /books/{book_id} - обновление
# GET /books/{book_id} - получение 1 книги
# DELETE /books/{book_id} - удаление

# 2xx - OK
# 3xx - Redirects
# 4xx - Client errors
# 5xx - Server errors

# CRUD - Create, Read, Update, Delete

from fastapi import FastAPI, status
from fastapi.responses import ORJSONResponse, Response
from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError

COUNTER = 1  # Каунтер, иметирующий присвоение id в базе данных


# Само приложение fastApi. именно оно запускается сервером и служит точкой входа
# в нем можно указать разные параметры для сваггера и для эндпоинтов.
app = FastAPI(
    title="Book Library App",
    description="Учебное приложение для MTS Shad",
    version="0.0.1",
    responses={404: {"description": "Object not found!"}},
    default_response_class=ORJSONResponse,  # Подключаем быстрый сериализатор
)


# симулируем хранилище данных. Просто сохраняем объекты в память, в словаре.
# {0: {"id": 1, "title": "blabla", ...., "year": 2023}}
fake_storage = {}


# Базовый класс "Книги", содержащий поля, которые есть во всех классах-наследниках.
class BaseBook(BaseModel):
    title: str
    author: str
    year: int


# Класс для обработки входных данных для частичного обновления данных о книге
class PatchBook(BaseModel):
    title: str | None = None
    author: str | None = None
    year: int | None = None
    pages: int | None = None


# Класс для валидации входящих данных. Не содержит id так как его присваивает БД.
class IncomingBook(BaseBook):
    pages: int = Field(
        default=100, alias="count_pages"
    )  # Пример использования тонкой настройки полей. Передачи в них метаинформации.

    @field_validator("year")  # Валидатор, проверяет что дата не слишком древняя
    @staticmethod
    def validate_year(val: int):
        if val < 2020:
            raise PydanticCustomError("Validation error", "Year is too old!")

        return val


# Класс, валидирующий исходящие данные. Он уже содержит id
class ReturnedBook(BaseBook):  # {"id": 1, "title": "Clean Code", ....}
    id: int
    pages: int | None = None


# Класс для возврата массива объектов "Книга"
class ReturnedAllBooks(BaseModel):
    books: list[ReturnedBook]


# Просто пример ручки и того, как ее можно исключить из схемы сваггера
@app.get("/main", include_in_schema=False)
async def main():
    return "Hello World!"


# Ручка, возвращающая все книги
@app.get("/books", response_model=ReturnedAllBooks)
async def get_all_books():
    # Хотим видеть формат
    # books: [{"id": 1, "title": "blabla", ...., "year": 2023},{...}]
    books = list(fake_storage.values())
    return {"books": books}


# Ручка для создания записи о книге в БД. Возвращает созданную книгу.
@app.post("/books", response_model=ReturnedBook, status_code=status.HTTP_201_CREATED)
async def create_book(
    book: IncomingBook,
):  # прописываем модель валидирующую входные данные
    global COUNTER  # счетчик ИД нашей фейковой БД

    # TODO запись в БД
    # это - бизнес логика. Обрабатываем данные, сохраняем, преобразуем и т.д.
    new_book = {
        "id": COUNTER,
        "title": book.title,
        "author": book.author,
        "year": book.year,
        "pages": book.pages,
    }

    fake_storage[COUNTER] = new_book
    COUNTER += 1

    # return ORJSONResponse({"book": new_book}, status_code=status.HTTP_201_CREATED) # Альтернатива для возврата кода
    return new_book


# Ручка для получения книги по ее ИД
@app.get("/books/{book_id}", response_model=ReturnedBook)
async def get_single_book(book_id: int):
    book = fake_storage.get(book_id)

    if book is not None:
        return book

    return Response(status_code=status.HTTP_404_NOT_FOUND)


# Ручка для удаления книги
@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int):
    deleted_book = fake_storage.pop(book_id, None)
    if deleted_book is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)


# Ручка для обновления данных о книге
@app.put("/books/{book_id}", response_model=ReturnedBook)
async def update_book(book_id: int, new_book_data: ReturnedBook):
    # book = fake_storage.get(book_id, None)
    # if book:
    # Оператор "морж", позволяющий одновременно и присвоить значение и проверить его. Заменяет то, что закомментировано выше.
    if _ := fake_storage.get(book_id):
        new_book = {
            "id": book_id,
            "title": new_book_data.title,
            "author": new_book_data.author,
            "year": new_book_data.year,
            "pages": new_book_data.pages,
        }

        fake_storage[book_id] = new_book

    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    return fake_storage[book_id]


# Ручка для частичного обновления данных о книге
@app.patch("/books/{book_id}", response_model=ReturnedBook)
async def patch_book(book_id: int, patched_book: PatchBook):
    if book := fake_storage.get(book_id):

        if patched_book.title is not None and patched_book.title != book["title"]:
            book["title"] = patched_book.title
        if patched_book.author is not None and patched_book.author != book["author"]:
            book["author"] = patched_book.author
        if patched_book.year is not None and patched_book.year != book["year"]:
            book["year"] = patched_book.year
        if patched_book.pages is not None and patched_book.pages != book["pages"]:
            book["pages"] = patched_book.pages

        fake_storage[book_id] = book

    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    return fake_storage[book_id]
