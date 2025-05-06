from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import httpx

app = Flask(__name__, static_url_path='/static')
app.secret_key = os.environ.get("SECRET_KEY", "devsecret")

AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL", "http://auth-service/auth")

@app.route("/")
def index():
    user = session.get("user")
    return render_template("index.html", user=user)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        try:
            resp = httpx.post(f"{AUTH_SERVICE_URL}/signin", json={"email": email, "password": password}, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                session["user"] = {"email": email, "token": data["access_token"]}
                return redirect(url_for("index"))
            else:
                flash("Invalid credentials", "danger")
        except Exception:
            flash("Auth service unavailable", "danger")
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        full_name = request.form["full_name"]
        password = request.form["password"]
        try:
            resp = httpx.post(f"{AUTH_SERVICE_URL}/signup", json={
                "username": username,
                "email": email,
                "full_name": full_name,
                "password": password
            }, timeout=5)
            if resp.status_code == 201:
                flash("Signup successful. Please log in.", "success")
                return redirect(url_for("login"))
            else:
                flash(resp.json().get("detail", "Signup failed"), "danger")
        except Exception:
            flash("Auth service unavailable", "danger")
    return render_template("signup.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("index"))

if __name__ == "__main__":
    # port muss mit containerPort in Deployment übereinstimmen
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))