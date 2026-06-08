from flask import Blueprint, request, jsonify
from app.models.client import Client
from app.schemas import ClientSchema

clients_bp = Blueprint("clients", __name__)
client_schema = ClientSchema()


@clients_bp.route("/api/clients", methods=["POST"])
def create_client():
    data = request.get_json()
    try:
        validated = client_schema.load(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    client = Client(**validated)
    from app.extensions import db
    db.session.add(client)
    db.session.commit()

    return jsonify(client.to_dict()), 201


@clients_bp.route("/api/clients", methods=["GET"])
def list_clients():
    from app.extensions import db
    clients = Client.query.order_by(Client.created_at.desc()).all()
    return jsonify([c.to_dict() for c in clients]), 200


@clients_bp.route("/api/clients/<int:client_id>", methods=["GET"])
def get_client(client_id):
    from app.extensions import db
    client = Client.query.get(client_id)
    if not client:
        return jsonify({"error": "Cliente no encontrado"}), 404
    return jsonify(client.to_dict()), 200