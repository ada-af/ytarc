from logging import debug
from config import App, db
import models
import routes
import api
import updater
import os
from pyfladesk import init_gui
import pathlib

if __name__ == '__main__':
    if not os.path.exists('storage'):
        pathlib.Path("storage").mkdir(parents=True, exist_ok=True)

    if os.path.exists('update.lck'):
        os.remove('update.lck')

    db.create_all()
    App.run(debug=True, host='0.0.0.0')
    # init_gui(App)