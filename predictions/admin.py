from django.contrib import admin

from .models import PointTransaction, Prediction


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'match', 'predicted_home_score', 'predicted_away_score',
        'predicted_winner', 'points_awarded', 'updated_at',
    )
    list_filter = ('match__fixture__stage', 'match')
    search_fields = ('user__username', 'user__email')
    ordering = ('-match__fixture__kickoff_at',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'points', 'transaction_type', 'reason', 'match', 'created_by', 'created_at',
    )
    list_filter = ('transaction_type',)
    search_fields = ('user__username', 'user__email', 'reason')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

    def get_fields(self, request, obj=None):
        if obj is None:
            # Manual adjustments only - PREDICTION transactions are system generated.
            return ('user', 'points', 'reason')
        return ('user', 'points', 'transaction_type', 'reason', 'match', 'created_by', 'created_at')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.transaction_type = PointTransaction.TransactionType.ADJUSTMENT
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def has_change_permission(self, request, obj=None):
        if obj is not None and obj.transaction_type == PointTransaction.TransactionType.PREDICTION:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.transaction_type == PointTransaction.TransactionType.PREDICTION:
            return False
        return super().has_delete_permission(request, obj)
