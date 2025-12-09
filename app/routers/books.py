from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
import httpx
import logging

from .. import schemas, models, database, dependencies

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/books",
    tags=["Books"]
)

@router.get("/", response_model=List[schemas.Book])
async def get_all_books(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(database.get_db)
):
    result = await db.execute(select(models.Book).offset(skip).limit(limit))
    books = result.scalars().all()
    return books

@router.get("/{book_id}", response_model=schemas.Book)
async def get_book(book_id: int, db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.Book).where(models.Book.id == book_id))
    book = result.scalars().first()
    
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.put("/{book_id}", response_model=schemas.Book)
async def update_book(
    book_id: int, 
    book_update: schemas.BookCreate, 
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    result = await db.execute(select(models.Book).where(models.Book.id == book_id))
    db_book = result.scalars().first()

    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    
    db_book.title = book_update.title
    db_book.author = book_update.author
    db_book.isbn = book_update.isbn
    db_book.description = book_update.description
    db_book.cover_url = book_update.cover_url
    
    await db.commit()
    await db.refresh(db_book)
    return db_book

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: int, 
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only administrators can delete books")
    
    result = await db.execute(select(models.Book).where(models.Book.id == book_id))
    db_book = result.scalars().first()

    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    
    await db.delete(db_book)
    await db.commit()
    return None

@router.post("/search-by-isbn", response_model=schemas.Book, status_code=status.HTTP_201_CREATED)
async def search_book_by_isbn(
    isbn_request: schemas.ISBNSearch,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    logger.info(f"ISBN search started. Request: {isbn_request}, User: {current_user.username}")
    
    isbn = isbn_request.isbn.strip()
    logger.info(f"ISBN value processed: '{isbn}' (length: {len(isbn)})")
    
    result = await db.execute(select(models.Book).where(models.Book.isbn == isbn))
    existing_book = result.scalars().first()
    
    if existing_book:
        logger.info(f"Book already exists in database: ID={existing_book.id}, Title={existing_book.title}")
        return existing_book
    
    logger.info("Book not found in database, starting external API call...")
    
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            api_url = f"https://openlibrary.org/isbn/{isbn}.json"
            logger.info(f"Open Library API call: {api_url}")
            
            response = await client.get(
                api_url,
                timeout=10.0,
                follow_redirects=True
            )
            
            logger.info(f"API response status: {response.status_code}")
            
            if response.status_code == 404:
                logger.warning(f"Book not found in Open Library for ISBN: {isbn}")
                raise HTTPException(status_code=404, detail="Book not found with this ISBN")
            
            if response.status_code != 200:
                logger.error(f"API error status: {response.status_code}, response: {response.text[:200]}")
                raise HTTPException(status_code=500, detail="Error occurred during external API call")
            
            book_data = response.json()
            logger.info(f"API response data: title={book_data.get('title', 'N/A')}, authors={book_data.get('authors', [])}")
            
            title = book_data.get("title", "Unknown title")
            if not title or not isinstance(title, str):
                title = "Unknown title"
            
            authors = book_data.get("authors", [])
            author = "Unknown author"
            
            if authors and len(authors) > 0:
                try:
                    if isinstance(authors[0], dict):
                        author_key = authors[0].get("key", "")
                        if author_key:
                            try:
                                author_response = await client.get(
                                    f"https://openlibrary.org{author_key}.json",
                                    timeout=5.0
                                )
                                if author_response.status_code == 200:
                                    author_data = author_response.json()
                                    author = author_data.get("name", "Unknown author")
                            except (httpx.RequestError, httpx.TimeoutException, Exception):
                                pass
                    elif isinstance(authors[0], str):
                        author = authors[0]
                except (AttributeError, IndexError, TypeError, Exception):
                    author = "Unknown author"
            
            description = book_data.get("description", "")
            if isinstance(description, dict):
                description = description.get("value", "") or ""
            if not isinstance(description, str):
                description = str(description) if description else ""
            if len(description) > 10000:
                description = description[:10000]
            
            cover_url = None
            covers = book_data.get("covers", [])
            if covers:
                cover_id = covers[0]
                cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
            
            logger.info(f"Creating new book: title={title}, author={author}, isbn={isbn}")
            
            new_book = models.Book(
                title=title,
                author=author,
                isbn=isbn,
                description=description,
                cover_url=cover_url
            )
            
            db.add(new_book)
            await db.commit()
            await db.refresh(new_book)
            
            logger.info(f"Book successfully created: ID={new_book.id}")
            return new_book
            
    except httpx.TimeoutException as e:
        logger.error(f"Timeout during API call: {str(e)}")
        raise HTTPException(status_code=504, detail="Timeout during external API call")
    except httpx.RequestError as e:
        logger.error(f"Request error during API call: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error occurred while accessing external API: {str(e)}")
    except HTTPException as e:
        logger.warning(f"HTTPException: {e.status_code} - {e.detail}")
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Unexpected error during ISBN search: {str(e)}\nTraceback:\n{error_trace}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")