#!/bin/bash

exec python create_database.py btcusdt &
exec python app.py