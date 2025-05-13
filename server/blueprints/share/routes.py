from flask import Blueprint, render_template, request, flash, url_for, redirect
from flask_login import login_required, current_user

from server.blueprints.share.forms import ShareForm, PreviewForm
from server.utils.decorators import api_response
import server.blueprints.share.logic as share_logic
import server.blueprints.browse.logic as browse_logic

share_bp = Blueprint("share", __name__, template_folder="templates")


@share_bp.route("/", methods=["GET"])
@login_required
def index():
    form = ShareForm()
    shares_received, shares_sent = share_logic.get_user_shares()
    return render_template(
        "share/index.html",
        form=form,
        exercise_metrics=browse_logic.get_exercises_metrics(),
        exercise_types=browse_logic.get_exercise_types(),
        body_measurement_types=browse_logic.get_body_measurement_types(),
        shares_received=shares_received,
        shares_sent=shares_sent,
    )


@share_bp.route("/preview", methods=["POST"])
@login_required
@api_response
def preview():
    form = PreviewForm.from_json(request.json)
    if not form.validate():
        raise ValueError(str(form.errors))
    return share_logic.get_shared_data(
        current_user.id,
        form.scope.data,
        form.start_date_utc,
        form.end_date_utc,
    )


@share_bp.route("/<uuid:share_id>", methods=["GET"])
@login_required
def view(share_id):
    if not share_id:
        raise ValueError("Share ID is required.")
    try:
        shared_data = share_logic.get_shared(share_id)
        return render_template(
            "share/view.html",
            shared_data=shared_data,
            exercise_metrics=browse_logic.get_exercises_metrics(),
            exercise_types=browse_logic.get_exercise_types(),
            body_measurement_types=browse_logic.get_body_measurement_types(),
        )
    except Exception as e:
        flash(str(e), "danger")
        return redirect(url_for("share.index"))


@share_bp.route("/<uuid:share_id>", methods=["DELETE"])
@login_required
@api_response
def delete(share_id):
    if not share_id:
        raise ValueError("Share ID is required.")
    return share_logic.delete_share(share_id)


@share_bp.route("/create", methods=["POST"])
@login_required
def create_share():
    form = ShareForm()
    if not form.validate():
        flash(str(form.errors), "danger")
        return redirect(url_for("share.index"))
    try:
        share = share_logic.create_share(
            sender_id=current_user.id,
            receiver_id=form.receiver_id.data,
            scope=form.scope.data,
            start_date=form.start_date_utc,
            end_date=form.end_date_utc,
        )
        flash(f"Share {share.id} created successfully!", "success")
    except Exception as e:
        flash(str(e), "danger")
    return redirect(url_for("share.index"))
