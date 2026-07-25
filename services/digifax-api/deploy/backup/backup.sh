#!/bin/bash
set -eo pipefail

# Configuration parameters
BACKUP_DIR="/var/backups/digifax"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_BACKUP_FILE="${BACKUP_DIR}/db_backup_${TIMESTAMP}.sql"
STORAGE_BACKUP_DIR="${BACKUP_DIR}/storage_backup_${TIMESTAMP}"

# Database parameters
DB_HOST=${DATABASE_HOST:-"postgres-service"}
DB_USER=${DATABASE_USER:-"postgres"}
DB_NAME=${DATABASE_NAME:-"digifax"}

# MinIO storage parameters
MINIO_ALIAS=${MINIO_ALIAS:-"digifax-store"}
MINIO_ENDPOINT=${MINIO_ENDPOINT:-"http://minio-service:9000"}
MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY:-"minioadmin"}
MINIO_SECRET_KEY=${MINIO_SECRET_KEY:-"minioadminpassword"}

echo "=== Starting DigiFax Production Backup: ${TIMESTAMP} ==="
mkdir -p "${BACKUP_DIR}"

# 1. Database Backup (pg_dump)
echo "Backing up PostgreSQL database: ${DB_NAME} from host ${DB_HOST}..."
PGPASSWORD=${DATABASE_PASSWORD:-"password123"} pg_dump -h "${DB_HOST}" -U "${DB_USER}" -d "${DB_NAME}" -F c -b -v -f "${DB_BACKUP_FILE}"
echo "PostgreSQL database backup completed: ${DB_BACKUP_FILE}"

# 2. MinIO Storage Backup (mc mirror)
echo "Backing up MinIO buckets..."
if command -v mc &> /dev/null; then
    # Configure minio client session
    mc alias set "${MINIO_ALIAS}" "${MINIO_ENDPOINT}" "${MINIO_ACCESS_KEY}" "${MINIO_SECRET_KEY}" --api S3v4
    
    # Mirror all buckets locally
    mkdir -p "${STORAGE_BACKUP_DIR}"
    mc mirror "${MINIO_ALIAS}" "${STORAGE_BACKUP_DIR}"
    echo "MinIO buckets mirrored to: ${STORAGE_BACKUP_DIR}"
else
    echo "WARNING: MinIO client utility (mc) is not installed. Skipping MinIO mirroring backup."
fi

# 3. Cleanup older backups (keep last 7 days)
echo "Cleaning up backups older than 7 days..."
find "${BACKUP_DIR}" -type f -mtime +7 -delete
find "${BACKUP_DIR}" -type d -empty -mtime +7 -delete

echo "=== Backup Process Completed Successfully ==="
exit 0
