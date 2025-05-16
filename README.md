# CITS5505 Project: Sport Tracker

This is our web application project for CITS5505. The application is built using Flask, SQLite, and various front-end
technologies. It is designed to be user-friendly and visually appealing, with a focus on data visualization and user
engagement.

## Group Members

- **Name:** Samuel Wei  
  **ID:** 24115652  
  **GitHub Username:** ipuppet

- **Name:** Brandon Ge  
  **ID:** 23813666  
  **GitHub Username:** bag026

- **Name:** Xiaoqin Fan  
  **ID:** 24055569  
  **GitHub Username:** Fan-Xiaoqin

- **Name:** Xiaotong Yin  
  **ID:** 24491566  
  **GitHub Username:** wisermonk

## Project Overview

Our project is a modern, sport tracker web application built with Flask and SQLite. It helps users log workouts, track
hydration, monitor progress, and set personal goals—all within a friendly, interactive dashboard. Unlike typical fitness
apps, our platform emphasizes social features, data visualization, and user motivation.

## Purpose and Design

**Sport Tracker** is a comprehensive web application designed to help users monitor, analyze, and improve their fitness journey in a modern, engaging, and social environment. The application is built with a focus on usability, data visualization, and motivation, making it suitable for both casual users and fitness enthusiasts.

### Purpose

- **Personal Fitness Management:** Users can log workouts, track body measurements (such as weight and BMI), monitor hydration, and set personalized fitness goals.
- **Progress Visualization:** The app provides clear, interactive charts and dashboards to help users visualize their progress over time, making it easier to stay motivated and identify trends.
- **Social Engagement:** Users can share achievements and progress with friends, fostering a sense of community and accountability.
- **Motivation and Guidance:** The platform offers motivational messages, weather-based workout suggestions, and achievement badges to keep users engaged and inspired.

### Design

- **User-Centered Interface:** The UI is built with Bootstrap for responsiveness and accessibility, ensuring a seamless experience across devices.
- **Modular Architecture:** The backend uses Flask blueprints to organize features into logical modules (dashboard, user, browse, share, etc.), making the codebase maintainable and extensible.
- **Data Visualization:** Chart.js is used to present workout data, calorie intake, weight trends, and goal progress in an intuitive and visually appealing way.
- **Security and Privacy:** User data is protected with authentication, and sharing features are designed to be private and secure.
- **Test-Driven Development:** The project includes comprehensive unit and system tests to ensure reliability and facilitate future development.

### Use

1. **Registration & Login:** Users create an account and log in to access personalized features.
2. **Dashboard:** The main dashboard displays key metrics, recent activity, hydration status, and motivational content.
3. **Workout & Measurement Logging:** Users can add workouts, body measurements, and hydration data through simple forms.
4. **Goal Setting:** Users set and track progress toward custom fitness goals, with real-time feedback and visual progress bars.
5. **Social Features:** Users can connect with friends, share selected data, and celebrate achievements together.
6. **Data Insights:** Interactive charts and summaries help users understand their habits and progress, supporting informed decision-making.
7. **Private Sharing:** Easily share your dashboard or achievements with others via a secure, private link.

**Sport Tracker** aims to make fitness tracking enjoyable, insightful, and socially rewarding, supporting users on their journey to better health.

## What Makes This Project Different?

- **Social Fitness Tracking:** Users can share progress, achievements, and workout data with friends for motivation and
  accountability.
- **Personalized Dashboard:** Visualize calories burned, calorie intake, weight trends, BMI, hydration, and more—all in
  one place.
- **Motivational Features:** Dynamic motivational messages and weather-based workout suggestions keep users engaged and
  inspired.
- **Goal Management:** Set, track, and visualize progress toward custom fitness goals with real-time feedback.
- **Hydration Tracker:** Simple, interactive water intake tracker with motivational feedback.
- **Modern UI:** Responsive, accessible interface using Bootstrap and Chart.js for a smooth user experience.
- **Easy Setup:** Designed for quick local deployment with clear instructions and minimal dependencies.
- **Test-Driven Development:** Comprehensive unit tests ensure reliability and maintainability.

## Project Structure

```plaintext
.
├── instance
│   ├── config.py
│   └── dev.sqlite
├── migrations
├── README.md
├── requirements.in
├── requirements.txt
├── server
│   ├── app.py
│   ├── blueprints
│   ├── config.py
│   ├── models.py
│   ├── static
│   ├── templates
│   └── utils
└── tests
    ├── conftest.py
    └── test_models
```

### Directory Structure

- `instance`: This directory contains the development configuration file and the SQLite database file. The configuration
  will override the default configuration in `server/config.py`.
- `requirements.in`: This file lists the top-level dependencies for the project. It is used by `pip-tools` to generate
  the `requirements.txt` file.
- `migrations`: This directory contains the database migration files. It is created by Flask-Migrate.
- `server`: This directory contains the main application code. It includes the following contents:
    - `blueprints`: This directory contains the blueprints. Each blueprint is a separate module that can be registered
      with the main application.
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

## Style Guide

This project follows the [Black](https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html) style
guide for Python code. To format the code, run the following command:

```bash
black .
```

Alternatively, you can use VSCode with
the [Black extension](https://marketplace.visualstudio.com/items/?itemName=ms-python.black-formatter) to format the code
automatically on save.

## Prerequisites

Please use virtual environments to manage dependencies. You can use `venv` to create a virtual environment.

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

### Install Dependencies

Use `pip-tools` to install the dependencies. Run the following command:

```bash
pip-sync --python-executable .venv/bin/python
```

Or you can use `pip` to install the dependencies directly from the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

## How to Run the Project

This project needs to set some environment variables to run. You can set them in the terminal or in the
`instance/config.py` file.

### Environment Variables

- `SECRET_KEY`: A secret key for the application. It is used to sign cookies and protect against CSRF attacks.
- `EMAIL_VERIFY_SALT`: A salt for the password hashing. It is used to hash the passwords.
- `MAIL_USERNAME`: The email address of the sender. It is used to send emails.
- `MAIL_PASSWORD`: The password of the sender's email address. It is used to send emails.

*Command to set environment variables in Linux and macOS:*

```bash
export SECRET_KEY="your_secret_key"
export EMAIL_VERIFY_SALT="your_email_verify_salt"
export MAIL_USERNAME="your_email_address"
export MAIL_PASSWORD="your_email_password"
```

### Run the Project

Initialize the database and create the tables. You can do this by running the following command:

```bash
flask init-db
```

Use the following command to run the project:

```bash
flask run
```

Run with debug mode (real-time reload changes):

```bash
flask run --debug
```

If there are any database migrations, you need to run the following command to upgrade the database:

```bash
flask db upgrade
```

## Testing

To run the tests, use the following command:

```bash
python -m pytest
```

> In virtual environment, you need to run `python -m pytest` instead of `pytest`.

## Database Migration

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
