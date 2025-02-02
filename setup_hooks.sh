#!/bin/bash

echo "Setting up Git hooks..."

# Copy hooks to .git/hooks
cp scripts/hooks/* .git/hooks/

# Make the hooks executable
chmod +x .git/hooks/*

echo "Git hooks setup complete!"
