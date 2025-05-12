from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user

from server.blueprints.share.forms import ShareForm
from server.utils.decorators import api_response
import server.blueprints.share.logic as share_logic
import server.blueprints.browse.logic as browse_logic

share_bp = Blueprint("share", __name__, template_folder="templates")


@share_bp.route("/", methods=["GET"])
@login_required
def index():
    share_form = ShareForm()
    return render_template(
        "share/index.html",
        form=share_form,
        exercise_types=browse_logic.get_exercise_types(),
        body_measurement_types=browse_logic.get_body_measurement_types(),
    )


@share_bp.route("/<uuid:share_id>", methods=["GET", "DELETE"])
@login_required
@api_response
def shared(share_id):
    if not share_id:
        raise ValueError("Share ID is required.")
    # Handle DELETE request
    if request.method == "DELETE":
        return share_logic.delete_share(share_id)
    return share_logic.get_shared(share_id)


@share_bp.route("/create", methods=["POST"])
@login_required
def create_share():
    share_form = ShareForm()
    if not share_form.validate():
        flash(share_form.errors, "danger")
        return render_template("share/create.html", form=share_form)
    share = None
    try:
        share = share_logic.create_share(
            sender_id=current_user.id,
            receiver_id=share_form.receiver_id.data,
            scope=share_form.scope.data,
        )
        flash(f"Share {share.id} created successfully!", "success")
    except Exception as e:
        flash(str(e), "danger")
    return render_template("share/create.html", share=share)
