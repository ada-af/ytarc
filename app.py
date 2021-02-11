from logging import debug
from config import App, db
import models
import routes
import api
import updater
from pyfladesk import init_gui

if __name__ == '__main__':
    db.create_all()
    App.run(debug=True, host='0.0.0.0')
    # init_gui(App)