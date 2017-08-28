import rules


@rules.predicate
def is_url_owner(person, url):
    if url:
        return person == url.person
    else:
        return person.urls.exists()
