from flask import Blueprint
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.libs.exceptions import FyleError
from core.models.assignments import Assignment
from .schema import AssignmentSchema
from marshmallow.exceptions import ValidationError

teacher_assignments_resources = Blueprint('teacher_assignments_resources', __name__)


@teacher_assignments_resources.route('/assignments', methods=['GET'], strict_slashes=False)
@decorators.auth_principal
def list_assignments(p):
    """Returns list of assignments"""
    teachers_assignments = Assignment.get_assignments_by_teacher(p.teacher_id)
    teachers_assignments_dump = AssignmentSchema().dump(teachers_assignments, many=True)
    return APIResponse.respond(data=teachers_assignments_dump)


@teacher_assignments_resources.route('/assignments/grade', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.auth_principal
def upsert_assignment(p, incoming_payload):
    """Grade an assignment"""
    assignment = Assignment.get_by_id(incoming_payload['id'])
    grade_given = incoming_payload["grade"]
    teacher_id = p.teacher_id

    if assignment is None:
        raise FyleError(404, "FyleError")

    if assignment.teacher_id != teacher_id or assignment.state != "SUBMITTED":
        raise FyleError(400, "FyleError")
    
    grade_list = ["A", "B", "C", "D"]
    if grade_given not in grade_list:
        raise ValidationError(404, "ValidationError")

    assignment.grade = grade_given
    db.session.commit()
    assignment_dump = AssignmentSchema().dump(assignment)
    return APIResponse.respond(data=assignment_dump)