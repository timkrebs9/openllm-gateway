from flask import Flask, render_template
import os

app = Flask(__name__, static_url_path='/static')

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    # port muss mit containerPort in Deployment übereinstimmen
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))