from nicegui import ui, app

def create_navbar():
    """Crée la barre de navigation en bas de page"""
    role = app.storage.user.get('role')
    pending_target = {'value': None}
    
    ui.add_head_html('''
        <style>
            :root {
                --primary: #4E7ED2;
                --secondary: #9BB1E5;
                --tertiary: #BCCBF0;
            }
            
            .navbar-container {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background: var(--primary);
                box-shadow: 0 -4px 20px rgba(0,0,0,0.1);
                z-index: 1000;
            }
            .navbar-content {
                display: flex;
                justify-content: space-around;
                align-items: center;
                padding: 10px 0;
                max-width: 600px;
                margin: 0 auto;
            }
            .nav-item {
                display: flex;
                flex-direction: column;
                align-items: center;
                cursor: pointer;
                padding: 8px 16px;
                border-radius: 12px;
                transition: background 0.2s;
            }
            .nav-item:hover {
                background: rgba(255, 255, 255, 0.2);
            }
            .nav-item.active {
                background: rgba(255, 255, 255, 0.3);
            }
            .nav-icon {
                font-size: 24px;
                margin-bottom: 4px;
                color: white;
            }
            .nav-label {
                font-size: 12px;
                font-weight: 500;
                color: white;
            }
            .nav-item.active .nav-icon,
            .nav-item.active .nav-label {
                color: white;
            }
        </style>
    ''')
    
    with ui.element('div').classes('navbar-container'):
        with ui.dialog().props('persistent') as unsaved_dialog, ui.card().classes('q-pa-md'):
            ui.label('Modifications non enregistrées').classes('text-h6 q-mb-sm')
            ui.label('Veuillez enregistrer vos modifications, ou continuer sans enregistrer.').classes('text-body2 q-mb-md')
            with ui.row().classes('w-full justify-end'):
                ui.button('Aller enregistrer', on_click=unsaved_dialog.close).props('flat color=primary')

                def discard_and_navigate() -> None:
                    app.storage.user['profile_dirty'] = False
                    ui.run_javascript('window.__profileDirty = false;')
                    target = pending_target.get('value')
                    pending_target['value'] = None
                    unsaved_dialog.close()
                    if target:
                        ui.navigate.to(target)

                ui.button('Ne pas enregistrer', on_click=discard_and_navigate).props('color=negative')

        def guarded_navigate(target: str) -> None:
            if app.storage.user.get('profile_dirty', False):
                pending_target['value'] = target
                ui.notify('Veuillez enregistrer vos modifications', type='warning', timeout=3)
                ui.run_javascript(
                    '''
                    const saveBtn = document.getElementById('profile-save-button');
                    if (saveBtn) {
                        saveBtn.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        saveBtn.classList.add('bg-orange-3');
                        setTimeout(() => saveBtn.classList.remove('bg-orange-3'), 1800);
                    }
                    '''
                )
                unsaved_dialog.open()
                return
            ui.navigate.to(target)

        with ui.element('div').classes('navbar-content'):
            # Bouton Accueil
            with ui.element('div').classes('nav-item').on('click', lambda: guarded_navigate('/accueil')):
                ui.icon('home').classes('nav-icon')
                ui.label('Accueil').classes('nav-label')
            
            # Bouton Calendrier
            if role == 'enseignant':
                with ui.element('div').classes('nav-item').on('click', lambda: guarded_navigate('/calendrier')):
                    ui.icon('calendar_month').classes('nav-icon')
                    ui.label('Calendrier').classes('nav-label')

                with ui.element('div').classes('nav-item').on('click', lambda: guarded_navigate('/statistiques')):
                    ui.icon('bar_chart').classes('nav-icon')
                    ui.label('Statistiques').classes('nav-label')
            else:
                with ui.element('div').classes('nav-item').on('click', lambda: guarded_navigate('/calendrier')):
                    ui.icon('calendar_month').classes('nav-icon')
                    ui.label('Calendrier').classes('nav-label')

                with ui.element('div').classes('nav-item').on('click', lambda: guarded_navigate('/statistiques')):
                    ui.icon('bar_chart').classes('nav-icon')
                    ui.label('Statistiques').classes('nav-label')
            
            # Bouton Profil
            with ui.element('div').classes('nav-item').on('click', lambda: guarded_navigate('/profil')):
                ui.icon('person').classes('nav-icon')
                ui.label('Moi').classes('nav-label')