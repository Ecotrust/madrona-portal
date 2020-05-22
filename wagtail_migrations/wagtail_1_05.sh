#!/bin/bash

PROJ=/usr/local/apps/ocean_portal
ENV=$PROJ/wag_env;
PIP=$ENV/bin/pip;

# 1_05
$PIP uninstall wagtail -y
$PIP uninstall django-modelcluster -y
$PIP install "django-modelcluster==2.0"
$PIP install "wagtail==1.5.3"
