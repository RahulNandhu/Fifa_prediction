from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from predictions.models import Prediction
from predictions.services import process_match_result

from .forms import FixtureForm, MatchResultForm, PenaltyResultForm
from .models import Fixture, Match, Outcome


@login_required
def upcoming(request):
    now = timezone.now()

    match_qs = Match.objects.filter(published=True).select_related('fixture')
    if not request.user.is_staff:
        match_qs = match_qs.filter(fixture__kickoff_at__gte=now)
    matches = match_qs.order_by('fixture__kickoff_at')

    my_predictions = {
        p.match_id: p
        for p in Prediction.objects.filter(user=request.user, match__in=matches)
    }

    rows = []
    for match in matches:
        deadline_passed = now >= match.prediction_deadline
        prediction = my_predictions.get(match.id)
        predictions_qs = match.predictions.all()
        predictions_count = predictions_qs.count()

        stats = None
        if deadline_passed and predictions_count:
            counts = {Outcome.HOME: 0, Outcome.AWAY: 0, Outcome.DRAW: 0}
            for p in predictions_qs:
                counts[p.predicted_winner] += 1
            stats = {
                'home_pct': round(counts[Outcome.HOME] * 100 / predictions_count),
                'draw_pct': round(counts[Outcome.DRAW] * 100 / predictions_count),
                'away_pct': round(counts[Outcome.AWAY] * 100 / predictions_count),
            }

        rows.append({
            'match': match,
            'deadline_passed': deadline_passed,
            'prediction': prediction,
            'predictions_count': predictions_count,
            'stats': stats,
        })

    unpublished_fixtures = None
    if request.user.is_staff:
        unpublished_fixtures = (
            Fixture.objects.filter(Q(match__isnull=True) | Q(match__published=False))
            .select_related('home_team', 'away_team')
            .order_by('kickoff_at')
        )

    return render(request, 'matches/upcoming.html', {
        'rows': rows,
        'unpublished_fixtures': unpublished_fixtures,
    })


@staff_member_required
def create_fixture(request):
    if request.method == 'POST':
        form = FixtureForm(request.POST)
        if form.is_valid():
            fixture = form.save()
            messages.success(
                request,
                f'Fixture "{fixture}" created. Publish it from the Admin Panel to make it visible to users.',
            )
            return redirect('matches:create_fixture')
    else:
        form = FixtureForm()

    return render(request, 'matches/fixture_form.html', {'form': form})


@staff_member_required
def edit_fixture(request, fixture_id):
    fixture = get_object_or_404(Fixture, id=fixture_id)
    if request.method == 'POST':
        form = FixtureForm(request.POST, instance=fixture)
        if form.is_valid():
            form.save()
            messages.success(request, f'Fixture "{fixture}" updated.')
            return redirect('matches:upcoming')
    else:
        form = FixtureForm(instance=fixture)

    return render(request, 'matches/fixture_form.html', {'form': form, 'editing': True, 'fixture': fixture})


@staff_member_required
def delete_fixture(request, fixture_id):
    fixture = get_object_or_404(Fixture, id=fixture_id)
    if request.method == 'POST':
        name = str(fixture)
        fixture.delete()
        messages.success(request, f'Fixture "{name}" deleted.')
    return redirect('matches:upcoming')


@staff_member_required
def publish_fixture(request, fixture_id):
    fixture = get_object_or_404(Fixture, id=fixture_id)

    if request.method == 'POST':
        match, _ = Match.objects.get_or_create(fixture=fixture)
        if not match.published:
            match.published = True
            match.save(update_fields=['published'])
            messages.success(request, f'"{fixture}" is now published and visible to users.')
        else:
            messages.info(request, f'"{fixture}" is already published.')

    return redirect('matches:upcoming')


@staff_member_required
def unpublish_match(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    if request.method == 'POST':
        match.published = False
        match.save(update_fields=['published'])
        messages.success(request, f'"{match.fixture}" has been unpublished.')

    return redirect('matches:upcoming')


@staff_member_required
def submit_results(request):
    if request.method == 'POST':
        match = get_object_or_404(Match, id=request.POST.get('match_id'), published=True)
        save_type = request.POST.get('save_type', 'result')

        if save_type == 'penalty':
            form = PenaltyResultForm(request.POST, instance=match)
            if form.is_valid():
                form.save()
                process_match_result(match)
                messages.success(
                    request,
                    f'Penalty result saved for "{match.fixture}" '
                    f'({match.penalty_home_score} - {match.penalty_away_score}). '
                    f'Points have been recalculated.',
                )
        else:
            form = MatchResultForm(request.POST, instance=match)
            if form.is_valid():
                saved = form.save(commit=False)
                if saved.home_score != saved.away_score:
                    saved.penalty_home_score = None
                    saved.penalty_away_score = None
                saved.save()
                if match.has_result:
                    process_match_result(match)
                    messages.success(
                        request,
                        f'Result saved for "{match.fixture}" ({match.home_score} - {match.away_score}). '
                        f'Points have been recalculated for all groups.',
                    )
                else:
                    messages.success(request, f'Result saved for "{match.fixture}".')
        return redirect('matches:submit_results')

    matches = (
        Match.objects.filter(published=True)
        .select_related('fixture', 'fixture__home_team', 'fixture__away_team')
        .order_by('fixture__kickoff_at')
    )
    rows = [
        {
            'match': match,
            'form': MatchResultForm(instance=match),
            'penalty_form': PenaltyResultForm(instance=match),
        }
        for match in matches
    ]

    return render(request, 'matches/submit_results.html', {'rows': rows})
