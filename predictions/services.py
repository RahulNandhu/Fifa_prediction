from django.db import transaction

from matches.models import Outcome

from .models import PointTransaction, Prediction

WINNER_POINTS = 2
EXACT_SCORE_POINTS = 2
BOTH_CORRECT_BONUS = 1
PENALTY_POINTS = 2
ALL_THREE_CORRECT_BONUS = 1


def calculate_points(prediction, match):
    """Return points earned by a prediction given the match's actual result."""
    winner_correct = prediction.predicted_winner == match.actual_winner
    score_correct = (
        prediction.predicted_home_score == match.home_score
        and prediction.predicted_away_score == match.away_score
    )

    points = 0
    if winner_correct:
        points += WINNER_POINTS
    if score_correct:
        points += EXACT_SCORE_POINTS
    if winner_correct and score_correct:
        points += BOTH_CORRECT_BONUS

    if match.is_knockout and match.has_penalty_result:
        if prediction.predicted_winner == Outcome.DRAW:
            penalty_correct = (
                prediction.predicted_penalty_home_score == match.penalty_home_score
                and prediction.predicted_penalty_away_score == match.penalty_away_score
            )
            if penalty_correct:
                points += PENALTY_POINTS
                if winner_correct and score_correct:
                    points += ALL_THREE_CORRECT_BONUS

    return points


@transaction.atomic
def process_match_result(match):
    """Calculate and award points for every prediction on a completed match.

    Safe to call again (e.g. after a score correction): previously awarded
    PREDICTION transactions for this match are removed and recreated.
    """
    if not match.has_result:
        return

    PointTransaction.objects.filter(
        match=match, transaction_type=PointTransaction.TransactionType.PREDICTION
    ).delete()

    for prediction in Prediction.objects.filter(match=match).select_related('user'):
        points = calculate_points(prediction, match)
        prediction.points_awarded = points
        prediction.save(update_fields=['points_awarded'])

        if points:
            PointTransaction.objects.create(
                user=prediction.user,
                points=points,
                transaction_type=PointTransaction.TransactionType.PREDICTION,
                reason=(
                    f'Prediction for {match.home_team} {match.home_score} - '
                    f'{match.away_score} {match.away_team}'
                ),
                match=match,
            )

    match.result_processed = True
    match.save(update_fields=['result_processed'])
