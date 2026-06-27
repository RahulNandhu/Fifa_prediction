from django.contrib import admin

from predictions.services import process_match_result

from .models import Fixture, Match, Team


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('flag', 'name', 'code')
    search_fields = ('name', 'code')
    ordering = ('name',)


@admin.register(Fixture)
class FixtureAdmin(admin.ModelAdmin):
    list_display = ('home_team', 'away_team', 'kickoff_at', 'stage', 'venue', 'is_knockout', 'is_published')
    list_filter = ('stage', 'is_knockout')
    search_fields = ('home_team__name', 'away_team__name')
    ordering = ('kickoff_at',)
    autocomplete_fields = ('home_team', 'away_team')
    actions = ['publish_fixtures']

    class Media:
        js = ('admin/js/fixture_knockout.js',)

    @admin.display(description='Published', boolean=True)
    def is_published(self, obj):
        return getattr(obj, 'match', None) is not None and obj.match.published

    @admin.action(description='Publish selected fixtures (create/show matches)')
    def publish_fixtures(self, request, queryset):
        count = 0
        for fixture in queryset:
            match, _ = Match.objects.get_or_create(fixture=fixture)
            if not match.published:
                match.published = True
                match.save(update_fields=['published'])
                count += 1
        self.message_user(request, f'{count} fixture(s) published.')


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = (
        'fixture', 'kickoff_at', 'published', 'fixture_is_knockout', 'prediction_deadline',
        'home_score', 'away_score', 'result_processed',
    )
    list_filter = ('published', 'result_processed')
    search_fields = ('fixture__home_team__name', 'fixture__away_team__name')
    actions = ['publish_matches', 'unpublish_matches', 'recalculate_results']
    fields = (
        'fixture', 'published',
        'home_score', 'away_score',
        'penalty_home_score', 'penalty_away_score',
        'result_processed',
    )
    readonly_fields = ('result_processed',)

    @admin.display(description='Knockout', boolean=True)
    def fixture_is_knockout(self, obj):
        return obj.fixture.is_knockout

    @admin.action(description='Publish selected matches')
    def publish_matches(self, request, queryset):
        updated = queryset.update(published=True)
        self.message_user(request, f'{updated} match(es) published.')

    @admin.action(description='Unpublish selected matches')
    def unpublish_matches(self, request, queryset):
        updated = queryset.update(published=False)
        self.message_user(request, f'{updated} match(es) unpublished.')

    @admin.action(description='Recalculate points for selected results')
    def recalculate_results(self, request, queryset):
        count = 0
        for match in queryset:
            if match.has_result:
                process_match_result(match)
                count += 1
        self.message_user(request, f'Recalculated points for {count} match(es).')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.has_result:
            process_match_result(obj)
