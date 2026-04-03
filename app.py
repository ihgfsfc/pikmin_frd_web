from flask import Flask, render_template, request, redirect, url_for, flash, session
from dotenv import load_dotenv
from supabase import create_client
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)


load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase = create_client(url, key)

players = []

@app.route("/", methods=["GET", "POST"])
def home():

    lang = session.get("lang", "zh")


    if request.method == "POST":
        name = request.form["name"]
        code = request.form["code"]
        location = request.form["location"]
        note = request.form["note"]

        if not name or not code or not location or not note:
            flash("⚠️ Please fill in all fields!", "danger")
            return redirect(url_for("home"))

        if len(name) > 30 or len(code) > 30 or len(location) > 30:
            flash("Text fields cannot exceed 30 characters!", "danger")
            return redirect("/")

        if len(note) > 150:
            flash("Note cannot exceed 150 characters!", "danger")
            return redirect("/")

        #check if frd code exists
        existing = supabase.table("players").select("*").eq("code", code).execute()

        if existing.data:
            flash(f"⚠️ Friend Code {code} already exists!", "danger")
            return redirect(url_for("home"))

        supabase.table("players").insert({
            "name": name,
            "code": code,
            "location": location,
            "note": note
        }).execute()

        flash("🎉 Player successfully added!", "success")
        return  redirect(url_for("show_player"))
    
    #count the total players
    response = supabase.table("players").select("id", count="exact").execute()

    player_count = response.count


    return render_template("form.html", lang=lang, player_count=player_count)


@app.route("/lang/<language>")
def set_language(language):
    session["lang"] = language
    return redirect(request.referrer or url_for("home"))

@app.route("/players")
def show_player():
    lang = session.get("lang", "zh")

    search = request.args.get("search")

    query = supabase.table("players").select("*").order("created_at", desc=True)

    if search:
        query = query.or_(
            f"name.ilike.%{search}%,code.ilike.%{search}%,location.ilike.%{search}%,note.ilike.%{search}%"
        )

    response = query.execute()

    players = response.data

    return render_template("player.html", players=players, lang=lang)


if __name__ == "__main__":
    app.run(debug=True)