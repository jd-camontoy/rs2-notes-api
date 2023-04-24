#!/bin/sh

exec python create_database.py btcusdt &
exec python app.py