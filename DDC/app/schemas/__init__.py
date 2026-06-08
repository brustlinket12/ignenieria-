from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Email(required=True)
    name = fields.Str(required=True)
    role = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)


class ClientSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    id_type = fields.Str(required=True)
    id_number = fields.Str(required=True)
    country = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)


class RiskAssessmentSchema(Schema):
    id = fields.Int(dump_only=True)
    case_file_id = fields.Int(dump_only=True)
    sector_score = fields.Int(required=True)
    jurisdiction_score = fields.Int(required=True)
    pep_score = fields.Int(required=True)
    volume_score = fields.Int(required=True)
    funds_origin_score = fields.Int(required=True)
    sanctions_score = fields.Int(required=True)
    total_score = fields.Int(allow_none=True)
    risk_level = fields.Str(allow_none=True)
    calculation_aborted = fields.Bool()
    created_at = fields.DateTime(dump_only=True)


class SanctionsScreeningSchema(Schema):
    id = fields.Int(dump_only=True)
    case_file_id = fields.Int(dump_only=True)
    provider = fields.Str()
    result = fields.Str(required=True)
    matched_name = fields.Str(allow_none=True)
    matched_list = fields.Str(allow_none=True)
    raw_response = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)


class AlertSchema(Schema):
    id = fields.Int(dump_only=True)
    case_file_id = fields.Int()
    type = fields.Str(required=True)
    message = fields.Str(required=True)
    read = fields.Bool()
    created_at = fields.DateTime(dump_only=True)


class AuditLogSchema(Schema):
    id = fields.Int(dump_only=True)
    case_file_id = fields.Int(allow_none=True)
    user_id = fields.Int()
    event_type = fields.Str(required=True)
    payload = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    user = fields.Nested(UserSchema, dump_only=True)


class DocumentSchema(Schema):
    id = fields.Int(dump_only=True)
    case_file_id = fields.Int()
    filename = fields.Str(required=True)
    file_path = fields.Str(required=True)
    mime_type = fields.Str(allow_none=True)
    size = fields.Int(allow_none=True)
    created_at = fields.DateTime(dump_only=True)


class CaseFileSchema(Schema):
    id = fields.Int(dump_only=True)
    client_id = fields.Int(required=True)
    client = fields.Nested(ClientSchema, dump_only=True)
    status = fields.Str()
    current_step = fields.Int()
    blocked_by_sanctions = fields.Bool()
    created_by = fields.Int()
    reviewed_by = fields.Int(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    submitted_at = fields.DateTime(allow_none=True)
    approved_at = fields.DateTime(allow_none=True)
    rejected_at = fields.DateTime(allow_none=True)
    risk_assessment = fields.Nested(RiskAssessmentSchema, dump_only=True)
    sanctions_screening = fields.List(fields.Nested(SanctionsScreeningSchema), dump_only=True)


class CaseFileCreateSchema(Schema):
    client_name = fields.Str(required=True)
    client_id_type = fields.Str(required=True)
    client_id_number = fields.Str(required=True)
    client_country = fields.Str(required=True)


class CaseFileUpdateSchema(Schema):
    current_step = fields.Int()
    status = fields.Str()