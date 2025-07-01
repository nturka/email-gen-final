# This comment is to trigger a fresh Render deployment.
from flask import Flask, render_template

app = Flask(__name__)

# This route will just serve the main HTML page.
# The email generation logic is handled by JavaScript on the client-side (in index.html).
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# IMPORTANT: Remove the app.run() block when deploying with Gunicorn or other WSGI servers.
# Gunicorn will directly import and run the 'app' Flask instance.
# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, render_template

app = Flask(__name__)

# This route will just serve the main HTML page.
# The email generation logic is handled by JavaScript on the client-side (in index.html).
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# IMPORTANT: Remove the app.run() block when deploying with Gunicorn or other WSGI servers.
# Gunicorn will directly import and run the 'app' Flask instance.
# if __name__ == '__main__':
#     app.run(debug=True)
