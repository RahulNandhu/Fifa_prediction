from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import ContestGroupForm
from .models import ContestGroup, GroupMembership


@login_required
def groups(request):
    all_groups = ContestGroup.objects.filter(is_active=True)
    memberships = {
        m.group_id: m
        for m in GroupMembership.objects.filter(user=request.user)
    }

    group_rows = [
        {'group': group, 'membership': memberships.get(group.id)}
        for group in all_groups
    ]

    pending_requests = None
    if request.user.is_staff:
        pending_requests = (
            GroupMembership.objects.filter(status=GroupMembership.Status.PENDING)
            .select_related('user', 'group')
            .order_by('requested_at')
        )

    return render(request, 'contests/groups.html', {
        'group_rows': group_rows,
        'pending_requests': pending_requests,
    })


@login_required
def request_join(request, group_id):
    group = get_object_or_404(ContestGroup, id=group_id, is_active=True)

    if request.user.is_staff:
        messages.error(request, 'Admin accounts cannot join contest groups.')
        return redirect('contests:groups')

    if request.method == 'POST':
        membership, created = GroupMembership.objects.get_or_create(
            user=request.user, group=group,
        )
        if created:
            messages.success(request, f'Your request to join "{group.name}" has been submitted.')
        elif membership.status == GroupMembership.Status.REJECTED:
            membership.status = GroupMembership.Status.PENDING
            membership.decided_at = None
            membership.save(update_fields=['status', 'decided_at'])
            messages.success(request, f'Your request to join "{group.name}" has been resubmitted.')
        else:
            messages.info(request, f'You already have a {membership.get_status_display().lower()} request for "{group.name}".')

    return redirect('contests:groups')


@staff_member_required
def create_group(request):
    if request.method == 'POST':
        form = ContestGroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            messages.success(request, f'Contest group "{group.name}" created.')
            return redirect('contests:groups')
    else:
        form = ContestGroupForm(initial={'is_active': True})

    return render(request, 'contests/group_form.html', {'form': form})


@staff_member_required
def approve_membership(request, membership_id):
    membership = get_object_or_404(
        GroupMembership, id=membership_id, status=GroupMembership.Status.PENDING
    )

    if request.method == 'POST':
        membership.status = GroupMembership.Status.APPROVED
        membership.decided_at = timezone.now()
        membership.save(update_fields=['status', 'decided_at'])
        messages.success(
            request, f'Approved {membership.user.username} for "{membership.group.name}".'
        )

    return redirect('contests:groups')


@staff_member_required
def reject_membership(request, membership_id):
    membership = get_object_or_404(
        GroupMembership, id=membership_id, status=GroupMembership.Status.PENDING
    )

    if request.method == 'POST':
        membership.status = GroupMembership.Status.REJECTED
        membership.decided_at = timezone.now()
        membership.save(update_fields=['status', 'decided_at'])
        messages.success(
            request, f'Rejected {membership.user.username} for "{membership.group.name}".'
        )

    return redirect('contests:groups')
