#!/usr/bin/env bash
date=$(date +%Y-%m-%d)
filename="${date}.sql"
mysqldump --bind-address=192.168.1.105 --user=root --password=NuStar_Orient123 --host=localhost --protocol=tcp --port=3306 --default-character-set=utf8 --events --skip-triggers "oasis_web">/home/django/backup/${filename}