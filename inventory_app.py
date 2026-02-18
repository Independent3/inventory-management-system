import mysql.connector


class Product:
    def __init__(self, id, sku, quantity, name, price):
        self.id = id
        self.sku = sku
        if quantity is None:
            self.quantity = 0
        else:
            self.quantity = quantity
        self.name = name
        self.price = float(price)

    def apply_discount(self, percentage):
        self.price = (1 - (percentage / 100)) * self.price
        return self.price

    def __str__(self):

        return f"ID: {self.id} | Name: {self.name} | Sku: {self.sku} | Quantity: {self.quantity} | Price: {self.price:.2f}"

class Supplier:
    def __init__(self, id , name , email):
        self.id = id
        self.name = name
        self.email = email

    def __str__(self):
        return f"ID: {self.id} | Name: {self.name} | Email: {self.email}"


class DatabaseManager:
    def __init__(self, host, user, pwd, db_name):
        self.host = host
        self.user = user
        self.password = pwd
        self.dbname = db_name
        self.connection = None

    def open_connection(self):

        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.dbname
            )
            print("Successfully connected to MySQL.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")


    def get_all_products(self):
        if self.connection is None or not self.connection.is_connected():
            print("No connection! Opening it now...")
            self.open_connection()
        cursor = self.connection.cursor()
        try:
            query = "SELECT * FROM products;"
            cursor.execute(query)
            results = cursor.fetchall()
            return results
        except mysql.connector.Error as err:
            print(f"Query failed: {err}")
            return []
        finally:
            #Release the messenger (Clean up)
            cursor.close()

    def update_stock(self, product_id , quantity):
        if self.connection is None or not self.connection.is_connected():
            print("No connection! Opening it now...")
            self.open_connection()
        cursor = self.connection.cursor()
        query = "UPDATE products SET quantity = quantity + %s WHERE id = %s;"
        cursor.execute(query, (quantity, product_id))
        self.connection.commit()
        affected = cursor.rowcount
        cursor.close()
        return affected

    def delete(self, product_id):
        if self.connection is None or not self.connection.is_connected():
            print("No connection! Opening it now...")
            self.open_connection()
        cursor = self.connection.cursor()
        query = "DELETE FROM Products WHERE ID = %s;"
        cursor.execute(query,(product_id,))
        self.connection.commit()
        affected = cursor.rowcount
        cursor.close()
        return affected

    def insert_product(self, sku , quantity , name , price):
        if self.connection is None or not self.connection.is_connected():
            print("No connection! Opening it now...")
            self.open_connection()
        cursor = self.connection.cursor()
        try:
            query = "INSERT INTO Products (SKU, QUANTITY, NAME, PRICE) Values ( %s , %s , %s , %s)"
            cursor.execute(query,(sku ,quantity ,name ,price,))
            self.connection.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Database Error: {err}")
            return False
        finally:
            cursor.close()

    def insert_supplier(self, name, email):
        if self.connection is None or not self.connection.is_connected():
            print("No connection! Opening it now...")
            self.open_connection()
        cursor = self.connection.cursor()
        try:
            query = "INSERT INTO SUPPLIERS (name,email) VALUES (%s , %s )"
            cursor.execute(query , (name,email,))
            self.connection.commit()
        except mysql.connector.IntegrityError:
            print("Error: Email already exists")
        finally:
            cursor.close()

    def get_all_suppliers(self):
        if self.connection is None or not self.connection.is_connected():
            print("No connection! Opening it now...")
            self.open_connection()
        cursor = self.connection.cursor()
        query = "SELECT * FROM SUPPLIERS"
        cursor.execute(query,)
        result = cursor.fetchall()
        cursor.close()
        return result





    def close_connection(self):

        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed")




if __name__ == "__main__":
    db = DatabaseManager(
        host="localhost",
        user="root",
        pwd="YOUR PASSWORD HERE",
        db_name="inventory_system"
    )

    while True:
        print("\n--- Inventory System ---")
        print("1. View Products")
        print("2. Add Product")
        print("3. Update Stock")
        print("4. Delete Product")
        print("5. View Suppliers")
        print("6. Add Supplier")
        print("0. Exit")

        choice = input("Select an option: ")

        if choice == "1":
            raw_data = db.get_all_products()
            for row in raw_data:
                print(Product(*row))  # pass all row items to Product

        elif choice == "2":
            sku = input("SKU: ").strip()
            if not sku:
                print("Error: SKU cannot be empty")
                continue
            elif not sku[0].isalpha() :
                print("Error: SKU must start with a letter (A-Z)")
                continue
            try:
                qty = int(input("Quantity: "))
            except ValueError:
                print("Error: You must enter an integer for quantity")
                continue
            if qty < 0:
                print("Error: Quantity shouldn't be < 0")
                continue
            name = input("Name: ").strip()
            if not name:
                print("Error: Name can't be empty")
                continue
            if not name.replace(" ", "").isalnum():
                print("Error: Special characters (symbols) are not allowed.")
                continue
            try:
                price = float(input("Price: "))
            except ValueError:
                print("Error: price should be a number")
                continue
            if price <= 0:
                print("price should be a positive number")
                continue
            if db.insert_product(sku, qty, name, price):
                print(f"Success: {name} added to inventory")
            else:
                print(f"Failure: Could not add product(SKU might be a duplicate)")

        elif choice == "3":
            try:
                pid = int(input("Product ID: "))
                amt = int(input("Amount to add/remove: "))
                result = db.update_stock(pid, amt)
                if result > 0:
                    print(f"Success! Updated stock for ID {pid}.")
                else:
                    print(f"Error: Product with ID {pid} was not found.")
            except ValueError:
                print("Error: Please enter valid numbers.")
                continue
        elif choice == "4":
            try:
                pid = int(input("ID to delete: "))
                result = db.delete(pid)
                if result > 0:
                    print(f"Success: Product {pid} deleted.")
                else:
                    print(f"Error: Product ID {pid} does not exist in the database.")
            except ValueError:
                print("Error: Please enter an existing ID")
                continue
        elif choice == "5":
            suppliers = db.get_all_suppliers()
            for supplier in suppliers:
                print(Supplier(*supplier))
        elif choice == "6":
            email = input("Enter the Email")
            if not email:
                print("Error: Empty email is not allowed")
                continue
            if " " in email:
                print("Error: Email should not contain spaces")
                continue
            if not email[0].isalpha():
                print("Error: Email should start with A-z or a-z")
                continue
            name = input("Enter the Name").strip()
            if not name:
                print("Error: Name can't be empty")
                continue
            db.insert_supplier(name,email)

        elif choice == "0":
            db.close_connection()
            break
        else:
            print("\n[!] Invalid input. Please enter a number between 0 and 4.")
