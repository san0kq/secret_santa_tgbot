#!/bin/sh

ALEMBIC_CONFIG_PATH="/app/alembic.ini"

alembic -c $ALEMBIC_CONFIG_PATH revision --autogenerate -m 'init'
alembic -c $ALEMBIC_CONFIG_PATH upgrade head