from flask import url_for
from myapp import app
app.config['SERVER_NAME'] = 'localhost:5000'

if __name__ == "__main__":
    app.run(debug=True)