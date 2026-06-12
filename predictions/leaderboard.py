from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Sum

from contests.models import GroupMembership
from .models import PointTransaction

User = get_user_model()


def _approved_users(group):
    user_ids = GroupMembership.objects.filter(
        group=group, status=GroupMembership.Status.APPROVED
    ).values_list('user_id', flat=True)
    return User.objects.filter(id__in=user_ids)


def _rank(entries):
    rank = 0
    last_points = None
    for entry in entries:
        if entry['points'] != last_points:
            rank += 1
            last_points = entry['points']
        entry['rank'] = rank
    return entries


def week_start(date):
    """Return the Monday of the week containing the given date."""
    return date - timedelta(days=date.weekday())


def overall_leaderboard(group):
    totals = dict(
        PointTransaction.objects.filter(user__in=_approved_users(group))
        .values('user')
        .annotate(total=Sum('points'))
        .values_list('user', 'total')
    )

    entries = []
    for user in _approved_users(group):
        entries.append({'user': user, 'points': totals.get(user.id, 0)})

    entries.sort(key=lambda e: (-e['points'], e['user'].get_full_name() or e['user'].username))
    return _rank(entries)


def available_weeks(group):
    dates = PointTransaction.objects.filter(
        user__in=_approved_users(group)
    ).select_related('match__fixture')

    weeks = set()
    for txn in dates:
        weeks.add(week_start(txn.week_date))

    return sorted(weeks, reverse=True)


def weekly_leaderboard(group, week_start_date):
    week_end_date = week_start_date + timedelta(days=7)

    approved_users = _approved_users(group)
    totals = {}
    for txn in PointTransaction.objects.filter(user__in=approved_users).select_related('match__fixture'):
        if week_start_date <= txn.week_date < week_end_date:
            totals[txn.user_id] = totals.get(txn.user_id, 0) + txn.points

    entries = []
    for user in approved_users:
        entries.append({'user': user, 'points': totals.get(user.id, 0)})

    entries.sort(key=lambda e: (-e['points'], e['user'].get_full_name() or e['user'].username))
    return _rank(entries)
