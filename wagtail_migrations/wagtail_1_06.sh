#!/bin/bash

PROJ=/usr/local/apps/ocean_portal
ENV=$PROJ/wag_env;
PIP=$ENV/bin/pip;

# 1_06
$PIP uninstall wagtail -y
$PIP install "wagtail==1.6.3"
