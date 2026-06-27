from .models import KnockoutModalDismissal


def knockout_modal(request):
    if not request.user.is_authenticated:
        return {'show_knockout_modal': False, 'show_admin_knockout_modal': False}

    pref = KnockoutModalDismissal.objects.filter(user=request.user).first()

    if request.user.is_staff:
        return {
            'show_knockout_modal': False,
            'show_admin_knockout_modal': not (pref and pref.admin_dismissed),
        }

    return {
        'show_knockout_modal': not (pref and pref.dismissed),
        'show_admin_knockout_modal': False,
    }
