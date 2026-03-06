#!/bin/bash
# EC2 Setup Script for EnergyMind AI

echo "Updating system..."
sudo dnf update -y

echo "Installing Docker..."
sudo dnf install docker -y

echo "Starting Docker service..."
sudo systemctl start docker
sudo systemctl enable docker

echo "Adding current user to docker group..."
sudo usermod -a -G docker $USER

echo "Docker installation complete!"
echo "IMPORTANT: Please log out and log back in for group changes to take effect."
echo "Then you can run: docker ps to verify."
