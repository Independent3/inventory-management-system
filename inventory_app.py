import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


class Product:
    def __init__(self, product_id, sku, quantity, name, price):
        self.product_id = product_id
        self.sku = sku
        self.quantity = 0 if quantity is None else quantity
        self.name = name
        self.price = float(price)

    def apply_discount(self, percentage):
        if percentage < 0 or percentage > 100:
            raise ValueError("Discount must be between 0 and 100.")
        self.price *= (1 - percentage / 100)
        return self.price

    def __str__(self):
        return (
            f"ID: {self.product_id} | Name: {self.name} | "
            f"SKU: {self.sku} | Quantity: {self.quantity} | Price: {self.price:.2f}"
        )


class Supplier:
    def __init__(self, supplier_id, name, email):
        self.supplier_id = supplier_id
        self.name = name
        self.email = email

    def __str__(self):
        return f"ID: {self.supplier_id} | Name: {self.name} | Email: {self.email}"


class ProductSupplier:
    def __init__(self, product_name, supplier_name, wholesale_price, lead_time):
        self.product_name = product_name
        self.supplier_name = supplier_name
        self.wholesale_price = float(wholesale_price)
        self.lead_time = int(lead_time)

    def __str__(self):
        return (
            f"Product: {self.product_name} | Supplier: {self.supplier_name} | "
            f"Wholesale Price: {self.wholesale_price:.2f} | Lead Time: {self.lead_time} days"
        )
class Restock:
    def __init__(self, restock_id , product_id, supplier_id, date , quantity_added):
        self.restock_id = restock_id
        self.product_id = product_id
        self.supplier_id = supplier_id
        self.date = date
        self.quantity_added = quantity_added

    def __str__(self):
        return (
            f"Restock: {self.restock_id} | Product: {self.product_id} | "
            f"Supplier: {self.supplier_id} | Date: {self.date} | "
            f"Quantity_Added: {self.quantity_added}"
        )
class Orders:
    def __init__(self, order_id, product_id, date_timestamp, quantity_sold):
        self.order_id = order_id
        self.product_id = product_id
        self.date_timestamp = date_timestamp
        self.quantity_sold = quantity_sold

    def __str__(self):
        return(
        f"Order: {self.order_id} | Product: {self.product_id} | "
        f"Date: {self.date_timestamp} | Sold: {self.quantity_sold}"
        )

