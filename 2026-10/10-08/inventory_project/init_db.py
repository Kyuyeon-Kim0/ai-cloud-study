"""Create tables and add stock columns to the original products table."""
from app.database import get_connection


def initialize():
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                product_name VARCHAR(100) NOT NULL,
                price DECIMAL(12,2) NOT NULL,
                quantity INT NOT NULL DEFAULT 0,
                min_stock INT NOT NULL DEFAULT 0,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                deleted_at DATETIME NULL,
                CONSTRAINT chk_price CHECK (price >= 0),
                CONSTRAINT chk_quantity CHECK (quantity >= 0),
                CONSTRAINT chk_min_stock CHECK (min_stock >= 0)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        cursor.execute("SHOW COLUMNS FROM products")
        column_info = {row[0]: row[1] for row in cursor.fetchall()}
        columns = set(column_info)
        if column_info["price"].lower() in {"int", "bigint", "mediumint", "smallint"}:
            cursor.execute("ALTER TABLE products MODIFY price DECIMAL(12,2) NOT NULL")
        for name, definition in {
            "quantity": "INT NOT NULL DEFAULT 0",
            "min_stock": "INT NOT NULL DEFAULT 0",
            "deleted_at": "DATETIME NULL",
        }.items():
            if name not in columns:
                cursor.execute(f"ALTER TABLE products ADD COLUMN {name} {definition}")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_movements (
                movement_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                product_id INT NOT NULL,
                change_amount INT NOT NULL,
                resulting_quantity INT NOT NULL,
                reason VARCHAR(200) NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                INDEX ix_movement_product (product_id, movement_id),
                FOREIGN KEY (product_id) REFERENCES products(product_id),
                CONSTRAINT chk_resulting_quantity CHECK (resulting_quantity >= 0)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        connection.commit()
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    initialize()
    print("MySQL tables initialized (existing products preserved).")
