# Error handling logic for the Flask application

from flask import jsonify
from domain.exceptions import NotFoundException, ValidationException, UnauthorizedException, ConflictException

class CustomError(Exception):
    status_code = 400

    def __init__(self, message, status_code=None):
        super().__init__(message)
        if status_code is not None:
            self.status_code = status_code
        self.message = message

    def to_dict(self):
        return {'message': self.message}

def handle_error(error):
    if isinstance(error, NotFoundException):
        return jsonify({'message': error.message}), 404
    if isinstance(error, ValidationException):
        return jsonify({'message': error.message}), 400
    if isinstance(error, UnauthorizedException):
        return jsonify({'message': error.message}), 401
    if isinstance(error, ConflictException):
        return jsonify({'message': error.message}), 409

    if isinstance(error, CustomError):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    import traceback
    print(traceback.format_exc())
    response = jsonify({'message': 'An unexpected error occurred.', 'error': str(error)})
    response.status_code = 500
    return response

def register_error_handlers(app):
    app.register_error_handler(Exception, handle_error)