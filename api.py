from models import LinkObject
from flask.wrappers import Response
from config import App, db
from flask import redirect, Response

@App.route('/api/link/delete/<id>', methods=['DELETE'])
def delete_link(id):
    lo = LinkObject.query.get(id)
    db.session.delete(lo)
    db.session.commit()
    return Response("OK", 200)
    
@App.route('/api/link/toggle_updates/<id>', methods=['PATCH'])
def toggle_udpates(id):
    lo = LinkObject.query.get(id)
    lo.check_updates = not lo.check_updates
    db.session.merge(lo)
    db.session.commit()
    return Response("OK", 200)