# Inventory Management System

This is a Flask-based web application for managing an inventory system, including purchasing and sales operations. It supports tracking items, managing purchases and sales, and generating reports. It also includes a basic balance management feature for the company.

## Features

- **Item Management:** Add, edit, and view items in the inventory.
- **Purchasing:** Add items to the purchase cart, update the cart, and complete the purchase process. Tracks buying price and selling price.
- **Sales:** Add items to the sales cart, update the cart, and complete the sale process. Tracks quantity and selling price.
- **Balance Management:** Update the company's cash balance used for purchases.
- **Reports:** View detailed reports of purchases and sales.
- **Session Management:** Track purchase and sale carts in user sessions.

## Requirements

- Python 3.x
- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-Bcrypt
- Flask-WTF
- WTForms

### Installing Dependencies

To set up this project on your local machine, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/Sumith-2004/Flask_Web_Application.git
    cd Flask_Web_Application
    ```

2. Create a virtual environment:
    ```bash
    python -m venv venv
    ```

3. Activate the virtual environment:
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

4. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

5. Set up the database:
    ```bash
    flask db init
    flask db migrate
    flask db upgrade
    ```

## Running the Application

To run the application locally, execute:

```bash
flask run
