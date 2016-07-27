Filesystem Structure
----
```
/
|- Docs/    .   .   .   .   .   Documentation files
|- OrderSystem/
    |- forms/   .   .   .   .   WTForms
    |- routing/ .   .   .   .   Route definitions
    |- sql/ .   .   .   .   .   MySQL database code
        |- ORM/ .   .   .   .   ORMs (Object Relational Mappings) -- defines DB relations (table) structure
    |
    |- static/  .   .   .   .   Static content
        |- css/ .   .   .   .   CSS meant for production. Mostly our custom overrides
        |- js/  .   .   .   .   JavaScript meant for production. Also mostly our custom scripts
        |- img/ .   .   .   .   Images meant for production
        |- scss/    .   .   .   SCSS files
    |
    |- templates/   .   .   .   Jinja2 templates
    |- Utilities/   .   .   .   Collection of various helper scripts
|- scripts/     .   .   .   .   Other scripts that run outside the application context
|- logs/    .   .   .   .   .   Application logs
```