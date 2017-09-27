import rules


@rules.predicate
def is_place_owner(person, place):
    if place:
        return person == place.person
    else:
        return person.places.exists()
