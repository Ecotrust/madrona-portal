#!/bin/bash

PROJ=/usr/local/apps/ocean_portal
ENV=$PROJ/wag_env;
PIP=$ENV/bin/pip;

# 1_07
$PIP uninstall wagtail -y
$PIP uninstall Willow -y
$PIP install "Willow<0.5"
$PIP install "wagtail==1.7"
