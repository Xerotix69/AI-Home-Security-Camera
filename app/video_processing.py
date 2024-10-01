from flask import Blueprint, request, jsonify
import os
import time

from functions import take_snapshot, record_clip            
from stream import get_frames

video_routes = Blueprint('video', __name__)


@video_routes.route('/take_snapshot', methods=['POST'])
def snapshot():
    take_snapshot(get_frames(1), "screenshots", "image")
    return jsonify({"status": "screenshot taken"})

@video_routes.route('/record_clip', methods=['POST'])
def clip():
    record_clip(get_frames(24*2), 24, 2, "clips", "video")
    return jsonify({"status": "clip record"})