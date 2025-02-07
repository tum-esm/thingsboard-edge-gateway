#!/bin/bash

ping -c 1 8.8.8.8

RETURN=$?

if [ $RETURN -eq 0 ];
then
  echo "Network connected. No need to reboot"
  exit 0
else
  echo "Network connection lost! Rebooting..."
  reboot
fi 
