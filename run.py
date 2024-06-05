#Runs the create_app() function from _init_.py
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
