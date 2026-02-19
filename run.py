from app import create_app

app = create_app()
#aide de l'IA concernant le "__mp_main__"
if __name__ in {"__main__", "__mp_main__"}:
    app.run(debug=True)
