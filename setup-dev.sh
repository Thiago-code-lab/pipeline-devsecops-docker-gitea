#!/bin/bash

# Create required directories
echo "Creating required directories..."
mkdir -p logs uploads monitoring/grafana/provisioning/dashboards

# Set permissions
echo "Setting permissions..."
chmod -R 755 logs uploads monitoring

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    
    # Generate secure secrets
    echo "Generating secure secrets..."
    sed -i "s/SECRET_KEY=.*/SECRET_KEY=$(openssl rand -hex 32)/" .env
    sed -i "s/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$(openssl rand -hex 32)/" .env
    sed -i "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$(openssl rand -base64 20 | tr -d '\n')/" .env
    sed -i "s/REDIS_PASSWORD=.*/REDIS_PASSWORD=$(openssl rand -base64 20 | tr -d '\n')/" .env
    
    echo "Please review the generated .env file and update any values as needed."
fi

# Create Docker network if it doesn't exist
echo "Creating Docker network if needed..."
docker network create app-network 2>/dev/null || true

# Install pre-commit hooks
echo "Setting up pre-commit hooks..."
pip install pre-commit
pre-commit install

echo "Development environment setup complete!"
echo "1. Review the .env file"
echo "2. Run 'docker-compose up -d' to start the services"
echo "3. Run 'docker-compose logs -f app' to follow the application logs"
