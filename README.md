# CITS5505 Project

## Ddependencies

Please use virtual environments to manage dependencies. You can use `venv` or `virtualenv` to create a virtual environment.

To create a virtual environment, run the following command:

```bash
python3 -m venv venv
```

To activate the virtual environment, run the following command:

- For Linux and macOS

```bash
source venv/bin/activate
```

- For Windows

```bash
venv\Scripts\activate
```

This project use `pip-tools` to manage dependencies. The main file is `requirements.in`, which lists the top-level dependencies. The `requirements.txt` file is generated from this file and includes all the transitive dependencies.

**Do not edit `requirements.txt` directly.**

Instead, edit `requirements.in` and run the following command to generate `requirements.txt`:

```bash
pip-compile
```

### Install dependencies

Use `pip-tools` to install the dependencies. Run the following command:

```bash
pip-sync
```

Or you can use `pip` to install the dependencies directly from the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

## Style guide

This project follows the [Black](https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html) style guide for Python code. To format the code, run the following command:

```bash
black .
```

Alternatively, you can use VSCode with the [Black extension](https://marketplace.visualstudio.com/items/?itemName=ms-python.black-formatter) to format the code automatically on save.

## Project structure

> `tree -I "__pycache__|*.pyc|venv|.venv"`

```plaintext
.
├── instance
│   ├── config.py
│   └── db.sqlite
├── README.md
├── requirements.in
├── requirements.txt
└── server
    ├── app.py
    ├── blueprints
    │   ├── index
    │   │   ├── routes.py
    │   │   └── templates
    │   │       └── index.html
    │   └── user
    │       ├── forms.py
    │       ├── routes.py
    │       └── templates
    │           ├── login.html
    │           └── register.html
    ├── config.py
    ├── models.py
    └── utils
        └── decorators.py
```

### Directory structure

- `instance`: This directory contains the development configuration file and the SQLite database file. The configuration will override the default configuration in `server/config.py`.
- `requirements.in`: This file lists the top-level dependencies for the project. It is used by `pip-tools` to generate the `requirements.txt` file.
- `server`: This directory contains the main application code. It includes the following contents:
  - `blueprints`: This directory contains the blueprints. Each blueprint is a separate module that can be registered with the main application.
    - `index`: Blueprint for the index page.
    - `user`: Blueprint for user-related routes.
  - `utils`: This directory contains utility functions and decorators.
  - `app.py`: The main application file. It initializes the Flask application and registers the blueprints.
  - `config.py`: The configuration file for the application.
  - `models.py`: Models for the application.

*`instance` should not be included in version control.*

## Running the project

Use the following command to run the project:

```bash
flask --app server.app run
```

Run with debug mode:

```bash
flask --app server.app run --debug
```
