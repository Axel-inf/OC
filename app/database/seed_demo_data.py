from datetime import date, timedelta
from database.database import get_db
from database.models import Utilisateur, Enseignant, Eleve, RoleEnum, CalendarEvent
from utils.auth import hash_password


def clear_database() -> None:
    """Clear all data from the database."""
    db = get_db()
    try:
        db.query(CalendarEvent).delete()
        db.query(Enseignant).delete()
        db.query(Eleve).delete()
        db.query(Utilisateur).delete()
        db.commit()
    finally:
        db.close()


def seed_demo_school_data() -> None:
    """Seed the database with test data:
    - 10 teachers: 0-9 (email: 0@example.com, password: 12345678)
    - 26 students: a-z (email: a@example.com, password: 12345678)
    - Calendar events with various dates
    """
    # Clear existing data first
    clear_database()
    
    db = get_db()
    try:
        password = hash_password('12345678')
        
        # Define classes and their assignments
        classes_list = ['1gy1', '1gy2', '2gy1', '2gy2', '3gy1', '3gy2']
        
        # Branches for teachers
        branches_options = [
            'Mathématiques,Physique,OS Physique et application des mathématiques',
            'Français,Allemand,OC Histoire',
            'Anglais,Basic English,OC Informatique',
            'Biologie,Chimie,OS Biologie et chimie',
            'Histoire,Géographie,OC Géographie',
            'Économie et droit,OC Économie et droit',
            'Philosophie,OS Philosophie et psychologie',
            'Arts visuels,Musique,OC Arts visuels',
            'Éducation physique,OC Sport',
            'Italien,Latin,OS Italien',
        ]
        
        # Create 10 teachers (0-9)
        teachers = []
        for i in range(10):
            teacher_user = Utilisateur(
                email=f'{i}@example.com',
                mot_de_passe=password,
                nom=str(i),
                prenom=str(i),
                role=RoleEnum.ENSEIGNANT,
            )
            db.add(teacher_user)
            db.flush()
            
            # Assign 2-3 classes per teacher
            teacher_classes = classes_list[i % 3:(i % 3) + 2]
            if i >= 5:
                teacher_classes = classes_list[(i % 3) + 1:(i % 3) + 3]
            
            teacher_profile = Enseignant(
                utilisateur_id=teacher_user.id,
                branches=branches_options[i],
                classes=','.join(teacher_classes),
                os='Physique et application des mathématiques' if i % 3 == 0 else 'Biologie et chimie' if i % 3 == 1 else 'Italien',
                oc='Informatique' if i % 2 == 0 else 'Histoire',
                basic_english=i % 4 == 0,
                bilingue=i % 5 == 0,
            )
            db.add(teacher_profile)
            teachers.append((teacher_user, teacher_profile, teacher_classes))
        
        # Create 26 students (a-z)
        students = []
        for i, letter in enumerate('abcdefghijklmnopqrstuvwxyz'):
            student_user = Utilisateur(
                email=f'{letter}@example.com',
                mot_de_passe=password,
                nom=letter,
                prenom=letter,
                role=RoleEnum.ELEVE,
            )
            db.add(student_user)
            db.flush()
            
            # Assign student to a class (distribute across classes)
            student_class = classes_list[i % len(classes_list)]
            
            student_profile = Eleve(
                utilisateur_id=student_user.id,
                classe=student_class,
                niveau_maths='Mathématiques standards' if i % 2 == 0 else 'Mathématiques renforcées',
                langue1='Français',
                langue2='Anglais' if i % 2 == 0 else 'Allemand',
                langue3='Allemand' if i % 2 == 0 else 'Italien',
                os='Physique et application des mathématiques' if i % 4 == 0 else 'Biologie et chimie' if i % 4 == 1 else 'Italien' if i % 4 == 2 else 'Philosophie et psychologie',
                oc='Informatique' if i % 3 == 0 else 'Histoire' if i % 3 == 1 else 'Géographie',
                basic_english=i % 5 == 0,
                bilingue=i % 7 == 0,
            )
            db.add(student_profile)
            students.append((student_user, student_profile))
        
        db.commit()
        
        # Create calendar events
        today = date.today()
        
        # Event definitions with varied dates
        events_data = [
            # Past events (already done)
            ('devoir', 'Mathématiques', 'Exercices chapitre 3', today - timedelta(days=14), '1 heure', '45 minutes'),
            ('examen', 'Français', 'Dissertation', today - timedelta(days=10), '3 heures', '4 heures'),
            ('devoir', 'Anglais', 'Essay writing', today - timedelta(days=7), '2 heures', '2h30'),
            ('examen', 'Physique', 'Mécanique', today - timedelta(days=5), '2 heures', '3 heures'),
            ('devoir', 'Chimie', 'Labo report', today - timedelta(days=3), '1h30', '2 heures'),
            
            # Today
            ('devoir', 'Histoire', 'Résumé chapitre 12', today, '1 heure', '0 minute'),
            ('examen', 'Biologie', 'Cellules', today, '2 heures', '0 minute'),
            
            # Future events (upcoming)
            ('devoir', 'Allemand', 'Übungen Seite 45', today + timedelta(days=1), '30 minutes', '0 minute'),
            ('examen', 'Mathématiques', 'Intégrales', today + timedelta(days=3), '2 heures', '0 minute'),
            ('devoir', 'Philosophie', 'Lecture Kant', today + timedelta(days=5), '4 heures', '0 minute'),
            ('examen', 'Géographie', 'Climatologie', today + timedelta(days=7), '1h30', '0 minute'),
            ('devoir', 'Économie et droit', 'Analyse de cas', today + timedelta(days=10), '2 heures', '0 minute'),
            ('examen', 'Italien', 'Vocabolario', today + timedelta(days=14), '1 heure', '0 minute'),
            ('devoir', 'Arts visuels', 'Projet créatif', today + timedelta(days=21), '5 heures', '0 minute'),
            ('examen', 'Musique', 'Solfège', today + timedelta(days=30), '1 heure', '0 minute'),
        ]
        
        # Get fresh db session for events
        db = get_db()
        
        # For each teacher, create events that link to their students
        all_teachers = db.query(Utilisateur).filter(Utilisateur.role == RoleEnum.ENSEIGNANT).all()
        all_students = db.query(Utilisateur).filter(Utilisateur.role == RoleEnum.ELEVE).all()
        
        for teacher in all_teachers:
            teacher_profile = db.query(Enseignant).filter(Enseignant.utilisateur_id == teacher.id).first()
            if not teacher_profile:
                continue
                
            teacher_classes = teacher_profile.classes.split(',') if teacher_profile.classes else []
            
            # Create events for this teacher (subset of events)
            teacher_num = int(teacher.nom)
            for idx, (event_type, subject, description, event_date, estimated, time_spent) in enumerate(events_data):
                if idx % 3 == teacher_num % 3:  # Each teacher gets different events
                    # Create teacher's source event
                    teacher_event = CalendarEvent(
                        user_identifier=teacher.email,
                        event_type=event_type,
                        subject=subject,
                        title=f'{event_type.capitalize()} - {subject}',
                        description=description,
                        date_iso=event_date.isoformat(),
                        estimated_time=estimated,
                        time_spent='0 minute',  # Teachers don't track time spent
                        is_hidden=False,
                        source_event_id=None,
                    )
                    db.add(teacher_event)
                    db.flush()
                    
                    # Create linked events for students in teacher's classes
                    for student in all_students:
                        student_profile = db.query(Eleve).filter(Eleve.utilisateur_id == student.id).first()
                        if student_profile and student_profile.classe in teacher_classes:
                            student_event = CalendarEvent(
                                user_identifier=student.email,
                                event_type=event_type,
                                subject=subject,
                                title=f'{event_type.capitalize()} - {subject}',
                                description=description,
                                date_iso=event_date.isoformat(),
                                estimated_time=estimated,
                                time_spent=time_spent if event_date < today else '0 minute',
                                is_hidden=False,
                                source_event_id=teacher_event.id,
                            )
                            db.add(student_event)
        
        db.commit()
        print("Database seeded successfully with test data!")
        print("Teachers: 0@example.com to 9@example.com (password: 12345678)")
        print("Students: a@example.com to z@example.com (password: 12345678)")
        
    finally:
        db.close()
