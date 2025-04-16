#!/usr/bin/env python3
"""
GitHub Project Setup Script using GraphQL API (Version 3)

This script sets up a GitHub Project for the Performance Suite repository using the GraphQL API.
It demonstrates how to automate project management with the new GitHub Projects experience.

Usage:
    python scripts/setup_github_project_graphql_v3.py

Requirements:
    - Python 3.6+
    - requests package
    - python-dotenv package
    - GitHub CLI (gh) installed and authenticated
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path

try:
    import requests
    import dotenv
    import yaml
except ImportError:
    print("Required packages not found. Installing...")
    os.system("pip install requests python-dotenv pyyaml")
    import requests
    import dotenv
    import yaml

# GraphQL API endpoint
GITHUB_API_URL = "https://api.github.com/graphql"

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
        'token': os.getenv('GITHUB_TOKEN')
    }

def get_github_token(env_vars):
    """Get GitHub token from env or GitHub CLI"""
    if env_vars['token']:
        return env_vars['token']
    
    try:
        # Try to get token from GitHub CLI
        result = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True,
            text=True,
            check=True
        )
        token = result.stdout.strip()
        
        if token:
            # Save token to .env file
            with open('.env', 'a') as f:
                f.write(f"\nGITHUB_TOKEN={token}\n")
            return token
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    
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

def run_graphql_query(token, query, variables=None):
    """Run a GraphQL query against the GitHub API"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    
    data = {
        "query": query,
        "variables": variables or {}
    }
    
    response = requests.post(GITHUB_API_URL, headers=headers, json=data)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        sys.exit(1)
    
    result = response.json()
    
    # Check for errors in the response
    if 'errors' in result:
        print("GraphQL Error:")
        for error in result['errors']:
            print(f"  - {error['message']}")
        print("Full response:", json.dumps(result, indent=2))
        sys.exit(1)
    
    return result

def get_user_info(token, username):
    """Get user information using GraphQL"""
    query = """
    query($username: String!) {
      user(login: $username) {
        id
        login
        repositories(first: 100) {
          nodes {
            id
            name
            nameWithOwner
          }
        }
      }
    }
    """
    
    variables = {
        "username": username
    }
    
    result = run_graphql_query(token, query, variables)
    return result["data"]["user"]

def find_repository(user_info, repo_name_pattern):
    """Find repository by name pattern"""
    repos = user_info["repositories"]["nodes"]
    
    # First try exact match
    for repo in repos:
        if repo["name"].lower() == repo_name_pattern.lower():
            return repo
    
    # Then try contains match
    for repo in repos:
        if repo_name_pattern.lower() in repo["name"].lower():
            return repo
    
    return None

def create_project(token, user_id, title):
    """Create a new project using GraphQL"""
    query = """
    mutation($input: CreateProjectV2Input!) {
      createProjectV2(input: $input) {
        projectV2 {
          id
          number
          url
        }
      }
    }
    """
    
    variables = {
        "input": {
            "ownerId": user_id,
            "title": title
            # "description" field is no longer supported
        }
    }
    
    try:
        result = run_graphql_query(token, query, variables)
        return result["data"]["createProjectV2"]["projectV2"]
    except KeyError as e:
        print(f"KeyError: {e}")
        print("Failed to create project. This could be due to permission issues or rate limiting.")
        print("Try creating the project manually through the GitHub UI.")
        sys.exit(1)

def create_project_field(token, project_id, name, field_type, options=None):
    """Create a custom field in the project"""
    if field_type == "SINGLE_SELECT":
        query = """
        mutation($input: CreateProjectV2FieldInput!) {
          createProjectV2Field(input: $input) {
            projectV2Field {
              id
              name
            }
          }
        }
        """
        
        variables = {
            "input": {
                "projectId": project_id,
                "dataType": field_type,
                "name": name,
                "singleSelectOptions": options or []
            }
        }
    else:
        query = """
        mutation($input: CreateProjectV2FieldInput!) {
          createProjectV2Field(input: $input) {
            projectV2Field {
              id
              name
            }
          }
        }
        """
        
        variables = {
            "input": {
                "projectId": project_id,
                "dataType": field_type,
                "name": name
            }
        }
    
    try:
        result = run_graphql_query(token, query, variables)
        return result["data"]["createProjectV2Field"]["projectV2Field"]
    except KeyError as e:
        print(f"KeyError: {e}")
        print(f"Failed to create field '{name}'. This could be due to permission issues or rate limiting.")
        print("Try creating the field manually through the GitHub UI.")
        return {"id": "dummy_id", "name": name}

def create_project_view(token, project_id, name, view_type="BOARD"):
    """Create a project view"""
    query = """
    mutation($input: CreateProjectV2ViewInput!) {
      createProjectV2View(input: $input) {
        projectV2View {
          id
          name
          number
        }
      }
    }
    """
    
    variables = {
        "input": {
            "projectId": project_id,
            "name": name,
            "layout": view_type
        }
    }
    
    try:
        result = run_graphql_query(token, query, variables)
        return result["data"]["createProjectV2View"]["projectV2View"]
    except KeyError as e:
        print(f"KeyError: {e}")
        print(f"Failed to create view '{name}'. This could be due to permission issues or rate limiting.")
        print("Try creating the view manually through the GitHub UI.")
        return {"id": "dummy_id", "name": name, "number": 1}

def get_existing_projects(token, username):
    """Get existing projects for a user"""
    query = """
    query($username: String!) {
      user(login: $username) {
        projectsV2(first: 20) {
          nodes {
            id
            title
            url
            number
          }
        }
      }
    }
    """
    
    variables = {
        "username": username
    }
    
    try:
        result = run_graphql_query(token, query, variables)
        return result["data"]["user"]["projectsV2"]["nodes"]
    except KeyError as e:
        print(f"KeyError: {e}")
        print("Failed to get existing projects.")
        return []

