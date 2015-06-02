base_partner_extensions
=======================

This addon will add some tweaks to res.partner so the address book of odoo. It serves as a base for all extensions and
changes added to res.partner and its related views and forms.

Tasks:
------

- Allow full hierarchy 
    - Also use non company addresses as parent
    - Full interface to set parent company in quick create mask
- Allow to always set the address type (Default, Delivery ...)
- Force the Partner Number to be unique
- Maybe use a partner sequence by default - see oca: base_partner_sequence
- Search for the Partner Number in any Form (not just for the display_name)
- Show what kind of address it is in search fields (e.g. commercial) - see initos partner_extended_name


This module combines and port these v7 addons:
----------------------------------------------

- openat_partner_fullhierarchy
- openat_partnernumber_search_everywhere
- openat_partnernumber_unique

This external addons could be helpfull:
- https://github.com/OCA/partner-contact/tree/8.0/partner_firstname
- https://github.com/OCA/partner-contact/tree/8.0/base_partner_sequence
- https://github.com/OCA/partner-contact/tree/8.0/partner_contact_address_detailed
- http://bazaar.launchpad.net/~initos.com/initos.com-openerp-addons/7.0/view/head:/partner_extended_name/res_partner.py
