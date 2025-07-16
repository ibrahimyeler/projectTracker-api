#!/bin/bash

# Project Tracker API Deployment Script
set -e

echo "🚀 Starting deployment..."

# Variables
PROJECT_NAME="project-tracker-api"
DOMAIN="api.projecttracker.ibrahimyeler.com"
GITHUB_REPO="your-username/project-tracker-api"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Update system
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
print_status "Installing required packages..."
sudo apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx postgresql postgresql-contrib

# Create project directory
print_status "Setting up project directory..."
sudo mkdir -p /opt/$PROJECT_NAME
sudo chown $USER:$USER /opt/$PROJECT_NAME

# Clone or update repository
if [ -d "/opt/$PROJECT_NAME/.git" ]; then
    print_status "Updating existing repository..."
    cd /opt/$PROJECT_NAME
    git pull origin main
else
    print_status "Cloning repository..."
    git clone https://github.com/$GITHUB_REPO.git /opt/$PROJECT_NAME
    cd /opt/$PROJECT_NAME
fi

# Setup virtual environment
print_status "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Setup PostgreSQL
print_status "Setting up PostgreSQL database..."
sudo -u postgres psql -c "CREATE DATABASE project_tracker;" || print_warning "Database might already exist"
sudo -u postgres psql -c "CREATE USER project_tracker WITH PASSWORD 'your_secure_password';" || print_warning "User might already exist"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE project_tracker TO project_tracker;"

# Create environment file
print_status "Creating environment configuration..."
cat > .env << EOF
DATABASE_URL=postgresql://project_tracker:your_secure_password@localhost:5432/project_tracker
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
ALLOWED_ORIGINS=https://$DOMAIN,https://www.$DOMAIN
HOST=0.0.0.0
PORT=8000
EOF

# Setup Nginx
print_status "Setting up Nginx..."
sudo cp nginx.conf /etc/nginx/sites-available/$PROJECT_NAME
sudo sed -i "s/yourdomain.com/$DOMAIN/g" /etc/nginx/sites-available/$PROJECT_NAME
sudo ln -sf /etc/nginx/sites-available/$PROJECT_NAME /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# Setup systemd service
print_status "Setting up systemd service..."
sudo cp project-tracker.service /etc/systemd/system/
sudo sed -i "s|/opt/project-tracker-api|/opt/$PROJECT_NAME|g" /etc/systemd/system/project-tracker.service
sudo systemctl daemon-reload
sudo systemctl enable project-tracker
sudo systemctl start project-tracker

# Setup SSL certificate
print_status "Setting up SSL certificate..."
sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email your-email@example.com

# Final checks
print_status "Performing final checks..."
sleep 5
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_status "✅ API is running successfully!"
else
    print_error "❌ API health check failed"
    sudo systemctl status project-tracker
    exit 1
fi

if sudo nginx -t > /dev/null 2>&1; then
    print_status "✅ Nginx configuration is valid!"
else
    print_error "❌ Nginx configuration is invalid"
    exit 1
fi

print_status "🎉 Deployment completed successfully!"
print_status "Your API is now available at: https://$DOMAIN"
print_status "API Documentation: https://$DOMAIN/docs"
print_status "Health Check: https://$DOMAIN/health"
print_status "Swagger UI: https://$DOMAIN/docs"

echo ""
print_warning "Don't forget to:"
echo "1. Update the domain name in nginx.conf"
echo "2. Update your DNS records to point to this server"
echo "3. Change the database password in .env file"
echo "4. Update the email address in the certbot command" 