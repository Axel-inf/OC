from datetime import datetime, date, timedelta

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)
from flask_sqlalchemy import SQLAlchemy

# -------------------------------------------------
# Configuration de l'application
# -------------------------------------------------
app = Flask(__name__)

# Base SQLite dans un fichier local
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///schoolplanner.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Clé secrète pour les messages flash (dev uniquement)
app.config["SECRET_KEY"] = "change-this-secret-key"

db = SQLAlchemy(app)


# -------------------------------------------------
# Modèles de la base de données
# -------------------------------------------------
class Teacher(db.Model):
    __tablename__ = "teachers"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=True)

    courses = db.relationship("Course", back_populates="teacher")

    def __repr__(self):
        return f"<Teacher {self.first_name} {self.last_name}>"


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    classe = db.Column(db.String(20), nullable=True)

    def __repr__(self):
        return f"<Student {self.first_name} {self.last_name}>"


class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)

    teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id"), nullable=True)
    teacher = db.relationship("Teacher", back_populates="courses")

    assignments = db.relationship("Assignment", back_populates="course")

    def __repr__(self):
        return f"<Course {self.name}>"


class Assignment(db.Model):
    """
    Devoir / tâche à faire.
    """

    __tablename__ = "assignments"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)

    due_date = db.Column(db.Date, nullable=False)
    estimated_minutes = db.Column(db.Integer, nullable=False, default=30)

    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    course = db.relationship("Course", back_populates="assignments")

    def __repr__(self):
        return f"<Assignment {self.title} ({self.due_date})>"


# -------------------------------------------------
# Commande CLI : initialiser la base + données de test
# -------------------------------------------------
@app.cli.command("init-db")
def init_db():
    """
    Initialisation de la base :
    - supprime les tables
    - recrée les tables
    - ajoute quelques données de test
    Utilisation : flask --app app init-db
    """
    db.drop_all()
    db.create_all()

    # Création de quelques enseignants
    t1 = Teacher(first_name="Marie", last_name="Dupont", email="marie.dupont@ecole.ch")
    t2 = Teacher(first_name="Jean", last_name="Martin", email="jean.martin@ecole.ch")

    db.session.add_all([t1, t2])
    db.session.commit()

    # Cours
    c1 = Course(name="Mathématiques", teacher=t1)
    c2 = Course(name="Français", teacher=t2)
    c3 = Course(name="Sciences", teacher=t1)

    db.session.add_all([c1, c2, c3])
    db.session.commit()

    # Devoirs d'exemple
    today = date.today()
    d1 = Assignment(
        title="Exercices équations",
        description="Exercices 3 à 7 page 42",
        due_date=today + timedelta(days=1),
        estimated_minutes=30,
        course=c1,
    )
    d2 = Assignment(
        title="Rédaction",
        description="Rédiger une lettre argumentative",
        due_date=today + timedelta(days=2),
        estimated_minutes=60,
        course=c2,
    )
    d3 = Assignment(
        title="Compte rendu d'expérience",
        description="Compléter le rapport sur l'expérience de chimie",
        due_date=today + timedelta(days=3),
        estimated_minutes=45,
        course=c3,
    )

    db.session.add_all([d1, d2, d3])
    db.session.commit()

    print("Base initialisée avec des données de test.")


# -------------------------------------------------
# Routes
# -------------------------------------------------
@app.route("/")
def index():
    """
    Page d'accueil : simple menu.
    """
    return render_template("index.html")


# ----------- CRUD des devoirs (assignments) -----------
@app.route("/devoirs")
def devoirs_list():
    """
    Liste de tous les devoirs, triés par date de rendu.
    """
    devoirs = (
        Assignment.query.join(Course)
        .order_by(Assignment.due_date.asc(), Course.name.asc())
        .all()
    )
    return render_template("devoirs_list.html", devoirs=devoirs)


