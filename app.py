from flask import Flask, render_template

app = Flask(__name__)

# This route will just serve the main HTML page.
# The email generation logic is handled by JavaScript on the client-side (in index.html).
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

if __name__ == '__main__':
    # Run the Flask development server.
    # debug=True allows for automatic reloading on code changes and provides detailed error messages.
    # For production environments, set debug=False.
    app.run(debug=True)
