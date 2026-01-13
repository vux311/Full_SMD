from flask import Blueprint, request, jsonify
from dependency_injector.wiring import inject, Provide
from dependency_container import Container
from services.student_service import StudentService
from api.schemas.student_schema import StudentSubscriptionSchema, StudentReportSchema

student_bp = Blueprint('student', __name__, url_prefix='/student')
sub_schema = StudentSubscriptionSchema()
rep_schema = StudentReportSchema()

@student_bp.route('/subscribe', methods=['POST', 'OPTIONS'], strict_slashes=False)
@inject
def subscribe(service: StudentService = Provide[Container.student_service]):
    """
    Student subscribes to a subject
    ---
    tags:
      - Student Features
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              student_id: {type: integer}
              subject_id: {type: integer}
    responses:
      201:
        description: Subscription created
    """
    data = request.get_json() or {}
    item = service.subscribe(data.get('student_id'), data.get('subject_id'))
    return jsonify(sub_schema.dump(item)), 201

@student_bp.route('/report', methods=['POST', 'OPTIONS'], strict_slashes=False)
@inject
def report(service: StudentService = Provide[Container.student_service]):
    """
    Student reports an issue with a syllabus
    ---
    tags:
      - Student Features
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/StudentReport'
    responses:
      201:
        description: Report created
    """
    data = request.get_json() or {}
    item = service.report_syllabus(data.get('student_id'), data.get('syllabus_id'), data.get('content'))
    return jsonify(rep_schema.dump(item)), 201

@student_bp.route('/reports', methods=['GET', 'OPTIONS'], strict_slashes=False)
@inject
def list_reports(service: StudentService = Provide[Container.student_service]):
    """
    List all student reports (Admin)
    ---
    tags:
      - Student Features
    responses:
      200:
        description: List of reports
    """
    items = service.list_reports()
    return jsonify(rep_schema.dump(items, many=True)), 200