#!/bin/bash
python -m vesta --token $TOKEN --postgres $POSTGRES_USER:$POSTGRES_PASSWORD@postgres/$POSTGRES_DATABASE -l $LOGGING_LEVEL