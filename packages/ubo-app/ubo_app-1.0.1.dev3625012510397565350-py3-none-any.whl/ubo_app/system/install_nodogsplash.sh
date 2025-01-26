#!/bin/bash

set -o xtrace
set -o errexit
set -o pipefail
set -o nounset

# Variables
REPO="sassanh/nodogsplash" # TODO replace with "nodogsplash/nodogsplash"
ASSET_NAME="nodogsplash_.*_arm64.deb"  # Regex pattern for the desired asset

# Fetch the latest release data from GitHub API
API_URL="https://api.github.com/repos/$REPO/releases/latest"
RELEASE_DATA=$(curl -s $API_URL)

# Extract the download URL for the desired asset
DOWNLOAD_URL=$(echo "$RELEASE_DATA" | grep -oP '"browser_download_url": "\K(.*?'"$ASSET_NAME"')' | head -n 1)

if [ -z "$DOWNLOAD_URL" ]; then
  echo "No matching asset found in the latest release."
  exit 1
fi

# Download the asset
echo "Downloading from: $DOWNLOAD_URL"
curl -L -o $(basename $DOWNLOAD_URL) $DOWNLOAD_URL

echo "Download completed: $(basename $DOWNLOAD_URL)"

echo "Installing the package"
dpkg -i $(basename $DOWNLOAD_URL) || true

echo "Fixing dependencies"
apt-get -y install -f

echo "Cleaning up"
apt-get -y clean
rm -f $(basename $DOWNLOAD_URL)
