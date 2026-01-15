from nicegui import ui, app

def create_header(title: str, show_back: bool = False):
    """Crée un en-tête avec titre et bouton retour optionnel"""
    
    with ui.row().classes('w-full items-center justify-between p-4 bg-white shadow-md'):
        if show_back:
            ui.button(
                icon='arrow_back',
                on_click=lambda: ui.navigate.back()
            ).props('flat round color=primary')
        
        ui.label(title).classes('text-h5 font-bold')
        
        # Icône de profil
        ui.button(
            icon='person',
            on_click=lambda: ui.navigate.to('/profil')
        ).props('flat round color=primary')