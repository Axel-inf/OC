from flask import render_template, request, redirect, url_for, flash
from datetime import datetime, date, timedelta

from .models import db, Teacher, Student, Course, Assignment

def register_routes(app):

    @app.route("/")
    def index():
        return render_template("index.html")

    # -------- DEVOIRS : LISTE ----------
    @app.route("/devoirs")
    def devoirs_list():
        devoirs = Assignment.query.order_by(Assignment.due_date.asc()).all()
        return render_template("devoirs_list.html", devoirs=devoirs)

    # -------- DEVOIRS : NOUVEAU ----------
    @app.route("/devoirs/nouveau", methods=["GET", "POST"])
    def devoirs_new():
        if request.method == "POST":
            title = request.form["title"]
            description = request.form["description"]
            course_id = request.form["course_id"]
            due_date = datetime.strptime(request.form["due_date"], "%Y-%m-%d").date()
            estimated_minutes = int(request.form["estimated_minutes"])

            a = Assignment(
                title=title,
                description=description,
                course_id=course_id,
                due_date=due_date,
                estimated_minutes=estimated_minutes,
            )
            db.session.add(a)
            db.session.commit()
            flash("Devoir ajouté.", "success")
            return redirect(url_for("devoirs_list"))

        courses = Course.query.order_by(Course.name.asc()).all()
        return render_template("devoirs_form.html", courses=courses, assignment=None)

    # -------- DEVOIRS : MODIFIER ----------
    @app.route("/devoirs/<int:id>/modifier", methods=["GET", "POST"])
    def devoirs_edit(id):
        a = Assignment.query.get_or_404(id)

        if request.method == "POST":
            a.title = request.form["title"]
            a.description = request.form["description"]
            a.course_id = request.form["course_id"]
            a.due_date = datetime.strptime(request.form["due_date"], "%Y-%m-%d").date()
            a.estimated_minutes = int(request.form["estimated_minutes"])
            db.session.commit()
            flash("Devoir modifié.", "success")
            return redirect(url_for("devoirs_list"))

        courses = Course.query.order_by(Course.name.asc()).all()
        return render_template("devoirs_form.html", courses=courses, assignment=a)

    # -------- DEVOIRS : SUPPRIMER ----------
    @app.route("/devoirs/<int:id>/supprimer", methods=["POST"])
    def devoirs_delete(id):
        a = Assignment.query.get_or_404(id)
        db.session.delete(a)
        db.session.commit()
        flash("Devoir supprimé.", "info")
        return redirect(url_for("devoirs_list"))

    # -------- VUE PLANNING ----------
    @app.route("/planning")
    def planning():
        today = date.today()
        end = today + timedelta(days=6)

        devoirs = Assignment.query.filter(
            Assignment.due_date >= today,
            Assignment.due_date <= end
        ).order_by(Assignment.due_date.asc()).all()

        planning_data = {}  # dict : date -> liste + total

        for d in devoirs:
            planning_data.setdefault(d.due_date, {"items": [], "total": 0})
            planning_data[d.due_date]["items"].append(d)
            planning_data[d.due_date]["total"] += d.estimated_minutes

        days = [today + timedelta(days=i) for i in range(7)]

        return render_template("planning.html", days=days, planning_data=planning_data)
