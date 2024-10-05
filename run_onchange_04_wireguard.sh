#!/bin/bash

sudo apt install wireguard -y
sudo systemctl enable wg-quick@wg0