@app.route("/devoirs/nouveau", methods=["GET", "POST"])
def devoirs_new():
    """
    Création d'un nouveau devoir.
    """
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        course_id = request.form.get("course_id")
        due_date_str = request.form.get("due_date")
        estimated_minutes = request.form.get("estimated_minutes", "30")

        # Validation très simple
        if not title or not due_date_str or not course_id:
            flash("Titre, date de rendu et cours sont obligatoires.", "danger")
            return redirect(url_for("devoirs_new"))

        try:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Format de date invalide.", "danger")
            return redirect(url_for("devoirs_new"))

        try:
            estimated_minutes = int(estimated_minutes)
        except ValueError:
            estimated_minutes = 30

        assignment = Assignment(
            title=title,
            description=description,
            due_date=due_date,
            estimated_minutes=estimated_minutes,
            course_id=int(course_id),
        )

        db.session.add(assignment)
        db.session.commit()

        flash("Devoir créé avec succès.", "success")
        return redirect(url_for("devoirs_list"))

    courses = Course.query.order_by(Course.name.asc()).all()
    return render_template("devoirs_form.html", courses=courses, assignment=None)


@app.route("/devoirs/<int:assignment_id>/modifier", methods=["GET", "POST"])
def devoirs_edit(assignment_id):
    """
    Modification d'un devoir existant.
    """
    assignment = Assignment.query.get_or_404(assignment_id)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        course_id = request.form.get("course_id")
        due_date_str = request.form.get("due_date")
        estimated_minutes = request.form.get("estimated_minutes", "30")

        if not title or not due_date_str or not course_id:
            flash("Titre, date de rendu et cours sont obligatoires.", "danger")
            return redirect(url_for("devoirs_edit", assignment_id=assignment.id))

        try:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Format de date invalide.", "danger")
            return redirect(url_for("devoirs_edit", assignment_id=assignment.id))

        try:
            estimated_minutes = int(estimated_minutes)
        except ValueError:
            estimated_minutes = 30

        assignment.title = title
        assignment.description = description
        assignment.course_id = int(course_id)
        assignment.due_date = due_date
        assignment.estimated_minutes = estimated_minutes

        db.session.commit()
        flash("Devoir modifié avec succès.", "success")
        return redirect(url_for("devoirs_list"))

    courses = Course.query.order_by(Course.name.asc()).all()
    return render_template("devoirs_form.html", courses=courses, assignment=assignment)


@app.route("/devoirs/<int:assignment_id>/supprimer", methods=["POST"])
def devoirs_delete(assignment_id):
    """
    Suppression d'un devoir.
    """
    assignment = Assignment.query.get_or_404(assignment_id)
    db.session.delete(assignment)
    db.session.commit()
    flash("Devoir supprimé.", "info")
    return redirect(url_for("devoirs_list"))


# ----------- Planning / charge de travail -----------
@app.route("/planning")
def planning():
    """
    Vue de la semaine : devoirs du jour J à J+6.
    Affiche la charge de travail totale par jour.
    """
    today = date.today()
    end_date = today + timedelta(days=6)

    devoirs = (
        Assignment.query.filter(
            Assignment.due_date >= today, Assignment.due_date <= end_date
        )
        .join(Course)
        .order_by(Assignment.due_date.asc(), Course.name.asc())
        .all()
    )

    # On regroupe les devoirs par date
    planning_data = {}  # {date: {"devoirs": [...], "total_minutes": int}}

    for d in devoirs:
        day = d.due_date
        if day not in planning_data:
            planning_data[day] = {"devoirs": [], "total_minutes": 0}
        planning_data[day]["devoirs"].append(d)
        planning_data[day]["total_minutes"] += d.estimated_minutes

    # Liste des jours de la semaine courante
    days = [today + timedelta(days=i) for i in range(7)]

    return render_template(
        "planning.html",
        days=days,
        planning_data=planning_data,
    )


# -------------------------------------------------
# Lancement en mode script (optionnel)
# -------------------------------------------------
if __name__ == "__main__":
    # Pour lancer en direct : python app.py
    app.run(debug=True)
