from __future__ import annotations

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_talisman import Talisman

ACCOUNTS = {}


def build_account(account_id: str, payload: dict) -> dict:
    return {
        "id": account_id,
        "name": payload.get("name", ""),
        "email": payload.get("email", ""),
        "account_type": payload.get("account_type", "customer"),
        "balance": payload.get("balance", 0),
    }


def reset_accounts():
    ACCOUNTS.clear()


def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})
    Talisman(
        app,
        force_https=False,
        frame_options='SAMEORIGIN',
        content_security_policy="default-src 'self'",
        strict_transport_security="max-age=31536000; includeSubDomains",
    )

    @app.route("/")
    def service_info():
        return jsonify({"name": "Account REST API Service", "version": "1.0"})

    @app.route("/accounts", methods=["GET", "POST"])
    def accounts_collection():
        if request.method == "GET":
            return jsonify({"accounts": list(ACCOUNTS.values())})

        payload = request.get_json(silent=True) or {}
        if not payload:
            return jsonify({"error": "Request body is required"}), 400

        account_id = str(len(ACCOUNTS) + 1)
        account = build_account(account_id, payload)
        ACCOUNTS[account_id] = account
        return jsonify(account), 201

    @app.route("/accounts/<account_id>", methods=["GET", "PUT", "DELETE"])
    def account_detail(account_id):
        account = ACCOUNTS.get(account_id)
        if account is None:
            return jsonify({"error": "Account not found"}), 404

        if request.method == "GET":
            return jsonify(account)

        if request.method == "PUT":
            payload = request.get_json(silent=True) or {}
            if not payload:
                return jsonify({"error": "Request body is required"}), 400

            account.update({
                "name": payload.get("name", account["name"]),
                "email": payload.get("email", account["email"]),
                "account_type": payload.get("account_type", account["account_type"]),
                "balance": payload.get("balance", account["balance"]),
            })
            ACCOUNTS[account_id] = account
            return jsonify(account)

        del ACCOUNTS[account_id]
        return jsonify({"message": "Account deleted", "id": account_id})

    return app


app = create_app()
