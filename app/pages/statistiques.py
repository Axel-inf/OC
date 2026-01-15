from nicegui import ui, app
from components.navbar import create_navbar
import random

def create():
    """Crée la page des statistiques"""
    
    ui.add_head_html('''
        <style>
            .stats-container {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px 20px 100px 20px;
            }
            .stats-header {
                background: white;
                padding: 20px;
                margin-bottom: 20px;
                border-radius: 15px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            }
            .stats-title {
                font-size: 28px;
                font-weight: 700;
                color: #333;
                text-align: center;
            }
            .chart-card {
                background: white;
                padding: 20px;
                margin-bottom: 20px;
                border-radius: 15px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            }
            .chart-title {
                font-size: 18px;
                font-weight: 600;
                color: #333;
                margin-bottom: 15px;
                text-align: center;
            }
            .filter-section {
                background: white;
                padding: 15px;
                margin-bottom: 20px;
                border-radius: 15px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            }
        </style>
    ''')
    
    with ui.column().classes('stats-container'):
        # En-tête
        with ui.element('div').classes('stats-header'):
            ui.html('<div class="stats-title">Statistiques</div>', sanitize=False)
        
        # Filtres
        with ui.element('div').classes('filter-section'):
            with ui.row().classes('w-full gap-2'):
                branche_filter = ui.select(
                    ['Toutes', 'Mathématiques', 'Français', 'Allemand', 'Anglais', 
                     'Histoire', 'Géographie', 'Sciences'],
                    label='Branche',
                    value='Toutes'
                ).props('outlined dense').classes('flex-1')
                
                periode_filter = ui.select(
                    ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                     'Septembre', 'Octobre', 'Novembre', 'Décembre'],
                    label='Période',
                    value='Janvier'
                ).props('outlined dense').classes('flex-1')
        
        # Graphique 1: Charge de travail par mois
        with ui.element('div').classes('chart-card'):
            ui.html('<div class="chart-title">Mois de janvier</div>', sanitize=False)
            
            # Données exemple pour le graphique
            mois_data = {
                'categories': ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4'],
                'series': [
                    {'name': 'Devoirs', 'data': [8, 12, 10, 15]},
                    {'name': 'Examens', 'data': [2, 1, 3, 2]},
                ]
            }
            
            # Utilisation d'un graphique echarts via NiceGUI
            chart = ui.echart({
                'xAxis': {'type': 'category', 'data': mois_data['categories']},
                'yAxis': {'type': 'value'},
                'series': [
                    {
                        'name': 'Devoirs',
                        'type': 'bar',
                        'data': [8, 12, 10, 15],
                        'itemStyle': {'color': '#667eea'}
                    },
                    {
                        'name': 'Examens',
                        'type': 'bar',
                        'data': [2, 1, 3, 2],
                        'itemStyle': {'color': '#764ba2'}
                    },
                ],
                'legend': {'data': ['Devoirs', 'Examens']},
                'tooltip': {'trigger': 'axis'}
            }).classes('w-full')
        
        # Graphique 2: Répartition par matière
        with ui.element('div').classes('chart-card'):
            ui.html('<div class="chart-title">Mois de février</div>', sanitize=False)
            
            chart2 = ui.echart({
                'xAxis': {'type': 'category', 'data': ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4']},
                'yAxis': {'type': 'value'},
                'series': [
                    {
                        'name': 'Total charge',
                        'type': 'bar',
                        'data': [10, 15, 12, 18],
                        'itemStyle': {'color': '#4ECDC4'}
                    },
                    {
                        'name': 'Statistiques',
                        'type': 'bar',
                        'data': [8, 10, 9, 14],
                        'itemStyle': {'color': '#95E1D3'}
                    },
                ],
                'legend': {'data': ['Total charge', 'Statistiques']},
                'tooltip': {'trigger': 'axis'}
            }).classes('w-full')
        
        # Statistiques textuelles
        with ui.element('div').classes('chart-card'):
            ui.html('<div class="chart-title">Résumé</div>', sanitize=False)
            
            with ui.column().classes('w-full gap-3'):
                with ui.row().classes('w-full items-center'):
                    ui.icon('assignment', size='24px', color='#667eea')
                    ui.label('Total devoirs: 45').classes('text-lg')
                
                with ui.row().classes('w-full items-center'):
                    ui.icon('quiz', size='24px', color='#764ba2')
                    ui.label('Total examens: 8').classes('text-lg')
                
                with ui.row().classes('w-full items-center'):
                    ui.icon('schedule', size='24px', color='#4ECDC4')
                    ui.label('Temps moyen/devoir: 1h30').classes('text-lg')
                
                with ui.row().classes('w-full items-center'):
                    ui.icon('trending_up', size='24px', color='#95E1D3')
                    ui.label('Précision estimations: 85%').classes('text-lg')
        
        # Navbar en bas
        create_navbar()