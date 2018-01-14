Filesystem Structure
----
```
/
|- configuration    .   .   .   Configuration files (Generated after running setup scripts)
|- Docs/    .   .   .   .   .   Documentation files
|- logs/    .   .   .   .   .   Application logs
|- migrations   .   .   .   .   SQL migrations
|- OrderSystem/
    |- forms/   .   .   .   .   WTForms
    |- routing/ .   .   .   .   Route definitions
    |- sql/ORM  .   .   .   .   ORMs (Object Relational Mappings) -- defines DB relations (table) structure
    |- static/  .   .   .   .   Static content
        |- css/ .   .   .   .   CSS meant for production. Mostly our custom overrides
        |- js/  .   .   .   .   JavaScript meant for production. Also mostly our custom scripts
        |- img/ .   .   .   .   Images meant for production
        |- scss/    .   .   .   SCSS files
        |- robots.txt   .   .   robots.txt file
    |
    |- templates/   .   .   .   Jinja2 templates
    |- utilities/   .   .   .   Collection of various helper scripts
|- scripts/     .   .   .   .   Other scripts that run outside the application context
|- setup/       .   .   .   .   Scripts to setup the system environment for the rest of the order system
```