#!/bin/bash

source env/bin/activate;
export FLASK_APP=run.py;
export FLASK_CONFIG=development;
export AUTHLIB_INSECURE_TRANSPORT=True;

flask run --host 0.0.0.0
