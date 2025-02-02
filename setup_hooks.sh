#!/bin/bash

echo "Setting up Git hooks..."

# Copy hooks to .git/hooks
cp scripts/hooks/pre-commit .git/hooks/pre-commit
cp scripts/hooks/post-commit .git/hooks/post-commit
cp scripts/hooks/revert_translations.py .git/hooks/revert_translations.py
cp scripts/hooks/apply_translations.py .git/hooks/apply_translations.py

# Make the hooks executable
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/post-commit
chmod +x .git/hooks/revert_translations.py
chmod +x .git/hooks/apply_translations.py

echo "Git hooks setup complete!"
