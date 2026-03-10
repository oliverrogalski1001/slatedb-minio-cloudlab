#!/bin/sh
set -e
# CloudLab Parameters
LICENSE=$1
ROOT_USER=$2
ROOT_PASS=$3

TARGET_DEV="/dev/sdb"
MOUNT_POINT="/mnt/minio"

# Wait for internet connectivity before proceeding
echo "Checking for internet connectivity..."
MAX_RETRIES=30
RETRY_INTERVAL=10
attempt=0
while ! curl -s --max-time 5 -o /dev/null https://dl.min.io; do
  attempt=$((attempt + 1))
  if [ "$attempt" -ge "$MAX_RETRIES" ]; then
    echo "ERROR: No internet connectivity after $MAX_RETRIES attempts. Aborting."
    exit 1
  fi
  echo "No internet connection (attempt $attempt/$MAX_RETRIES). Retrying in ${RETRY_INTERVAL}s..."
  sleep "$RETRY_INTERVAL"
done
echo "Internet connectivity confirmed."

echo "$LICENSE" >/local/minio.license

if [ -b "$TARGET_DEV" ]; then
  echo "Formatting $TARGET_DEV..."
  # Create a single partition using the whole disk
  sudo parted -s "$TARGET_DEV" mklabel gpt mkpart primary xfs 0% 100%

  # Format the partition with XFS (MinIO's recommended FS)
  # Using -f to force if a filesystem already exists
  sudo mkfs.xfs -f "${TARGET_DEV}1"

  # Create Mount Point
  sudo mkdir -p "$MOUNT_POINT"

  # Get UUID for persistent mounting in /etc/fstab
  UUID=$(sudo blkid -s UUID -o value "${TARGET_DEV}1")
  echo "UUID=$UUID $MOUNT_POINT xfs defaults,noatime 0 2" | sudo tee -a /etc/fstab

  # Mount the drive
  sudo mount -a
  echo "Disk $TARGET_DEV mounted successfully at $MOUNT_POINT"
else
  echo "Error: $TARGET_DEV not found. Falling back to OS drive directory."
  sudo mkdir -p "$MOUNT_POINT"
fi

sudo curl -L dl.min.io/aistor/minio/release/linux-amd64/minio.deb -o /local/minio.deb
sudo dpkg -i /local/minio.deb

cat <<EOF | sudo tee /etc/default/minio
MINIO_VOLUMES="$MOUNT_POINT"

MINIO_ROOT_USER="${ROOT_USER}"
MINIO_ROOT_PASSWORD="${ROOT_PASS}"

MINIO_LICENSE="/local/minio.license"
EOF

sudo mkdir -p /opt/minio
sudo chown -R minio-user:minio-user /opt/minio/
sudo chown -R minio-user:minio-user "$MOUNT_POINT"

sudo systemctl enable minio.service
sudo systemctl start minio
