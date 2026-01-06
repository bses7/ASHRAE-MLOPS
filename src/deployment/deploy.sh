set -e

# =====================================================
# 7. Application Containers
# =====================================================
echo "--------------------------------"
echo "Starting Application Containers..."
echo "--------------------------------"

docker-compose -f docker-compose-app.yaml up -d

docker ps | grep ashrae
