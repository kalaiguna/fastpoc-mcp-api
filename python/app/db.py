"""
Implements an SQLite database with CRUD operations for Products.
Uses context managers for proper connection handling.
"""
from typing import List, Optional
from contextlib import contextmanager
import sqlite3
import os

from app.models import Product, ProductCreate, ProductUpdate


class ProductNotFoundError(Exception):
    """Exception raised when a product is not found."""
    pass


# Allowed columns for update operations (prevents SQL injection)
ALLOWED_UPDATE_COLUMNS = {'name', 'description', 'price', 'stock'}


class SQLiteDB:
    def __init__(self, db_path: str = None):
        """Initialize database with proper path management.
        
        Args:
            db_path: Path to SQLite database file. If None, uses application directory.
        """
        if db_path is None:
            # Use absolute path based on this file's location
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.db_path = os.path.join(base_dir, "products.db")
        else:
            self.db_path = db_path
        self._init_db()

    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Allow accessing columns by name
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        """Initialize the database with the products table."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    price REAL NOT NULL,
                    stock INTEGER NOT NULL
                )
            ''')
            conn.commit()
            
            # Check if empty, if so populate test data
            cursor.execute("SELECT COUNT(*) FROM products")
            count = cursor.fetchone()[0]
            if count == 0:
                self._populate_test_data(conn)

    def _populate_test_data(self, conn):
        """Populate the database with 30 dummy records."""
        cursor = conn.cursor()
        for i in range(1, 31):
            cursor.execute('''
                INSERT INTO products (name, description, price, stock)
                VALUES (?, ?, ?, ?)
            ''', (
                f"Sample Product {i}",
                f"This is a description for sample product {i}",
                round(10.0 + (i * 1.5), 2),
                10 + i
            ))
        conn.commit()

    def _row_to_product(self, row) -> Product:
        return Product(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            price=row["price"],
            stock=row["stock"]
        )

    def get_all(self) -> List[Product]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products")
            rows = cursor.fetchall()
            return [self._row_to_product(row) for row in rows]

    def get_by_id(self, product_id: int) -> Product:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
            row = cursor.fetchone()
            
            if row is None:
                raise ProductNotFoundError(f"Product with id {product_id} not found")
            return self._row_to_product(row)

    def create(self, product_in: ProductCreate) -> Product:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO products (name, description, price, stock)
                VALUES (?, ?, ?, ?)
            ''', (
                product_in.name,
                product_in.description,
                product_in.price,
                product_in.stock
            ))
            conn.commit()
            new_id = cursor.lastrowid
            
            # Return the created product with its new ID
            return Product(id=new_id, **product_in.model_dump())

    def update(self, product_id: int, product_in: ProductUpdate) -> Product:
        # First ensure existence
        existing_product = self.get_by_id(product_id)
        
        # Prepare update data
        update_data = product_in.model_dump(exclude_unset=True)
        if not update_data:
            return existing_product

        # Validate column names to prevent SQL injection
        for key in update_data.keys():
            if key not in ALLOWED_UPDATE_COLUMNS:
                raise ValueError(f"Invalid column name: {key}")

        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            set_clause = ", ".join([f"{key} = ?" for key in update_data.keys()])
            values = list(update_data.values())
            values.append(product_id)
            
            cursor.execute(f"UPDATE products SET {set_clause} WHERE id = ?", values)
            conn.commit()
            
            return self.get_by_id(product_id)

    def delete(self, product_id: int) -> bool:
        # First ensure existence to raise error if not found
        self.get_by_id(product_id)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
            conn.commit()
            return True

# Global database instance
db = SQLiteDB()
