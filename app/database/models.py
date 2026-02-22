from sqlalchemy import Column, Integer, String, Float, Date, Boolean, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship, declarative_base
import enum

Base = declarative_base()

class RoleEnum(enum.Enum):
    ELEVE = "eleve"
    ENSEIGNANT = "enseignant"

class Utilisateur(Base):
    __tablename__ = 'utilisateurs'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    mot_de_passe = Column(String(255), nullable=False)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
    
    # Relations
    eleve = relationship("Eleve", back_populates="utilisateur", uselist=False)
    enseignant = relationship("Enseignant", back_populates="utilisateur", uselist=False)

class Eleve(Base):
    __tablename__ = 'eleves'
    
    id = Column(Integer, primary_key=True)
    utilisateur_id = Column(Integer, ForeignKey('utilisateurs.id'), unique=True)
    classe = Column(String(50), nullable=False)
    niveau_maths = Column(String(50))
    langue1 = Column(String(50))
    langue2 = Column(String(50))
    langue3 = Column(String(50))
    os = Column(String(100))  # Option Spécifique
    oc = Column(String(100))  # Option Complémentaire
    basic_english = Column(Boolean, default=False)
    bilingue = Column(Boolean, default=False)
    
    # Relations
    utilisateur = relationship("Utilisateur", back_populates="eleve")
    temps_reels = relationship("TempsReel", back_populates="eleve")

class Enseignant(Base):
    __tablename__ = 'enseignants'
    
    id = Column(Integer, primary_key=True)
    utilisateur_id = Column(Integer, ForeignKey('utilisateurs.id'), unique=True)
    branches = Column(String(255))  # Liste des branches séparées par virgule
    classes = Column(String(255))   # Liste des classes séparées par virgule
    os = Column(String(100))
    oc = Column(String(100))
    basic_english = Column(Boolean, default=False)
    bilingue = Column(Boolean, default=False)
    
    # Relations
    utilisateur = relationship("Utilisateur", back_populates="enseignant")
    devoirs = relationship("Devoir", back_populates="enseignant")
    examens = relationship("Examen", back_populates="enseignant")

class Devoir(Base):
    __tablename__ = 'devoirs'
    
    id = Column(Integer, primary_key=True)
    titre = Column(String(200), nullable=False)
    branche = Column(String(100), nullable=False)
    description = Column(Text)
    date_rendu = Column(Date, nullable=False)
    temps_estime = Column(Float)  # En heures
    classe = Column(String(50), nullable=False)
    enseignant_id = Column(Integer, ForeignKey('enseignants.id'))
    
    # Pour les options spécifiques
    est_option = Column(Boolean, default=False)
    type_option = Column(String(50))  # 'OS', 'OC', 'langue3', etc.
    
    # Relations
    enseignant = relationship("Enseignant", back_populates="devoirs")
    temps_reels = relationship("TempsReel", back_populates="devoir")

class Examen(Base):
    __tablename__ = 'examens'
    
    id = Column(Integer, primary_key=True)
    titre = Column(String(200), nullable=False)
    branche = Column(String(100), nullable=False)
    description = Column(Text)
    date_examen = Column(Date, nullable=False)
    temps_revision_estime = Column(Float)  # En heures
    classe = Column(String(50), nullable=False)
    enseignant_id = Column(Integer, ForeignKey('enseignants.id'))
    
    # Pour les options spécifiques
    est_option = Column(Boolean, default=False)
    type_option = Column(String(50))
    
    # Relations
    enseignant = relationship("Enseignant", back_populates="examens")
    temps_reels = relationship("TempsReel", back_populates="examen")

class TempsReel(Base):
    __tablename__ = 'temps_reels'
    
    id = Column(Integer, primary_key=True)
    eleve_id = Column(Integer, ForeignKey('eleves.id'))
    devoir_id = Column(Integer, ForeignKey('devoirs.id'), nullable=True)
    examen_id = Column(Integer, ForeignKey('examens.id'), nullable=True)
    temps_reel = Column(Float, nullable=False)  # En heures
    
    # Relations
    eleve = relationship("Eleve", back_populates="temps_reels")
    devoir = relationship("Devoir", back_populates="temps_reels")
    examen = relationship("Examen", back_populates="temps_reels")


class CalendarEvent(Base):
    __tablename__ = 'calendar_events'

    id = Column(Integer, primary_key=True)
    user_identifier = Column(String(255), nullable=False, index=True)
    event_type = Column(String(20), nullable=False)
    subject = Column(String(100), nullable=False)
    title = Column(String(200), nullable=False, default='')
    description = Column(Text, default='')
    date_iso = Column(String(10), nullable=False)
    estimated_time = Column(String(50), nullable=False)
    time_spent = Column(String(50), nullable=False, default='0 minute')
    is_hidden = Column(Boolean, nullable=False, default=False)