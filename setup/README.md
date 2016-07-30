The files in this directory are critical to setting up the backend of the OrderSystem
to work properly. The scripts are numbered using the following format
`setup[number].py`, where the `[number]` is denoting the order that the scripts
need to be run in.

Run the scripts in numerical order and you should be golden

-----
**Script Details**

`setup1.py` - Responsible for creating `configuration` directory and corresponding .ini config files

`setup2.py` - Responsible for creating database schema, adding initial subteam [`OrderSystemAdmin`], and
initial user [Username = `robotics-osa`; Password = `admin`]. Password needs to be reset for
admin user on initial login