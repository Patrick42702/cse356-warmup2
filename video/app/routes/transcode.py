from app.services.transcode_trigger import trigger_transcode
from app.util import error, success
from flask import Blueprint, request

transcode_bp = Blueprint("transcode", __name__)

@transcode_bp.route('/transcode', methods=['POST'])
def transcode():
    data = request.get_json()
    filename = data.get('filename')
    if not filename:
        return error("No filename provided", 400)

    task_id = trigger_transcode(filename)
    return success(data=task_id.id, message="Transcoding started")