class DatabaseManager:
    def __init__(self, host, user, password, db_name):
        self.host = host
        self.user = user
        self.password = password
        self.db_name = db_name
        self.connection = None

    def open_connection(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.db_name
            )
            print("Connected to MySQL successfully.")
            return True
        except mysql.connector.Error as err:
            print(f"Connection error: {err}")
            self.connection = None
            return False

    def ensure_connection(self):
        if self.connection is None or not self.connection.is_connected():
            print("No active connection. Trying to reconnect...")
            return self.open_connection()
        return True

    def get_all_products(self):
        if not self.ensure_connection():
            return []

        cursor = self.connection.cursor()
        try:
            query = "SELECT id, sku, quantity, name, price FROM products;"
            cursor.execute(query)
            return cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Query failed: {err}")
            return [] # Return empty list instead of None (safer)
        finally:
            cursor.close()

    def update_stock(self, product_id, quantity_change):
        if not self.ensure_connection():
            return -99

        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT quantity FROM products WHERE id = %s;", (product_id,))
            row = cursor.fetchone()

            if row is None:
                return -1

            current_quantity = row[0] if row[0] is not None else 0
            new_quantity = current_quantity + quantity_change

            if new_quantity < 0:
                return -2

            cursor.execute(
                "UPDATE products SET quantity = %s WHERE id = %s;",
                (new_quantity, product_id)
            )
            self.connection.commit()
            return cursor.rowcount
        except mysql.connector.Error as err:
            print(f"Stock update failed: {err}")
            return 0
        finally:
            cursor.close()

    def delete_product(self, product_id): ##need cascade delete or unlink to work if the product is linked
        if not self.ensure_connection():
            return 0

        cursor = self.connection.cursor()
        try:
            query = "DELETE FROM products WHERE id = %s;"
            cursor.execute(query, (product_id,))
            self.connection.commit()
            return cursor.rowcount
        except mysql.connector.Error as err:
            print(f"Delete failed: {err}")
            return 0
        finally:
            cursor.close()

    def insert_product(self, sku, quantity, name, price):
        if not self.ensure_connection():
            return False

        cursor = self.connection.cursor()
        try:
            query = """
                INSERT INTO products (sku, quantity, name, price)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (sku, quantity, name, price))
            self.connection.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            return False
        finally:
            cursor.close()

    def insert_supplier(self, name, email):
        if not self.ensure_connection():
            return False

        cursor = self.connection.cursor()
        try:
            query = "INSERT INTO suppliers (name, email) VALUES (%s, %s);"
            cursor.execute(query, (name, email))
            self.connection.commit()
            return True
        except mysql.connector.IntegrityError:
            print("Error: this email already exists.")
            return False
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            return False
        finally:
            cursor.close()

    def get_all_suppliers(self):
        if not self.ensure_connection():
            return []

        cursor = self.connection.cursor()
        try:
            query = "SELECT supplier_id, name, email FROM suppliers;"
            cursor.execute(query)
            return cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Query failed: {err}")
            return []
        finally:
            cursor.close()

    def link_product_to_supplier(self, product_id, supplier_id, wholesale_price, lead_time):
        if not self.ensure_connection():
            return False

        cursor = self.connection.cursor()
        try:
            query = """
                INSERT INTO product_suppliers
                (product_id, supplier_id, wholesale_price, lead_time_days)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (product_id, supplier_id, wholesale_price, lead_time))
            self.connection.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error: could not create link. Details: {err}")
            return False
        finally:
            cursor.close()

    def get_all_product_suppliers(self):
        if not self.ensure_connection():
            return []

        cursor = self.connection.cursor()
        query = """
            SELECT p.name, s.name, ps.wholesale_price, ps.lead_time_days
            FROM product_suppliers ps
            JOIN products p ON ps.product_id = p.id
            JOIN suppliers s ON ps.supplier_id = s.supplier_id;
        """
        try:
            cursor.execute(query)
            return cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return []
        finally:
            cursor.close()

    def unlink_product_from_supplier(self , product_id , supplier_id):
        if not self.ensure_connection():
            return 0
        cursor = self.connection.cursor()
        try:
            query = "DELETE FROM Product_Suppliers WHERE product_id = %s AND supplier_id = %s;"
            cursor.execute(query, (product_id, supplier_id,))
            self.connection.commit()
            return cursor.rowcount
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return 0
        finally:
            cursor.close()

    def restock_product(self, product_id , supplier_id , quantity_added):
        if not self.ensure_connection():
            return 0
        cursor = self.connection.cursor()
        try:
            if quantity_added > 0:
                query = """
                    INSERT INTO RESTOCK (PRODUCT_ID , SUPPLIER_ID , QUANTITY_ADDED) VALUES 
                    (%s , %s , %s)
                    """
                cursor.execute(query , (product_id , supplier_id , quantity_added,))
                cursor.execute("UPDATE products SET quantity = quantity + %s WHERE id = %s;",
                (quantity_added, product_id))
                self.connection.commit()
            else:
                return -1
            return 1
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return 0
        finally:
            cursor.close()

    def place_order(self, product_id, quantity_sold):
        if not self.ensure_connection():
            return 0
        cursor = self.connection.cursor()
        try:
            query = "SELECT Quantity from PRODUCTS WHERE id = %s"
            cursor.execute(query,(product_id,))
            row = cursor.fetchone()
            if row is not None:
                quantity = row[0]
                if quantity_sold > quantity:
                    return -2
                else:
                    query = "INSERT INTO Orders (product_id, quantity_sold) VALUES (%s, %s);"
                    cursor.execute(query, (product_id, quantity_sold))
                    query = "UPDATE products  SET quantity = quantity - %s WHERE id = %s"
                    cursor.execute(query,(quantity_sold,product_id,))
                    self.connection.commit()
                    return 1
            else:
                return -1
        except mysql.connector.Error:
            return 0
        finally:
            cursor.close()






    def close_connection(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed.")


if __name__ == "__main__":
    db = DatabaseManager(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "your_password_here"),
        db_name=os.getenv("DB_NAME", "inventory_system")
    )

    while True:
        print("\n===== Inventory System =====")
        print("1. View Products")
        print("2. Add Product")
        print("3. Update Stock")
        print("4. Delete Product")
        print("5. View Suppliers")
        print("6. Add Supplier")
        print("7. Link Product to Supplier")
        print("8. View Product-Supplier Links")
        print("9. Unlink Product from Supplier")
        print("10. Restock Product")
        print("11. Place Order")
        print("0. Exit")

        choice = input("Select an option: ").strip()

        if choice == "1":
            products = db.get_all_products()
            if not products:
                print("No products found.")
            else:
                print("\n--- Products ---")
                for row in products:
                    print(Product(*row))

        elif choice == "2":
            sku = input("SKU: ").strip()
            if not sku:
                print("Error: SKU cannot be empty.")
                continue
            if not sku[0].isalpha():
                print("Error: SKU must start with a letter.")
                continue

            try:
                quantity = int(input("Quantity: "))
            except ValueError:
                print("Error: quantity must be an integer.")
                continue

            if quantity < 0:
                print("Error: quantity cannot be negative.")
                continue

            name = input("Name: ").strip()
            if not name:
                print("Error: name cannot be empty.")
                continue

            try:
                price = float(input("Price: "))
            except ValueError:
                print("Error: price must be a number.")
                continue

            if price <= 0:
                print("Error: price must be greater than 0.")
                continue

            if db.insert_product(sku, quantity, name, price):
                print(f"Product '{name}' added successfully.")
            else:
                print("Could not add product. SKU may already exist.")

        elif choice == "3":
            try:
                product_id = int(input("Product ID: "))
                amount = int(input("Amount to add/remove: "))
            except ValueError:
                print("Error: please enter valid integers.")
                continue

            result = db.update_stock(product_id, amount)

            if result > 0:
                print(f"Stock updated for product ID {product_id}.")
            elif result == -1:
                print(f"Error: product ID {product_id} was not found.")
            elif result == -2:
                print("Error: stock cannot go below zero.")
            elif result == -99:
                print("Error: could not connect to the database.")
            else:
                print("Stock update failed.")

        elif choice == "4":
            try:
                product_id = int(input("Product ID to delete: "))
            except ValueError:
                print("Error: please enter a valid product ID.")
                continue

            confirm = input(f"Are you sure you want to delete product {product_id}? (y/n): ").strip().lower()
            if confirm != "y":
                print("Delete cancelled.")
                continue

            result = db.delete_product(product_id)
            if result > 0:
                print(f"Product {product_id} deleted successfully.")
            else:
                print(f"Error: product ID {product_id} does not exist or could not be deleted.")

        elif choice == "5":
            suppliers = db.get_all_suppliers()
            if not suppliers:
                print("No suppliers found.")
            else:
                print("\n--- Suppliers ---")
                for row in suppliers:
                    print(Supplier(*row))

        elif choice == "6":
            email = input("Email: ").strip()
            if not email:
                print("Error: email cannot be empty.")
                continue
            if " " in email:
                print("Error: email cannot contain spaces.")
                continue
            if "@" not in email or "." not in email:
                print("Error: invalid email format.")
                continue

            name = input("Name: ").strip()
            if not name:
                print("Error: name cannot be empty.")
                continue

            if db.insert_supplier(name, email):
                print(f"Supplier '{name}' added successfully.")
            else:
                print("Could not add supplier.")

        elif choice == "7":
            try:
                print("\n--- Link Product to Supplier ---")
                product_id = int(input("Product ID: "))
                supplier_id = int(input("Supplier ID: "))
                wholesale_price = float(input("Wholesale Price: "))
                lead_time = int(input("Lead Time (Days): "))
            except ValueError:
                print("Error: please enter valid numbers.")
                continue

            if wholesale_price <= 0:
                print("Error: wholesale price must be greater than 0.")
                continue

            if lead_time < 0:
                print("Error: lead time cannot be negative.")
                continue

            if db.link_product_to_supplier(product_id, supplier_id, wholesale_price, lead_time):
                print("Product linked to supplier successfully.")
            else:
                print("Could not create product-supplier link.")

        elif choice == "8":
            links = db.get_all_product_suppliers()
            if not links:
                print("No product-supplier links found.")
            else:
                print("\n--- Product-Supplier Links ---")
                for row in links:
                    print(ProductSupplier(*row))

        elif choice == "9":
            try:
                product_id = int(input("Product ID: "))
                supplier_id = int(input("Supplier ID: "))
            except ValueError:
                print("Error: Product id and Supplier id must be integers")
                continue
            result = db.unlink_product_from_supplier(product_id, supplier_id)
            if result > 0:
                print("Link Removed successfully")
            else:
                print("Error: Link not found")

        elif choice == "10":
            try:
                print("\n--- Restock ---")
                product_id = int(input("Product ID: "))
                supplier_id = int(input("Supplier ID: "))
                quantity_added = int(input("Quantity to add: "))
                if quantity_added <= 0:
                    print(f"Error: Quantity must be greater than zero , your input {quantity_added} is not valid")
                    continue
            except ValueError:
                print("Error: Product ID , Supplier ID and Quantity must be integers")
                continue
            result = db.restock_product(product_id, supplier_id, quantity_added)
            if  result == 1:
                print(f"Success! Quantity that was added {quantity_added}")
            elif result == -1:
                print("Invalid Quantity")
            else:
                print("Database Error")

        elif choice == "11":
            try:
                print("\n--- Order ---")
                product_id = int(input("Product ID: "))
                quantity_sold = int(input("Quantity: "))
                if quantity_sold <= 0:
                    print("Error: Invalid quantity , must be greater than 0")
                    continue
                else:
                    result = db.place_order(product_id, quantity_sold)
                    if result == 1:
                        print(f"Success! Sold {quantity_sold} units.")
                    elif result == -1:
                        print("Error: Product not found.")
                    elif result == -2:
                        print("Error: Not enough stock available.")
                    else:
                        print("Database error.")
            except ValueError:
                print(f"Error: Product ID and Quantity must be integers")
                continue

        elif choice == "0":
            db.close_connection()
            print("Goodbye.")
            break

        else:
            print("Invalid option. Please enter a number between 0 and 11.")