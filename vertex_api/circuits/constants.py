from django.utils.translation import ugettext_lazy as _

# CircuitTermination sides
TERM_SIDE_A = 'A'
TERM_SIDE_Z = 'Z'
TERM_SIDE_CHOICES = (
    (TERM_SIDE_A, 'A'),
    (TERM_SIDE_Z, 'Z'),
)



# Contract Lenghts/Renewal
RENEWAL_MONTHLY = '1M'
RENEWAL_QUARTELY = '3M'
RENEWAL_BIANNUALLY = '6M'
RENEWAL_YEARLY = '1Y'
RENEWAL_TRIENNIALLY = '3Y'
RENEWAL_QUINQUENNIALLY = '5Y'

RENEWAL_TYPE_CHOICES = (
    (RENEWAL_MONTHLY, _('Every Month')),
    (RENEWAL_QUARTELY, _('Every 3 Months')),
    (RENEWAL_BIANNUALLY, _('Every 6 Months')),
    (RENEWAL_YEARLY, _('Every Year')),
    (RENEWAL_TRIENNIALLY, _('Every 3 Years')),
    (RENEWAL_QUINQUENNIALLY, _('Every 5 Years')),
)