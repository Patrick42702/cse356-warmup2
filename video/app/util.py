from flask import jsonify


def success(data=None, message="OK"):
    return jsonify({"message": message, "data": data}), 200

def error(message="An error occurred", code=400):
    return jsonify({"error": message}), code
