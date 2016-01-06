# A simple listener server. Does Nothing.
from flask import Flask

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def start_server(path):
    return 'Copy the url above.. this server will close soon'

if __name__ == '__main__':
    app.run(port='8888')