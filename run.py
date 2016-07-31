from OrderSystem import app

"""
  ___          _           ____            _
 / _ \ _ __ __| | ___ _ __/ ___| _   _ ___| |_ ___ _ __ ___
| | | | '__/ _` |/ _ \ '__\___ \| | | / __| __/ _ \ '_ ` _ \
| |_| | | | (_| |  __/ |   ___) | |_| \__ \ ||  __/ | | | | |
 \___/|_|  \__,_|\___|_|  |____/ \__, |___/\__\___|_| |_| |_|
                                 |___/

     Developed by M. Turi
     Copyright (C) 2015-2017
"""

"""
--- NOTICE ---
This file is only for running the site in development mode, on a development machine.
DO NOT USE THIS FILE TO RUN A PRODUCTION SERVER
"""

app.run(
    debug=True,
    port=1337
)
