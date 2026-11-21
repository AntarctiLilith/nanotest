# Streaming Dashboard Docker Setup

## Overview

This Docker configuration allows you to run the streaming dashboard implementation locally using nginx.

## Prerequisites

- Docker Desktop installed on Windows
- Docker Compose installed

## How to Run

1. **Build and start the container:**
   ```bash
   docker-compose up -d
   ```

2. **Access the dashboard:**
   Open your browser and navigate to `http://localhost:8080`

3. **Stop the container:**
   ```bash
   docker-compose down
   ```

## Directory Structure

The Docker container will mount the current directory to `/usr/share/nginx/html` inside the container, so all files in this directory will be served.

## Configuration

The dashboard loads stream data from `data/streams.json`. You can modify this file to add or change streams.

## Notes

- The dashboard uses a simple nginx server
- All files are served statically
- The configuration system loads JSON data from the data directory

