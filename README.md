# 📦 Inventory Management System API

A backend inventory management system built with Python, Flask, and MySQL.  
The application provides a RESTful API for managing products, suppliers, stock levels, and order logistics with proper relational database design.

---

## 💥 Features

✅ Product Management (Create, View, Update, Delete)  
✅ Supplier Management with unique email validation  
✅ Product–Supplier Relationships (many-to-many)  
✅ Order Processing with real-time stock validation  
✅ Restocking System with supplier tracking  
✅ Historical Tracking (Orders & Restocks)  
✅ REST API with structured JSON responses  
✅ Input Validation & Error Handling
✅ Docker containerization with docker-compose  
✅ GitHub Actions CI/CD pipeline

---

## 🧠 System Design

- Relational database using **MySQL**
- Foreign key constraints ensure data integrity
- Separation of concerns:
  - `inventory_app.py` → Database logic
  - `app.py` → Flask API layer

---

## 🌐 API Endpoints

### 🔹 GET Endpoints
- `/products` → Get all products  
- `/suppliers` → Get all suppliers  
- `/links` → Get product-supplier relationships  
- `/orders` → Get all order history  
- `/restocks` → Get restock history  

---

### 🔹 POST Endpoints
- `/add-product` → Add new product  
- `/add-supplier` → Add new supplier  
- `/link` → Link product to supplier  
- `/order` → Place an order (stock validation)  
- `/restock` → Restock a product  

---

### 🔹 DELETE Endpoints
- `/unlink` → Remove product-supplier relationship  

---

## 📊 Example API Usage

### ➤ Get Products
<img width="1017" height="662" alt="image" src="https://github.com/user-attachments/assets/ebc95666-27b2-4dae-a680-6eea6aab7610" />


### ➤ Restock Product
<img width="1016" height="658" alt="restock" src="https://github.com/user-attachments/assets/350dd697-2249-4908-8708-61c28422965f" />
<img width="1017" height="699" alt="image" src="https://github.com/user-attachments/assets/5e39d3ce-3ded-42d0-b1f2-3a4ba7fa2af3" />
<img width="1019" height="697" alt="products after restock" src="https://github.com/user-attachments/assets/81cf0763-51a3-47d3-82e4-dd6e96c34dbd" />

### ➤ Place Order (Postman)
<img width="1016" height="657" alt="order" src="https://github.com/user-attachments/assets/c28fda1f-fa61-459b-9aaf-e2cfd1dc4e3a" />
<img width="1016" height="657" alt="view orders" src="https://github.com/user-attachments/assets/435794d1-3a2e-401a-ae55-66d57a218a53" />
<img width="1017" height="694" alt="products after order" src="https://github.com/user-attachments/assets/e0060ea1-c9ac-410d-9dff-2c46e812f1bd" />


---

## 🗄️ Database Schema

- Included in: `inventory_management_system.sql`
- Visual diagram:

<img width="1359" height="728" alt="db" src="https://github.com/user-attachments/assets/cd1218dc-b49b-4353-b086-07b49269ec52" />



---

## 🛠️ Tech Stack

- Python  
- Flask  
- MySQL  
- REST API
- Docker / docker-compose
- GitHub Actions CI/CD
- Postman (testing)

---

## 🚀 Setup

1) Clone the repository

```bash
git clone https://github.com/Independent3/inventory-management-system.git
cd inventory-management-system
```

2) Create .env file based on .env.example

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password_here
DB_NAME=inventory_system
```

3) ## 🐳 Option 1 - Docker Setup (Recommended)

i) Clone the repository
   
ii) Create .env file based on .env.example
   
   - Set DB_HOST=db (not localhost)
   
4) Run with Docker:

   docker-compose up --build


5) Access the API:
   ```
      http://127.0.0.1:5000/
   ```

## Option 2 - Manual Setup
3) Install Dependencies

```bash
pip install -r requirements.txt
```

4) Setup Database
  
- Run the `inventory_management_system.sql` file in MySQL

5) Run the application

```bash
python app.py
```

6) Access the API
```text
http://127.0.0.1:5000/
```

---

## 🚨 Technical Challenges & Solutions

### 1) Data Consistency with Foreign Keys

**Challenge😤:**

Deleting products with existing relationships caused constraint errors.

**Solution💡:**

Handled relationships properly through unlinking and maintaining referential integrity.

### 2) Stock Validation Logic

**Challenge😤:**
Preventing orders that exceed available stock.

**Solution💡:**
Added backend validation to ensure quantity_sold ≤ available stock.

### 3) Schema Synchronization Issue

**Challenge😤:**
Mismatch between SQL schema and actual database (e.g., date vs date_timestamp).

**Solution💡:**
Aligned schema with application logic and verified using DESCRIBE queries.

---

## 🔧 Possible Improvements

-Authentication system (JWT)

-Frontend dashboard (React / HTML)

-API documentation (Swagger)

---

## 👤 Author

Nikolaos Vasilakopoulos

🌍 GitHub: https://github.com/Independent3

💼 LinkedIn: https://www.linkedin.com/in/nikolaos-vasilakopoulos-85714b3b0/

📧 Email: nickvasilakopoulos@rocketmail.com

