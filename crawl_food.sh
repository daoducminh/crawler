#!/usr/bin/env bash
.venv/bin/python -m scrapy crawl food -a number=$1
