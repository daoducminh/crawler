#!/usr/bin/env bash
dt=$(date '+%Y_%m_%d_%H_%M_%S')
mkdir -p /content/gdrive/MyDrive/Projects/it5230/$dt
.venv/bin/python -m scrapy crawl food -a number=$1 && cp -rf food/* /content/gdrive/MyDrive/Projects/it5230/