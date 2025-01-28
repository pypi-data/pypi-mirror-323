PyAwaish
===========

**PyAwaish** is a Flask-based Python framework that simplifies the development of MySQL-powered web applications. It provides a streamlined interface for connecting to a MySQL database, rendering templates, and executing queries dynamically via RESTful APIs.

Features
--------
- **Dynamic MySQL Configuration**: Configure MySQL database settings at runtime via a web interface.
- **Template Rendering**: Built-in support for rendering templates stored in the `templates` folder.
- **Query Execution API**: Execute MySQL queries dynamically through POST requests.
- **CRUD Operations**: Perform create, read, update, and delete operations programmatically.
- **RESTful Design**: Leverage Flask to expose endpoints for database interactions.
- **Environment Configuration**: Load sensitive credentials securely using environment variables.

Badges
------

.. image:: https://badge.fury.io/py/PyAwaish.svg
    :target: https://pypi.org/project/PyAwaish/

.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
    :target: https://opensource.org/licenses/MIT


Endpoints
---------
1. **`/`**: Displays the MySQL configuration page.
2. **`/home`**: Displays the home page.
3. **`/config_mysql`**: Accepts a POST request to configure MySQL connection details dynamically.
4. **`/execute_query`**: Accepts a POST request to execute MySQL queries or perform operations (e.g., insert, delete, update).

Installation
------------
1. Clone the repository:

   .. code-block:: bash

       git clone https://github.com/abuawaish/CRUD_App.git
       cd CRUD_App

2. Install the required dependencies:

   .. code-block:: bash

       pip install -r requirements.txt

3. Install the package:

   .. code-block:: bash

       pip install PyAwaish

4. Set environment variables for database configuration:

   .. code-block:: bash

       export MYSQL_HOST=localhost
       export MYSQL_USER=root
       export MYSQL_PASSWORD=your password
       export MYSQL_DB=mydatabase
       export SECRET_KEY=your_secret_key


Usage
-----

**Running the Application**

To start the MysqlWebApp server, instantiate the `MysqlApplication` class and call its `execute` method. For example:

.. code-block:: python

    from PyAwaish.MysqlApplication import MysqlApplication

    if __name__ == "__main__":
        app = MysqlApplication()
        app.execute()

**This will:**

- Start a Flask server on `http://0.0.0.0:5001`.
- Serve endpoints for configuring and interacting with the MySQL database.


**Configuring MySQL**

1. Navigate to the root endpoint (`http://localhost:5001/`) to access the configuration page.
2. Enter the database details (host, username, password, database name) and click "Save".
3. Upon successful configuration, you will be redirected to the home page.

**Executing Queries**

Use the `/execute_query` endpoint to run SQL queries or perform operations. Example request:

- **POST Request Example**:

  .. code-block:: json

      {
          "operation": "insert",
          "table_name": "users",
          "columns": "name, email",
          "values": "'John Doe', 'john@example.com'"
      }

- **Supported Operations**:
  - `insert`: Insert data into a table.
  - `delete`: Delete data from a table with a condition.
  - `update`: Update data in a table with a condition.
  - `fetch_data`: Fetch all data from a table.
  - `show_tables`: List all tables in the database.

Dependencies
------------
The application requires the following dependencies (listed in `requirements.txt`):

- Flask: Web framework.
- Flask-MySQLdb: MySQL connector for Flask.

To install them, run:

.. code-block:: bash

    pip install -r requirements.txt

Environment Variables
---------------------
- **MYSQL_HOST**: MySQL server hostname (default: `localhost`).
- **MYSQL_USER**: MySQL username (default: `root`).
- **MYSQL_PASSWORD**: MySQL password.
- **MYSQL_DB**: Default MySQL database name.
- **SECRET_KEY**: Flask secret key for session security.

Changelog
---------
Refer to `CHANGELOG.txt` for the complete version history of the project.

License
-------
This project is licensed under the MIT License. See `LICENSE.txt` for full details.

Contact
-------
For questions or feedback, contact:

- Email: abuawaish7@gmail.com
- GitHub: https://github.com/abuawaish/CRUD_App
