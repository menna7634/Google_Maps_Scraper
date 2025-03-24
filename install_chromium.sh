#!/bin/bash

# Update package list and install Chromium and dependencies
apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    libx11-xcb1 \
    libnss3 \
    libgdk-pixbuf2.0-0 \
    libxss1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*
