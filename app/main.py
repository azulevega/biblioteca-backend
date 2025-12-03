from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# Importar modelos y base de datos
from . import models, database

# Crear las tablas en la base de datos (si no existen)
# Nota: En este proyecto usamos init.sql para la tabla 'books', 
# pero esta línea asegura que la base esté lista para el ORM.
database.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="API de Biblioteca",
    description="API RESTful para gestionar libros con FastAPI y MySQL."
)

# Dependencia para obtener la sesión de la DB
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Endpoints CRUD ---

# POST /books: Crea un libro [cite: 15]
@app.post("/books", response_model=models.Book, status_code=status.HTTP_201_CREATED)
def create_book(book: models.BookBase, db: Session = Depends(get_db)):
    db_book = database.BookORM(**book.model_dump())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

# GET /books: Lista todos los libros [cite: 15]
@app.get("/books", response_model=List[models.Book])
def read_books(db: Session = Depends(get_db)):
    books = db.query(database.BookORM).all()
    return books

# GET /books/{id}: Obtiene un libro por su identificador [cite: 16]
@app.get("/books/{id}", response_model=models.Book)
def read_book(id: int, db: Session = Depends(get_db)):
    db_book = db.query(database.BookORM).filter(database.BookORM.id == id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

# PUT /books/{id}: Actualiza un libro existente [cite: 16]
@app.put("/books/{id}", response_model=models.Book)
def update_book(id: int, book: models.BookBase, db: Session = Depends(get_db)):
    db_book = db.query(database.BookORM).filter(database.BookORM.id == id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    # Actualiza los campos
    for key, value in book.model_dump().items():
        setattr(db_book, key, value)
    
    db.commit()
    db.refresh(db_book)
    return db_book

# DELETE /books/{id}: Elimina un libro [cite: 16]
@app.delete("/books/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(id: int, db: Session = Depends(get_db)):
    db_book = db.query(database.BookORM).filter(database.BookORM.id == id)
    if db_book.first() is None:
        raise HTTPException(status_code=404, detail="Book not found")
    
    db_book.delete(synchronize_session=False)
    db.commit()
    return {"ok": True}
