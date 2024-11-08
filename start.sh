#!/bin/sh

alembic revision --autogenerate -m 'init'
alembic upgrade head

python -m main
