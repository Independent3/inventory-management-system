import os
from flask import Flask, request
from dotenv import load_dotenv
from inventory_app import DatabaseManager

load_dotenv()

app = Flask(__name__)

db = DatabaseManager(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", "your_password_here"),
    db_name=os.getenv("DB_NAME", "inventory_system")
)


@app.route("/")
def home():
    return {
        "message": "Inventory API is running!",
        "endpoints": [
            "GET /products",
            "GET /suppliers",
            "GET /links",
            "GET /orders",
            "GET /restocks",
            "POST /add-product",
            "POST /add-supplier",
            "POST /link",
            "DELETE /unlink",
            "POST /restock",
            "POST /order",
        ],
    }


@app.route("/products", methods=["GET"])
def get_products():
    rows = db.get_all_products()
    products = []

    for row in rows: ## tuple of values to dictionary
        products.append({
            "id": row[0],
            "sku": row[1],
            "quantity": row[2],
            "name": row[3],
            "price": row[4],
        })

    return {"products": products}, 200 #returning dictionary (easier to add features later like pagination)


@app.route("/suppliers", methods=["GET"])
def get_suppliers():
    rows = db.get_all_suppliers()
    suppliers = []

    for row in rows:
        suppliers.append({
            "supplier_id": row[0],
            "name": row[1],
            "email": row[2],
        })

    return {"suppliers": suppliers}, 200


@app.route("/links", methods=["GET"])
def get_links():
    rows = db.get_all_product_suppliers()
    links = []

    for row in rows:
        links.append({
            "product_name": row[0],
            "supplier_name": row[1],
            "wholesale_price": row[2],
            "lead_time_days": row[3],
        })

    return {"links": links}, 200


@app.route("/orders", methods=["GET"])
def get_orders():
    if not db.ensure_connection():
        return {"error": "Database connection failed"}, 500

    cursor = db.connection.cursor()
    try:
        cursor.execute(
            "SELECT order_id, product_id, date, quantity_sold FROM orders;"
        )
        rows = cursor.fetchall()

        orders = []
        for row in rows:
            orders.append({
                "order_id": row[0],
                "product_id": row[1],
                "date": str(row[2]),
                "quantity_sold": row[3]
            })

        return {"orders": orders}, 200

    except Exception as e:
        print(f"Error: {e}")
        return {"error": "Database error"}, 500
    finally:
        cursor.close()


@app.route("/restocks", methods=["GET"])
def get_restocks():
    if not db.ensure_connection():
        return {"error": "Database connection failed"}, 500

    cursor = db.connection.cursor()
    try:
        cursor.execute(
            "SELECT restock_id, product_id, supplier_id, date, quantity_added FROM restock;"
        )
        rows = cursor.fetchall()

        restocks = []
        for row in rows:
            restocks.append({
                "restock_id": row[0],
                "product_id": row[1],
                "supplier_id": row[2],
                "date": str(row[3]),
                "quantity_added": row[4]
            })

        return {"restocks": restocks}, 200

    except Exception as e:
        print(f"Error: {e}")
        return {"error": "Database error"}, 500
    finally:
        cursor.close()


@app.route("/add-product", methods=["POST"])
def add_product():
    data = request.get_json()
    if not data:
        return {"error": "Invalid or missing JSON body"}, 400

    try:
        sku = str(data.get("sku")).strip()
        quantity = int(data.get("quantity"))
        name = str(data.get("name")).strip()
        price = float(data.get("price"))
    except (TypeError, ValueError):
        return {"error": "Invalid product data types"}, 400

    if not sku:
        return {"error": "SKU cannot be empty"}, 400
    if not sku[0].isalpha():
        return {"error": "SKU must start with a letter"}, 400
    if quantity < 0:
        return {"error": "Quantity cannot be negative"}, 400
    if not name:
        return {"error": "Name cannot be empty"}, 400
    if price <= 0:
        return {"error": "Price must be greater than 0"}, 400

    success = db.insert_product(sku, quantity, name, price) #the result is true or false depending the success or not

    if success:
        return {"message": "Product added successfully"}, 201
    return {"error": "Could not add product"}, 400


