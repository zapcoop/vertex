from django.utils.translation import ugettext_lazy as _

GENERIC_INFORMATION_TYPES = (
    ('assistant', _("Assistant")),
    ('business', _("Business")),
    ('business-other', _("Business, other")),
    ('company', _("Company")),
    ('home', _("Home")),
    ('home-other', _("Home, other")),
    ('other', _("Other")),
    ('primary', _("Primary")),
)

PHONE_SPECIFIC_INFORMATION_TYPES = (
    ('business-fax', _("Business fax")),
    ('callback', _("Callback")),
    ('car', _("Car")),
    ('home-fax', _("Home fax")),
    ('isdn', _("ISDN")),
    ('mobile', _("Mobile")),
    ('other-fax', _("Other fax")),
    ('pager', _("Pager")),
    ('radio', _("Radio")),
    ('tty-tdd', _("TTY/TDD")),

)
URL_SPECIFIC_INFORMATION_TYPES = (
    (_("Social media"), (
        ('apple', "Apple"),
        ('behance', "Behance"),
        ('bitbucket', "BitBucket"),
        ('delicious', "Delicious"),
        ('deviantart', "DeviantArt"),
        ('facebook', "Facebook"),
        ('flickr', "Flickr"),
        ('github', "Github"),
        ('googleplus', "Google+"),
        ('instagram', "Instagram"),
        ('linkedin', "LinkedIn"),
        ('pinterest', "Pinterest"),
        ('reddit', "Reddit"),
        ('tumblr', "Tumblr"),
        ('twitter', "Twitter"),
        ('youtube', "YouTube"),
    )),
    (_("Web site"), (
        GENERIC_INFORMATION_TYPES
    ))
)

