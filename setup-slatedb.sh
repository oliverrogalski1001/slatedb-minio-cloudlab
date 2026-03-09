#!/bin/sh
set -e

SLATEDB_REPO=$1
MINIO_USER=$2
MINIO_PASS=$3
MINIO_IP=$4
MINIO_BUCKET=$5

MINIO_ENDPOINT="http://${MINIO_IP}:9000"

# install rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# clone slatedb repo
git clone $SLATEDB_REPO

# install minio client
wget https://dl.min.io/aistor/mc/release/linux-amd64/mc -o mc
chmod +x ./mc
mv ./mc /usr/local/bin/

# wait for minio to be ready
echo "Waiting for MinIO at ${MINIO_ENDPOINT}..."
until mc alias set myminio "$MINIO_ENDPOINT" "$MINIO_USER" "$MINIO_PASS" 2>/dev/null; do
  sleep 5
done

# create the bucket
mc mb "myminio/${MINIO_BUCKET}" --ignore-existing

# write .env
cat <<EOF >.env
AWS_ACCESS_KEY_ID=${MINIO_USER}
AWS_SECRET_ACCESS_KEY=${MINIO_PASS}
AWS_REGION=us-east-1
AWS_BUCKET=${MINIO_BUCKET}
AWS_ENDPOINT=${MINIO_ENDPOINT}
AWS_ALLOW_HTTP=true
EOF
