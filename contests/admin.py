from django.contrib import admin
from django.utils import timezone

from .models import ContestGroup, GroupMembership


class GroupMembershipInline(admin.TabularInline):
    model = GroupMembership
    extra = 0
    fields = ('user', 'status', 'requested_at', 'decided_at')
    readonly_fields = ('requested_at',)


@admin.register(ContestGroup)
class ContestGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'member_count', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)
    inlines = [GroupMembershipInline]

    @admin.display(description='Approved members')
    def member_count(self, obj):
        return obj.memberships.filter(status=GroupMembership.Status.APPROVED).count()


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'status', 'requested_at', 'decided_at')
    list_filter = ('status', 'group')
    search_fields = ('user__username', 'user__email', 'group__name')
    actions = ['approve_memberships', 'reject_memberships']

    @admin.action(description='Approve selected membership requests')
    def approve_memberships(self, request, queryset):
        updated = queryset.update(
            status=GroupMembership.Status.APPROVED, decided_at=timezone.now()
        )
        self.message_user(request, f'{updated} membership(s) approved.')

    @admin.action(description='Reject selected membership requests')
    def reject_memberships(self, request, queryset):
        updated = queryset.update(
            status=GroupMembership.Status.REJECTED, decided_at=timezone.now()
        )
        self.message_user(request, f'{updated} membership(s) rejected.')
