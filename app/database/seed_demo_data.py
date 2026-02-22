from database.database import get_db
from database.models import Utilisateur, Enseignant, Eleve, RoleEnum
from utils.auth import hash_password


def seed_demo_school_data() -> None:
    db = get_db()
    try:
        teacher_email = 'prof.demo@college.ch'
        student_email = 'eleve.demo@college.ch'
        second_teacher_email = 'prof2.demo@college.ch'
        second_student_email = 'eleve2.demo@college.ch'

        teacher_user = db.query(Utilisateur).filter(Utilisateur.email == teacher_email).first()
        if teacher_user is None:
            teacher_user = Utilisateur(
                email=teacher_email,
                mot_de_passe=hash_password('ProfDemo123!'),
                nom='Martin',
                prenom='Claire',
                role=RoleEnum.ENSEIGNANT,
            )
            db.add(teacher_user)
            db.flush()

            db.add(Enseignant(
                utilisateur_id=teacher_user.id,
                branches='Mathématiques,Anglais,OS Physique et application des mathématiques,OC Informatique,Basic English',
                classes='2GY1,2GY2,3GY1',
                os='Physique et application des mathématiques',
                oc='Informatique',
                basic_english=False,
                bilingue=False,
            ))
        else:
            teacher_profile = db.query(Enseignant).filter(Enseignant.utilisateur_id == teacher_user.id).first()
            if teacher_profile is not None:
                teacher_profile.branches = 'Mathématiques,Anglais,OS Physique et application des mathématiques,OC Informatique,Basic English'
                teacher_profile.classes = '2GY1,2GY2,3GY1'

        student_user = db.query(Utilisateur).filter(Utilisateur.email == student_email).first()
        if student_user is None:
            student_user = Utilisateur(
                email=student_email,
                mot_de_passe=hash_password('EleveDemo123!'),
                nom='Dupont',
                prenom='Lucas',
                role=RoleEnum.ELEVE,
            )
            db.add(student_user)
            db.flush()

            db.add(Eleve(
                utilisateur_id=student_user.id,
                classe='2GY1',
                niveau_maths='Mathématiques standards',
                langue1='Français',
                langue2='Anglais',
                langue3='Allemand',
                os='Physique et application des mathématiques',
                oc='Physique',
                basic_english=False,
                bilingue=False,
            ))

        second_teacher_user = db.query(Utilisateur).filter(Utilisateur.email == second_teacher_email).first()
        if second_teacher_user is None:
            second_teacher_user = Utilisateur(
                email=second_teacher_email,
                mot_de_passe=hash_password('Prof2Demo123!'),
                nom='Rochat',
                prenom='Nadia',
                role=RoleEnum.ENSEIGNANT,
            )
            db.add(second_teacher_user)
            db.flush()

            db.add(Enseignant(
                utilisateur_id=second_teacher_user.id,
                branches='Français,Allemand,OS Italien,OC Histoire,Basic English',
                classes='3GY1,3GY2',
                os='Français',
                oc='Histoire',
                basic_english=False,
                bilingue=False,
            ))
        else:
            second_teacher_profile = db.query(Enseignant).filter(Enseignant.utilisateur_id == second_teacher_user.id).first()
            if second_teacher_profile is not None:
                second_teacher_profile.branches = 'Français,Allemand,OS Italien,OC Histoire,Basic English'
                second_teacher_profile.classes = '3GY1,3GY2'

        second_student_user = db.query(Utilisateur).filter(Utilisateur.email == second_student_email).first()
        if second_student_user is None:
            second_student_user = Utilisateur(
                email=second_student_email,
                mot_de_passe=hash_password('Eleve2Demo123!'),
                nom='Rey',
                prenom='Sofia',
                role=RoleEnum.ELEVE,
            )
            db.add(second_student_user)
            db.flush()

            db.add(Eleve(
                utilisateur_id=second_student_user.id,
                classe='3GY1',
                niveau_maths='Mathématiques renforcées',
                langue1='Français',
                langue2='Allemand',
                langue3='Anglais',
                os='Biologie et chimie',
                oc='Géographie',
                basic_english=False,
                bilingue=False,
            ))

        db.commit()
    finally:
        db.close()
