import uuid
from flask import Blueprint, render_template, request, g, flash

from server.blueprints.share.forms import ShareForm
from server.utils.decorators import login_required, api_response
import server.blueprints.share.logic as logic

share_bp = Blueprint("share", __name__, template_folder="templates")


@share_bp.route("/", methods=["GET"])
@login_required
def index():
    return render_template("share/index.html")


@share_bp.route("/<uuid:share_id>", methods=["GET", "DELETE"])
@login_required
@api_response
def shared(share_id):
    if not share_id:
        raise ValueError("Share ID is required.")
    share_id = uuid.UUID(share_id)
    # Handle DELETE request
    if request.method == "DELETE":
        return logic.delete_share(share_id)
    # Handle GET request
    share = logic.get_shared(share_id)
    if not share:
        raise ValueError("Share not found.")
    return share


@share_bp.route("/create", methods=["POST"])
@login_required
def create_share():
    share_form = ShareForm(request.form)
    if not share_form.validate():
        raise ValueError(share_form.errors)
    try:
        share = logic.create_share(
            sender_id=g.user.id,
            receiver_id=share_form.receiver_id.data,
            scope=share_form.scope.data,
        )
        flash(f"Share {share.id} created successfully!", "success")
    except Exception as e:
        flash(str(e), "danger")
    return render_template("share/create.html", share=share)
