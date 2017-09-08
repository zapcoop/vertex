from django.apps import apps
import rules


@rules.predicate
def is_team_member(person, team):
    # can't import Department because this would create a circular import dependency
    Team = apps.get_model('service', 'Team')

    if team:
        return Team.objects.filter(
            allowed_organization_departments__people=person
        ).filter(pk=team.pk).exists()
    else:
        return Team.objects.filter(
            allowed_organization_departments__people=person
        ).exists()


@rules.predicate
def is_ticket_team_member(person, ticket):
    Team = apps.get_model('service', 'Team')

    if not ticket:
        return Team.objects.filter(
            allowed_organization_departments__people=person
        ).exists()

    Team.objects.filter(
        allowed_organization_departments__people=person
    ).filter(pk__in=ticket.teams.values_list('pk', flat=True)).exists()
