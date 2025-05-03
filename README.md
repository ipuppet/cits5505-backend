# CITS5505 Project

## Dependencies

Please use virtual environments to manage dependencies. You can use `venv` or `virtualenv` to create a virtual
environment.

To create a virtual environment, run the following command:

```bash
python3 -m venv .venv
```

To activate the virtual environment, run the following command:

- For Linux and macOS

```bash
source .venv/bin/activate
```

- For Windows

```bash
.venv\Scripts\activate
```

This project use [pip-tools](https://github.com/jazzband/pip-tools) to manage dependencies. The main file is
`requirements.in`, which lists the top-level dependencies. The `requirements.txt` file is generated from this file and
includes all the transitive dependencies.

**Do not edit `requirements.txt` directly.**

Instead, edit `requirements.in` and run the following command to generate `requirements.txt`:

```bash
pip-compile
```

### Install dependencies

Use `pip-tools` to install the dependencies. Run the following command:

```bash
pip-sync --python-executable .venv/bin/python
```

Or you can use `pip` to install the dependencies directly from the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

## Style guide

This project follows the [Black](https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html) style
guide for Python code. To format the code, run the following command:

```bash
black .
```

Alternatively, you can use VSCode with
the [Black extension](https://marketplace.visualstudio.com/items/?itemName=ms-python.black-formatter) to format the code
automatically on save.

## Project structure

> `tree -I "__pycache__|.venv|*.html|css|js|img|test_*.py"`

```plaintext
.
├── instance
│   ├── config.py
│   └── dev.sqlite
├── migrations
│   ├── alembic.ini
│   ├── env.py
│   ├── README
│   ├── script.py.mako
│   └── versions
├── README.md
├── requirements.in
├── requirements.txt
├── server
│   ├── app.py
│   ├── blueprints
│   │   ├── dashboard
│   │   │   ├── routes.py
│   │   │   └── templates
│   │   │       └── dashboard
│   │   ├── exercise
│   │   │   ├── routes.py
│   │   │   └── templates
│   │   │       └── exercise
│   │   ├── index
│   │   │   ├── routes.py
│   │   │   └── templates
│   │   │       └── index
│   │   ├── share
│   │   │   ├── routes.py
│   │   │   └── templates
│   │   │       └── share
│   │   └── user
│   │       ├── forms.py
│   │       ├── logic.py
│   │       ├── routes.py
│   │       └── templates
│   │           └── user
│   ├── config.py
│   ├── models.py
│   ├── static
│   ├── templates
│   └── utils
└── tests
    ├── conftest.py
    └── test_models
```

### Directory structure

- `instance`: This directory contains the development configuration file and the SQLite database file. The configuration
  will override the default configuration in `server/config.py`.
- `requirements.in`: This file lists the top-level dependencies for the project. It is used by `pip-tools` to generate
  the `requirements.txt` file.
- `migrations`: This directory contains the database migration files. It is created by Flask-Migrate.
- `server`: This directory contains the main application code. It includes the following contents:
    - `blueprints`: This directory contains the blueprints. Each blueprint is a separate module that can be registered
      with the main application.
        - `index`: Blueprint for the home module.
        - `user`: Blueprint for user-related module.
    - `utils`: This directory contains utility functions and decorators.
    - `static`: This directory contains static files such as CSS and JavaScript files.
    - `templates`: This directory contains the base templates for the application.
    - `app.py`: The main application file. It initializes the Flask application and registers the blueprints.
    - `config.py`: The configuration file for the application.
    - `models.py`: Models for the application.
- `tests`: This directory contains the test files for the application. It includes the following contents:
    - `conftest.py`: This file contains the test configuration and fixtures.
    - `test_models`: This directory contains the test files for the models.

*`instance` should not be included in version control.*

## Running the project

Use the following command to run the project:

```bash
flask run
```

Run with debug mode (real-time reload changes):

```bash
flask run --debug
```

## Running tests

To run the tests, use the following command:

```bash
python -m pytest
```

> In virtual environment, you need to run `python -m pytest` instead of `pytest`.

## Database migration

This project uses [Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/) to manage database migrations.

To create a new migration, use the following command:

```bash
flask db upgrade # upgrade the database to the latest version before creating a new migration
flask db migrate -m "migration message"
```

To see all the commands that are available run this command:

```bash
flask db --help
```