def setup_github_project(token, username, config, dry_run=False):
    """Set up GitHub Project using GraphQL API"""
    if dry_run:
        print("\nDRY RUN - Configuration:")
        print(f"Project Name: {config.get('project', {}).get('name', 'Performance Suite Development')}")
        print(f"Views: {len(config.get('views', {}).get('views', []))}")
        print(f"Milestones: {len(config.get('milestones', {}).get('milestones', []))}")
        return
    
    # Get user info
    print(f"Getting information for user: {username}")
    user_info = get_user_info(token, username)
    user_id = user_info["id"]
    print(f"User ID: {user_id}")
    
    # Find repository
    repo = find_repository(user_info, "PerformanceSuite")
    if not repo:
        print("Repository not found. Please create it first.")
        sys.exit(1)
    
    print(f"Found repository: {repo['nameWithOwner']}")
    
    # Check for existing projects
    print("Checking for existing projects...")
    projects = get_existing_projects(token, username)
    project_name = config.get('project', {}).get('name', 'Performance Suite Development')
    
    existing_project = None
    for project in projects:
        if project["title"] == project_name:
            existing_project = project
            break
    
    if existing_project:
        print(f"Project already exists: {existing_project['url']}")
        project = existing_project
    else:
        # Create project
        print(f"Creating project: {project_name}")
        try:
            project = create_project(token, user_id, project_name)
            print(f"Project created: {project['url']}")
        except Exception as e:
            print(f"Error creating project: {e}")
            print("Please create the project manually through the GitHub UI.")
            sys.exit(1)
    
    # Update .env file with project URL
    with open('.env', 'a') as f:
        f.write(f"GITHUB_PROJECT_URL={project['url']}\n")
    
    # Create custom fields
    print("Creating custom fields...")
    
    # Priority field
    priority_options = [
        {"name": "🔥 High", "color": "RED"},
        {"name": "🔶 Medium", "color": "ORANGE"},
        {"name": "🔷 Low", "color": "GREEN"}
    ]
    priority_field = create_project_field(token, project['id'], "Priority", "SINGLE_SELECT", priority_options)
    print(f"Created Priority field: {priority_field['id']}")
    
    # Component field
    component_options = [
        {"name": "Audio Processing", "color": "BLUE"},
        {"name": "MIDI Generation", "color": "BLUE"},
        {"name": "AI Bandmates", "color": "BLUE"},
        {"name": "Visual Components", "color": "PURPLE"},
        {"name": "Control Interface", "color": "PURPLE"},
        {"name": "Infrastructure", "color": "YELLOW"},
        {"name": "Documentation", "color": "PINK"}
    ]
    component_field = create_project_field(token, project['id'], "Component", "SINGLE_SELECT", component_options)
    print(f"Created Component field: {component_field['id']}")
    
    # Effort field
    effort_options = [
        {"name": "Small", "color": "GREEN"},
        {"name": "Medium", "color": "YELLOW"},
        {"name": "Large", "color": "RED"}
    ]
    effort_field = create_project_field(token, project['id'], "Effort", "SINGLE_SELECT", effort_options)
    print(f"Created Effort field: {effort_field['id']}")
    
    # Create views
    print("Creating views...")
    
    # Board view (default)
    board_view = create_project_view(token, project['id'], "Board", "BOARD")
    print(f"Created Board view: {board_view['id']}")
    
    # Roadmap view
    roadmap_view = create_project_view(token, project['id'], "Roadmap", "ROADMAP")
    print(f"Created Roadmap view: {roadmap_view['id']}")
    
    # Component view
    component_view = create_project_view(token, project['id'], "Component View", "BOARD")
    print(f"Created Component view: {component_view['id']}")
    
    # Priority view
    priority_view = create_project_view(token, project['id'], "Priority View", "BOARD")
    print(f"Created Priority view: {priority_view['id']}")
    
    # Table view
    table_view = create_project_view(token, project['id'], "All Items", "TABLE")
    print(f"Created Table view: {table_view['id']}")
    
    print("\nSetup completed successfully!")
    print(f"Project URL: {project['url']}")
    print(f"Project ID: {project['id']}")
    print(f"Status Field ID: Look for the Status field ID in the project settings")
    print("\nNext steps:")
    print("1. Visit the project URL to configure the views")
    print("2. Set up automation workflows in the project settings")
    print("3. Update the project-automation-graphql.yml workflow with the project ID")
    
    # Update the workflow file with the project ID
    workflow_path = Path('.github/workflows/project-automation-graphql.yml')
    if workflow_path.exists():
        print("\nUpdating project-automation-graphql.yml with the project ID...")
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Replace the placeholder with the actual project ID
        content = content.replace('YOUR_PROJECT_ID', project['id'])
        
        with open(workflow_path, 'w') as f:
            f.write(content)
        
        print("Workflow file updated successfully!")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Set up GitHub Project for Performance Suite using GraphQL')
    parser.add_argument('--dry-run', action='store_true', help='Print configuration without making API calls')
    args = parser.parse_args()
    
    print("Performance Suite GitHub Project Setup (GraphQL v3)")
    print("===============================================")
    
    # Load environment variables
    env_vars = load_env()
    print(f"GitHub Username: {env_vars['username']}")
    print(f"GitHub Email: {env_vars['email']}")
    
    # Get GitHub token
    token = get_github_token(env_vars)
    
    # Load project configuration
    config = load_project_config()
    
    # Set up GitHub Project
    setup_github_project(token, env_vars['username'], config, args.dry_run)

if __name__ == "__main__":
    main()