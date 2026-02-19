from flask import Flask, render_template, request, redirect, session, url_for
from db import get_db_connection

app = Flask(__name__)
app.secret_key = "supersecretkey"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (name,email,password,role) VALUES (%s,%s,%s,%s)",
                    (name, email, password, role))
        conn.commit()
        cur.close()
        conn.close()

        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            session["role"] = user["role"]
            session["name"] = user["name"]

            if user["role"] == "donor":
                return redirect("/donor_dashboard")
            else:
                return redirect("/request_blood")

        return "Invalid login"

    return render_template("login.html")


@app.route("/donor_dashboard", methods=["GET", "POST"])
def donor_dashboard():
    if "user_id" not in session or session["role"] != "donor":
        return redirect("/login")

    user_id = session["user_id"]

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM donors WHERE user_id=%s", (user_id,))
    donor = cur.fetchone()

    if request.method == "POST":
        blood_group = request.form["blood_group"]
        city = request.form["city"]
        phone = request.form["phone"]
        last_donation = request.form["last_donation"]
        available = request.form.get("available")

        available = True if available == "on" else False

        if donor:
            cur.execute("""
                UPDATE donors SET blood_group=%s, city=%s, phone=%s,
                last_donation=%s, available=%s WHERE user_id=%s
            """, (blood_group, city, phone, last_donation, available, user_id))
        else:
            cur.execute("""
                INSERT INTO donors (user_id,blood_group,city,phone,last_donation,available)
                VALUES (%s,%s,%s,%s,%s,%s)
            """, (user_id, blood_group, city, phone, last_donation, available))

        conn.commit()

    cur.execute("SELECT * FROM donors WHERE user_id=%s", (user_id,))
    donor = cur.fetchone()

    cur.close()
    conn.close()

    return render_template("donor_dashboard.html", donor=donor)


@app.route("/request_blood", methods=["GET", "POST"])
def request_blood():
    if request.method == "POST":
        receiver_name = request.form["receiver_name"]
        blood_group = request.form["blood_group"]
        city = request.form["city"]
        units = request.form["units"]
        hospital = request.form["hospital"]
        phone = request.form["phone"]

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO requests (receiver_name,blood_group,city,units,hospital,phone)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (receiver_name, blood_group, city, units, hospital, phone))
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("donors_list", city=city, blood_group=blood_group))

    return render_template("request_blood.html")


@app.route("/donors_list")
def donors_list():
    city = request.args.get("city")
    blood_group = request.args.get("blood_group")

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT * FROM donors
        WHERE city=%s AND blood_group=%s AND available=TRUE
    """, (city, blood_group))

    donors = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("donors_list.html", donors=donors, city=city, blood_group=blood_group)

@app.route("/donor_requests")
def donor_requests():
    if "user_id" not in session or session["role"] != "donor":
        return redirect("/login")

    user_id = session["user_id"]

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    # Get donor city
    cur.execute("SELECT city FROM donors WHERE user_id=%s", (user_id,))
    donor = cur.fetchone()

    if not donor:
        cur.close()
        conn.close()
        return "Update your donor profile first."

    city = donor["city"]

    # Get requests from same city
    cur.execute("SELECT * FROM requests WHERE city=%s ORDER BY created_at DESC", (city,))
    requests_list = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("donor_requests.html", requests_list=requests_list, city=city)

@app.route("/search_donors", methods=["GET", "POST"])
def search_donors():
    donors = []
    city = ""
    blood_group = ""

    if request.method == "POST":
        city = request.form["city"]
        blood_group = request.form["blood_group"]

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute("""
            SELECT * FROM donors
            WHERE city=%s AND blood_group=%s AND available=TRUE
        """, (city, blood_group))

        donors = cur.fetchall()
        cur.close()
        conn.close()

    return render_template("search_donors.html", donors=donors, city=city, blood_group=blood_group)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)