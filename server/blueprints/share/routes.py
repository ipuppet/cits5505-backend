import uuid
from flask import Blueprint, render_template, request, g

from server.blueprints.share.forms import ShareForm
from server.utils.decorators import login_required, api_response
import server.blueprints.share.logic as logic

share_bp = Blueprint("share", __name__, template_folder="templates")


@share_bp.route("/", methods=["GET"])
@login_required
def index():
    return render_template("share/index.html")


@share_bp.route("/shares/<uuid:id>", methods=["GET", "DELETE"])
@login_required
@api_response
def shared():
    share_id = request.args.get("id")
    if not share_id:
        raise ValueError("Share ID is required.")
    # Handle DELETE request
    if request.method == "DELETE":
        return logic.delete_share(uuid.UUID(request.args.get("id")))
    # Handle GET request
    share = logic.get_shared(uuid.UUID(request.args.get("id")))
    if not share:
        raise ValueError("Share not found.")
    return share


@share_bp.route("/shares", methods=["POST"])
@login_required
@api_response
def create_share():
    share_form = ShareForm(request.form)
    if not share_form.validate():
        raise ValueError("Invalid form data.")
    share = logic.create_share(
        sender_id=g.user.id,
        receiver_id=share_form.receiver_id.data,
        scope=share_form.scope.data,
    )
    return share
