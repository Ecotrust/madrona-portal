#!/bin/bash

PROJ=/usr/local/apps/ocean_portal
ENV=$PROJ/wag_env;
PIP=$ENV/bin/pip;

# 1_04
$PIP uninstall wagtail -y
$PIP uninstall Willow -y
$PIP install "Willow==0.3.1"
$PIP install "wagtail==1.4.6"
