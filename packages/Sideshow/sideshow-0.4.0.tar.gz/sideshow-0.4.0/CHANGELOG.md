## v0.4.0 (2025-01-23)

### Feat

- add initial workflow master views, UI features
- add tools to change order item status; add notes
- add initial support for order item events

### Fix

- customize "view order item" page w/ panels
- add loading overlay for expensive calls in orders/create
- hide local customer when not applicable, for order view

## v0.3.0 (2025-01-13)

### Feat

- move lookup logic to handler; improve support for external lookup

### Fix

- expose new order batch handler choice in orders/configure
- add "Other" menu, for e.g. integration system links
- bugfix when new order with no pending customer

## v0.2.0 (2025-01-09)

### Feat

- add basic support for local customer, product lookups

### Fix

- expose config for new order w/ pending product

## v0.1.0 (2025-01-06)

### Feat

- add basic "create order" feature, docs, tests

### Fix

- add static libcache files for vue2 + buefy
