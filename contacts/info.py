from noss.info import Info, InfoItem
from noss import rules

Info.add_item(
    "apps",
    InfoItem(
        "contacts",
        children=(
            InfoItem(
                "organizations",
                lambda user: user.has_perm('contacts.view_organization')
            ),
        ),
    )
)
