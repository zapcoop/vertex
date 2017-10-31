import graphene


class CreateOrganization(graphene.relay.ClientIDMutation):

    class Input:
        name = graphene.String(required=True)
        faction_id = graphene.String(required=True)

    ship = graphene.Field(Ship)
    faction = graphene.Field(Faction)

    @classmethod
    def mutate_and_get_payload(cls, root, info, ship_name, faction_id, client_mutation_id=None):
        ship = create_ship(ship_name, faction_id)
        faction = get_faction(faction_id)
        return IntroduceShip(ship=ship, faction=faction)