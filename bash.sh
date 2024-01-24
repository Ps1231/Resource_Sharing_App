#!/bin/bash

# Your GitHub username
USERNAME="Ps1231"

# Get a list of your public repositories using the GitHub API
REPOS=$(curl -s "https://api.github.com/users/$USERNAME/repos" | jq -r '.[].full_name')

# Loop through each repository and print its name and contributors
for REPO in $REPOS; do
  echo "Repository: $REPO"
  
  # Get the contributors using the GitHub API
  CONTRIBUTORS=$(curl -s "https://api.github.com/repos/$REPO/contributors" | jq -r '.[].login')

  # Print the contributors
  echo "Contributors: $CONTRIBUTORS"
  
  # Add a separator for better readability
  echo "-------------------------"
done
