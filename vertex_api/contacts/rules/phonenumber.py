import rules


@rules.predicate
def is_phone_number_owner(person, phone_number):
    if phone_number:
        return person == phone_number.person
    else:
        return person.phone_numbers.exists()
