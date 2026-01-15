from nicegui import ui

def create_event_card(title: str, description: str, date: str, time_estimate: str, color: str = '#667eea'):
    """Crée une carte d'événement (devoir ou examen)"""
    
    with ui.card().classes('w-full').style(f'background: {color}; color: white;'):
        with ui.column().classes('gap-2'):
            ui.label(title).classes('text-h6 font-bold')
            ui.label(description).classes('text-body2')
            
            with ui.row().classes('items-center gap-2'):
                ui.icon('calendar_today', size='sm')
                ui.label(f'Pour le: {date}')
            
            with ui.row().classes('items-center gap-2'):
                ui.icon('schedule', size='sm')
                ui.label(f'Temps estimé: {time_estimate}')

def create_stats_card(title: str, value: str, icon: str, color: str = '#667eea'):
    """Crée une carte de statistique"""
    
    with ui.card().classes('w-full p-4'):
        with ui.row().classes('items-center gap-4'):
            with ui.element('div').style(f'width: 60px; height: 60px; background: {color}; border-radius: 50%; display: flex; align-items: center; justify-content: center;'):
                ui.icon(icon, size='lg', color='white')
            
            with ui.column().classes('flex-1'):
                ui.label(title).classes('text-body2 text-grey-7')
                ui.label(value).classes('text-h5 font-bold')