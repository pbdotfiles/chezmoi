#!/bin/bash

# PPA: https://launchpad.net/~graphics-drivers/+archive/ubuntu/ppa
sudo add-apt-repository ppa:graphics-drivers/ppa
sudo apt update
sudo apt install nvidia-driver-560 nvtop -y