@app.route("/add-supplier", methods=["POST"])
def add_supplier():
    data = request.get_json()
    if not data:
        return {"error": "Invalid or missing JSON body"}, 400

    name = data.get("name")
    email = data.get("email")

    if not isinstance(name, str) or not name.strip():
        return {"error": "Name cannot be empty"}, 400
    if not isinstance(email, str) or not email.strip():
        return {"error": "Email cannot be empty"}, 400

    name = name.strip()
    email = email.strip()

    if " " in email or "@" not in email or "." not in email:
        return {"error": "Invalid email format"}, 400

    success = db.insert_supplier(name, email)

    if success:
        return {"message": "Supplier added successfully"}, 201
    return {"error": "Could not add supplier"}, 400


@app.route("/link", methods=["POST"])
def link_product_supplier():
    data = request.get_json()
    if not data:
        return {"error": "Invalid or missing JSON body"}, 400

    try:
        product_id = int(data.get("product_id"))
        supplier_id = int(data.get("supplier_id"))
        wholesale_price = float(data.get("wholesale_price"))
        lead_time = int(data.get("lead_time"))
    except (TypeError, ValueError):
        return {"error": "Invalid link data types"}, 400

    if wholesale_price <= 0:
        return {"error": "Wholesale price must be greater than 0"}, 400
    if lead_time < 0:
        return {"error": "Lead time cannot be negative"}, 400

    success = db.link_product_to_supplier(
        product_id, supplier_id, wholesale_price, lead_time
    )

    if success:
        return {"message": "Product linked to supplier successfully"}, 201
    return {"error": "Could not create link"}, 400


@app.route("/unlink", methods=["DELETE"])
def unlink_product_supplier():
    data = request.get_json()
    if not data:
        return {"error": "Invalid or missing JSON body"}, 400

    try:
        product_id = int(data.get("product_id"))
        supplier_id = int(data.get("supplier_id"))
    except (TypeError, ValueError):
        return {"error": "Product ID and supplier ID must be integers"}, 400

    result = db.unlink_product_from_supplier(product_id, supplier_id)

    if result > 0:
        return {"message": "Link removed successfully"}, 200
    return {"error": "Link not found"}, 404


@app.route("/restock", methods=["POST"])
def restock_product():
    data = request.get_json()
    if not data:
        return {"error": "Invalid or missing JSON body"}, 400

    try:
        product_id = int(data.get("product_id"))
        supplier_id = int(data.get("supplier_id"))
        quantity = int(data.get("quantity"))
    except (TypeError, ValueError):
        return {"error": "Product ID, supplier ID and quantity must be integers"}, 400

    if quantity <= 0:
        return {"error": "Quantity must be greater than 0"}, 400

    result = db.restock_product(product_id, supplier_id, quantity)

    if result == 1:
        return {"message": "Product restocked successfully"}, 200
    elif result == -1:
        return {"error": "Invalid quantity"}, 400
    else:
        return {"error": "Database error"}, 500


@app.route("/order", methods=["POST"])
def place_order():
    data = request.get_json()
    if not data:
        return {"error": "Invalid or missing JSON body"}, 400

    try:
        product_id = int(data.get("product_id"))
        quantity = int(data.get("quantity"))
    except (TypeError, ValueError):
        return {"error": "Product ID and quantity must be integers"}, 400

    if quantity <= 0:
        return {"error": "Quantity must be greater than 0"}, 400

    result = db.place_order(product_id, quantity)

    if result == 1:
        return {"message": "Order placed successfully"}, 200
    elif result == -1:
        return {"error": "Product not found"}, 404
    elif result == -2:
        return {"error": "Not enough stock available"}, 400
    else:
        return {"error": "Database error"}, 500


@app.errorhandler(404) #error handlers for flask for errors it generates itself
def not_found(error):
    return {"error": "Endpoint not found"}, 404


@app.errorhandler(405)
def method_not_allowed(error):
    return {"error": "Method not allowed for this endpoint"}, 405


@app.errorhandler(500)
def internal_error(error):
    return {"error": "Internal server error"}, 500


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)