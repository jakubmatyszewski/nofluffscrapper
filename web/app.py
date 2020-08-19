from flask import Flask
from views import bp

app = Flask(__name__)
app.register_blueprint(bp)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
