from setuptools import setup, find_packages

setup(
    name="sport-track",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "flask",
        "flask-sqlalchemy",
        "flask-migrate",
        "flask-login",
        "flask-wtf",
        "wtforms",
        "wtforms-json",
        "pytest",
    ],
) 