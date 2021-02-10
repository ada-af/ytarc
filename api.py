from flask.wrappers import Response
from config import App, db
from flask import redirect, Response

@App.route('/api/link/delete/<id>', methods=['DELETE'])
def delete_link(id):
    return Response("OK", 200)
    
@App.route('/api/link/toggle_updates/<id>', methods=['PATCH'])
def toggle_udpates(id):
    return Response("OK", 200)