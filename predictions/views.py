from datetime import date

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from contests.models import ContestGroup, GroupMembership
from matches.models import Match

from . import leaderboard as leaderboard_service
from .forms import PointAdjustmentForm, PredictionForm
from .models import PointTransaction, Prediction


@login_required
def predict(request, match_id):
    match = get_object_or_404(Match, id=match_id, published=True)

    if request.user.is_staff:
        messages.error(request, 'Admin accounts cannot submit predictions.')
        return redirect('matches:upcoming')

    is_approved_member = GroupMembership.objects.filter(
        user=request.user, status=GroupMembership.Status.APPROVED
    ).exists()
    if not is_approved_member:
        messages.error(
            request,
            'You must be an approved member of a contest group to submit predictions.',
        )
        return redirect('contests:groups')

    if timezone.now() >= match.prediction_deadline:
        messages.error(request, 'The prediction deadline for this match has passed.')
        return redirect('matches:upcoming')

    prediction = Prediction.objects.filter(user=request.user, match=match).first()

    if request.method == 'POST':
        form = PredictionForm(request.POST, instance=prediction, match=match)
        if form.is_valid():
            if timezone.now() >= match.prediction_deadline:
                messages.error(request, 'The prediction deadline for this match has passed.')
                return redirect('matches:upcoming')

            pred = form.save(commit=False)
            pred.user = request.user
            pred.match = match
            pred.save()
            messages.success(request, 'Your prediction has been saved.')
            return redirect('matches:upcoming')
    else:
        form = PredictionForm(instance=prediction, match=match)

    return render(request, 'predictions/predict.html', {
        'form': form, 'match': match, 'prediction': prediction,
    })


@login_required
def my_predictions(request):
    predictions = (
        Prediction.objects.filter(user=request.user)
        .select_related('match__fixture')
        .order_by('-match__fixture__kickoff_at')
    )
    return render(request, 'predictions/my_predictions.html', {'predictions': predictions})


def _approved_groups(user):
    return [
        m.group for m in
        GroupMembership.objects.filter(user=user, status=GroupMembership.Status.APPROVED)
        .select_related('group')
    ]


def _leaderboard_groups(user):
    """Admins can view leaderboards for every group without joining any."""
    if user.is_staff:
        return list(ContestGroup.objects.filter(is_active=True))
    return _approved_groups(user)


def _selected_group(request, groups):
    group_id = request.GET.get('group')
    if group_id:
        for group in groups:
            if str(group.id) == group_id:
                return group
    return groups[0]


@login_required
def leaderboard(request):
    groups = _leaderboard_groups(request.user)
    if not groups:
        return render(request, 'predictions/no_group.html')

    selected_group = _selected_group(request, groups)

    tab = request.GET.get('tab')
    if tab not in ('overall', 'weekly'):
        tab = 'overall'

    context = {
        'groups': groups,
        'selected_group': selected_group,
        'tab': tab,
    }

    if tab == 'weekly':
        weeks = leaderboard_service.available_weeks(selected_group)

        selected_week = None
        week_param = request.GET.get('week')
        if week_param:
            try:
                parsed = date.fromisoformat(week_param)
                if parsed in weeks:
                    selected_week = parsed
            except ValueError:
                selected_week = None
        if selected_week is None and weeks:
            selected_week = weeks[0]

        entries = []
        if selected_week:
            entries = leaderboard_service.weekly_leaderboard(selected_group, selected_week)

        context.update({
            'weeks': weeks,
            'selected_week': selected_week,
            'entries': entries,
        })
    else:
        context['entries'] = leaderboard_service.overall_leaderboard(selected_group)

    return render(request, 'predictions/leaderboard.html', context)


@login_required
def leader_taunt(request):
    """Return JSON with the group leader's name and lead margin for the taunt toast."""
    groups = _leaderboard_groups(request.user)
    if not groups:
        return JsonResponse({})

    import random
    group = random.choice(groups)
    entries = leaderboard_service.overall_leaderboard(group)

    if len(entries) < 2 or entries[0]['points'] == 0:
        return JsonResponse({})

    leader = entries[0]
    second = entries[1]
    lead = leader['points'] - second['points']
    name = leader['user'].get_full_name() or leader['user'].username

    return JsonResponse({
        'name': name,
        'points': leader['points'],
        'lead': lead,
        'group': group.name,
        'is_me': leader['user'] == request.user,
    })


@staff_member_required
def manage_points(request):
    groups = list(ContestGroup.objects.filter(is_active=True))
    if not groups:
        return render(request, 'predictions/manage_points.html', {
            'groups': [], 'selected_group': None, 'entries': [], 'recent_adjustments': [],
        })

    if request.method == 'POST':
        selected_group = get_object_or_404(ContestGroup, id=request.POST.get('group_id'))
        target_user = get_object_or_404(get_user_model(), id=request.POST.get('user_id'))

        is_member = GroupMembership.objects.filter(
            user=target_user, group=selected_group, status=GroupMembership.Status.APPROVED
        ).exists()
        if not is_member:
            messages.error(request, 'That user is not an approved member of this group.')
        else:
            form = PointAdjustmentForm(request.POST)
            if form.is_valid():
                adjustment = form.save(commit=False)
                adjustment.user = target_user
                adjustment.transaction_type = PointTransaction.TransactionType.ADJUSTMENT
                adjustment.created_by = request.user
                adjustment.save()
                messages.success(
                    request,
                    f'Applied {adjustment.points:+d} points to '
                    f'{target_user.get_full_name() or target_user.username}.',
                )
            else:
                messages.error(request, 'Enter a non-zero point value and a reason for the adjustment.')

        return redirect(f"{reverse('predictions:manage_points')}?group={selected_group.id}")

    selected_group = _selected_group(request, groups)
    entries = leaderboard_service.overall_leaderboard(selected_group)

    recent_adjustments = PointTransaction.objects.filter(
        transaction_type=PointTransaction.TransactionType.ADJUSTMENT,
        user__in=[entry['user'] for entry in entries],
    ).select_related('user', 'created_by').order_by('-created_at')[:20]

    return render(request, 'predictions/manage_points.html', {
        'groups': groups,
        'selected_group': selected_group,
        'entries': entries,
        'recent_adjustments': recent_adjustments,
    })
