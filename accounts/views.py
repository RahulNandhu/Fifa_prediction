from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from contests.models import GroupMembership
from matches.models import Match
from predictions.leaderboard import overall_leaderboard
from predictions.models import Prediction

from .forms import RegisterForm


def register(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome! Your account has been created.')
            return redirect('contests:groups')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def dashboard(request):
    now = timezone.now()

    upcoming_matches = (
        Match.objects.filter(published=True, fixture__kickoff_at__gte=now)
        .select_related('fixture')
        .order_by('fixture__kickoff_at')[:5]
    )

    predicted_match_ids = set(
        Prediction.objects.filter(user=request.user, match__in=upcoming_matches)
        .values_list('match_id', flat=True)
    )

    memberships = GroupMembership.objects.filter(user=request.user).select_related('group')

    leaderboard_summaries = []
    for membership in memberships:
        if membership.status == GroupMembership.Status.APPROVED:
            entries = overall_leaderboard(membership.group)
            my_entry = next((e for e in entries if e['user'] == request.user), None)
            leaderboard_summaries.append({
                'group': membership.group,
                'rank': my_entry['rank'] if my_entry else None,
                'points': my_entry['points'] if my_entry else 0,
                'total_participants': len(entries),
            })

    context = {
        'upcoming_matches': upcoming_matches,
        'predicted_match_ids': predicted_match_ids,
        'memberships': memberships,
        'leaderboard_summaries': leaderboard_summaries,
    }
    return render(request, 'accounts/dashboard.html', context)
