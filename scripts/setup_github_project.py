#!/usr/bin/env python3
"""
GitHub Project Setup Script for Performance Suite

This script helps set up the GitHub Project and required secrets for the Performance Suite repository.
It reads configuration from the .env file and .github/projects directory.

Usage:
    python scripts/setup_github_project.py

Requirements:
    - Python 3.6+
    - PyGithub package
    - dotenv package
"""

import os
import sys
import yaml
import argparse
from pathlib import Path
from datetime import datetime

try:
    import dotenv
    from github import Github
    from github.GithubException import GithubException
except ImportError:
    print("Required packages not found. Installing...")
    os.system("pip install PyGithub python-dotenv pyyaml")
    import dotenv
    from github import Github
    from github.GithubException import GithubException

def load_env():
    """Load environment variables from .env file"""
    dotenv.load_dotenv()
    
    # Check for required environment variables
    required_vars = ['GITHUB_USERNAME', 'GITHUB_EMAIL']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please update your .env file with these variables.")
        sys.exit(1)
    
    return {
        'username': os.getenv('GITHUB_USERNAME'),
        'email': os.getenv('GITHUB_EMAIL'),
        'token': os.getenv('GITHUB_TOKEN'),
        'project_url': os.getenv('GITHUB_PROJECT_URL')
    }

def get_github_token(env_vars):
    """Get or prompt for GitHub token"""
    if env_vars['token']:
        return env_vars['token']
    
    print("\nA GitHub Personal Access Token is required to set up the project.")
    print("You can create one at: https://github.com/settings/tokens")
    print("Required scopes: repo, admin:org, project")
    token = input("\nEnter your GitHub Personal Access Token: ").strip()
    
    # Save token to .env file
    with open('.env', 'a') as f:
        f.write(f"\nGITHUB_TOKEN={token}\n")
    
    return token

def load_project_config():
    """Load project configuration from YAML files"""
    config_path = Path('.github/projects/project-config.yml')
    views_path = Path('.github/projects/project-views.yml')
    milestones_path = Path('.github/projects/milestones.yml')
    
    config = {}
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            config['project'] = yaml.safe_load(f)
    else:
        print(f"Warning: {config_path} not found")
    
    if views_path.exists():
        with open(views_path, 'r') as f:
            config['views'] = yaml.safe_load(f)
    else:
        print(f"Warning: {views_path} not found")
    
    if milestones_path.exists():
        with open(milestones_path, 'r') as f:
            config['milestones'] = yaml.safe_load(f)
    else:
        print(f"Warning: {milestones_path} not found")
    
    return config

def setup_github_project(token, username, config):
    """Set up GitHub Project using the API"""
    g = Github(token)
    user = g.get_user(username)
    
    try:
        # Check if user exists
        print(f"Authenticated as: {user.login}")
        
        # Get repositories
        repos = list(user.get_repos())
        print(f"\nFound {len(repos)} repositories")
        
        # Find Performance Suite repository
        perf_suite_repos = [repo for repo in repos if repo.name.lower() == 'performancesuite']
        
        if not perf_suite_repos:
            print("\nPerformance Suite repository not found.")
            create_repo = input("Would you like to create it? (y/n): ").lower() == 'y'
            
            if create_repo:
                repo = user.create_repo(
                    name="PerformanceSuite",
                    description="A comprehensive system for live musical performances with AI bandmates",
                    homepage="",
                    private=False,
                    has_issues=True,
                    has_projects=True,
                    has_wiki=True
                )
                print(f"Repository created: {repo.html_url}")
            else:
                print("Please create the repository manually and run this script again.")
                return
        else:
            repo = perf_suite_repos[0]
            print(f"Found repository: {repo.html_url}")
        
        # Check if project exists
        projects = list(repo.get_projects())
        project_name = config.get('project', {}).get('name', 'Performance Suite Development')
        matching_projects = [p for p in projects if p.name == project_name]
        
        if matching_projects:
            project = matching_projects[0]
            print(f"Project already exists: {project.html_url}")
        else:
            # Create project
            project = repo.create_project(
                name=project_name,
                body=config.get('project', {}).get('description', 'Project board for tracking development')
            )
            print(f"Project created: {project.html_url}")
            
            # Update .env file with project URL
            with open('.env', 'a') as f:
                f.write(f"GITHUB_PROJECT_URL={project.html_url}\n")
        
        print("\nSetup completed successfully!")
        print("\nNext steps:")
        print("1. Push your code to the repository")
        print("2. Set up the PROJECT_TOKEN secret in your repository settings")
        print("3. Configure the project columns and fields according to the configuration files")
        
    except GithubException as e:
        print(f"GitHub API Error: {e}")
        sys.exit(1)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Set up GitHub Project for Performance Suite')
    parser.add_argument('--dry-run', action='store_true', help='Print configuration without making API calls')
    args = parser.parse_args()
    
    print("Performance Suite GitHub Project Setup")
    print("=====================================")
    
    # Load environment variables
    env_vars = load_env()
    print(f"GitHub Username: {env_vars['username']}")
    print(f"GitHub Email: {env_vars['email']}")
    
    # Get GitHub token
    token = get_github_token(env_vars)
    
    # Load project configuration
    config = load_project_config()
    
    if args.dry_run:
        print("\nDRY RUN - Configuration:")
        print(f"Project Name: {config.get('project', {}).get('name', 'Performance Suite Development')}")
        print(f"Views: {len(config.get('views', {}).get('views', []))}")
        print(f"Milestones: {len(config.get('milestones', {}).get('milestones', []))}")
    else:
        # Set up GitHub Project
        setup_github_project(token, env_vars['username'], config)

if __name__ == "__main__":
    main()