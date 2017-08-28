import rules


@rules.predicate
def is_email_owner(person, email):
    if email:
        return person == email.person
    else:
        return person.email_addresses.exists()
