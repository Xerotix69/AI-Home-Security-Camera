from flask import Blueprint, flash, redirect, url_for, session, request, render_template

import firebase_admin
from firebase_admin import credentials, storage, firestore
#from google.cloud.firestore import timestamp

from functions import filter_events

search_routes = Blueprint('search', __name__)
@search_routes.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    camera_id = request.args.get('camera', 'Front Gate')
    
    events = []
    if query or camera_id:
        events = filter_events("images_metadata", cameraID=camera_id)
    
    return render_template('dashboard.html', 
                          events=events, 
                          query=query, 
                          camera_id=camera_id)

