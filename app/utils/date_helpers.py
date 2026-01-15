from datetime import datetime, timedelta
from typing import List

def get_week_dates(start_date: datetime = None) -> List[datetime]:
    """Retourne les 7 jours de la semaine à partir d'une date"""
    if not start_date:
        start_date = datetime.now()
    
    # Trouver le lundi de la semaine
    monday = start_date - timedelta(days=start_date.weekday())
    
    return [monday + timedelta(days=i) for i in range(7)]

def format_date_french(date: datetime) -> str:
    """Formate une date en français"""
    days = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    months = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin',
              'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
    
    day_name = days[date.weekday()]
    day_num = date.day
    month = months[date.month - 1]
    
    return f"{day_name} {day_num} {month}"

def parse_time_string(time_str: str) -> float:
    """Convertit une chaîne de temps (ex: '1h30') en heures (float)"""
    try:
        time_str = time_str.lower().strip()
        
        # Format: 1h30, 1h 30, 1:30, etc.
        if 'h' in time_str:
            parts = time_str.replace('h', ':').split(':')
            hours = float(parts[0])
            minutes = float(parts[1]) if len(parts) > 1 else 0
            return hours + (minutes / 60)
        
        # Format: 1.5, 2.0
        return float(time_str)
    except:
        return 0.0

def format_time_display(hours: float) -> str:
    """Formate un temps en heures (float) pour l'affichage"""
    h = int(hours)
    m = int((hours - h) * 60)
    
    if m == 0:
        return f"{h}h"
    return f"{h}h{m:02d}"