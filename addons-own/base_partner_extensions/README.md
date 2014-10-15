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
- Search for the Partner Number in any Form (not just for the display_name)


This module combines and port these v7 addons:
----------------------------------------------

- openat_partner_fullhierarchy
- openat_partnernumber_search_everywhere
- openat_partnernumber_unique