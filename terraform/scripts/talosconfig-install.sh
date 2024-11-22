#!/bin/bash

mkdir -p ~/.talos
echo "${talosconfig}" > ~/.talos/config
chmod 600 ~/.talos/config
