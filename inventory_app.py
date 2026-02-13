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

class DatabaseManager:
    def __init__(self, host, user, pwd, db_name):
        self.host = host
        self.user = user
        self.password = pwd
        self.dbname = db_name
        self.connection = None

    def open_connection(self):
        """Actually opens the door to the database."""
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

    def close_connection(self):
        """Hangs up the phone line."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed")


if __name__ == "__main__":
    db = DatabaseManager(
        host="localhost",
        user="root",
        pwd="PASSWORD_HERE",
        db_name="inventory_system"
    )

    #Get raw tuples from DB
    raw_data = db.get_all_products()

    #Turn tuples into Product OBJECTS
    product_list = []
    for row in raw_data:
        # row mapping: (id, sku, quantity, name, price)
        p = Product(row[0], row[1], row[2], row[3], row[4])
        product_list.append(p)

    print(f"\nI found {len(product_list)} products in the database")

    #Use the objects
    for item in product_list:
        item.apply_discount(10)  # 10% off
        print(item)  #calls the __str__ method automatically

    db.close_connection()

