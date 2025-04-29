import uuid
from flask import Blueprint, render_template, request, g

from server.blueprints.share.forms import ShareForm
from server.utils.decorators import login_required, api_response
import server.blueprints.share.logic as logic

share_bp = Blueprint("share", __name__, template_folder="templates")


@share_bp.route("/", methods=["GET"])
@login_required
def index():
    if request.method == "GET":
        return render_template("share/index.html")


@share_bp.route("/shares/<uuid:id>", methods=["GET"])
@login_required
@api_response
def shared():
    share_id = request.args.get("id")
    if not share_id:
        raise ValueError("Share ID is required.")
    share = logic.get_shared(uuid.UUID(request.args.get("id")))
    if not share:
        raise ValueError("Share not found.")
    return share


@share_bp.route("/shares", methods=["POST"])
@login_required
@api_response
def create_shared():
    share_form = ShareForm(request.form)
    if not share_form.validate():
        raise ValueError("Invalid form data.")
    share = logic.create_shared(
        sender_id=g.user.id,
        receiver_id=share_form.receiver_id.data,
        scope=share_form.scope.data,
    )
    return share


@share_bp.route("/shares/<uuid:id>", methods=["DELETE"])
@login_required
@api_response
def delete_shared():
    share_id = request.args.get("id")
    if not share_id:
        raise ValueError("Share ID is required.")
    logic.delete_shared(uuid.UUID(request.args.get("id")))
