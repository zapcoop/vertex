import rules


@rules.predicate
def is_note_creator(person, note):
    return note.posted_by == person
