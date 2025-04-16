# Manual GitHub Project Setup Guide

This guide explains how to manually set up GitHub Projects for the Performance Suite repository.

## Background

GitHub has deprecated the classic Projects API in favor of the new Projects experience. Our script successfully found your repository at https://github.com/SplinteredSunlight/PerformanceSuite, but we need to set up the project manually through the GitHub UI.

## Setup Steps

### 1. Create a New Project

1. Go to your repository at https://github.com/SplinteredSunlight/PerformanceSuite
2. Click on the "Projects" tab
3. Click "New project"
4. Select "Board" as the template
5. Name the project "Performance Suite Development"
6. Click "Create"

### 2. Configure Project Fields

1. In your new project, click on the "..." menu in the top-right corner
2. Select "Settings"
3. Go to the "Fields" section
4. Add the following custom fields:

#### Priority Field
1. Click "New field"
2. Select "Single select" as the field type
3. Name the field "Priority"
4. Add the following options:
   - 🔥 High (Color: Red)
   - 🔶 Medium (Color: Orange)
   - 🔷 Low (Color: Green)
5. Click "Save"

#### Component Field
1. Click "New field"
2. Select "Single select" as the field type
3. Name the field "Component"
4. Add the following options:
   - Audio Processing (Color: Blue)
   - MIDI Generation (Color: Light Blue)
   - AI Bandmates (Color: Cyan)
   - Visual Components (Color: Purple)
   - Control Interface (Color: Light Purple)
   - Infrastructure (Color: Yellow)
   - Documentation (Color: Pink)
5. Click "Save"

#### Effort Field
1. Click "New field"
2. Select "Single select" as the field type
3. Name the field "Effort"
4. Add the following options:
   - Small (Color: Green)
   - Medium (Color: Yellow)
   - Large (Color: Red)
5. Click "Save"

### 3. Configure Project Views

1. In your project, click on the "Views" section in the sidebar
2. Create the following views:

#### Board View (Default)
- This is created by default
- Ensure it's grouped by Status

#### Roadmap View
1. Click "New view"
2. Select "Roadmap" as the view type
3. Name the view "Roadmap"
4. Configure it to group by Milestone
5. Click "Save"

#### Component View
1. Click "New view"
2. Select "Board" as the view type
3. Name the view "Component View"
4. Configure it to group by Component
5. Click "Save"

#### Priority View
1. Click "New view"
2. Select "Board" as the view type
3. Name the view "Priority View"
4. Configure it to group by Priority
5. Click "Save"

#### All Items View
1. Click "New view"
2. Select "Table" as the view type
3. Name the view "All Items"
4. Ensure all fields are visible
5. Click "Save"

### 4. Create Milestones

For each milestone in the `.github/projects/milestones.yml` file, create a corresponding milestone in GitHub:

1. Go to your repository at https://github.com/SplinteredSunlight/PerformanceSuite
2. Click on the "Issues" tab
3. Click on "Milestones"
4. Click "New milestone"
5. Enter the milestone title, description, and due date
6. Click "Create milestone"
7. Repeat for each milestone

### 5. Set Up Automation

GitHub Projects has built-in automation capabilities:

1. In your project, click on the "..." menu in the top-right corner
2. Select "Workflows"
3. Enable the following built-in workflows:
   - Item added to project
   - Item closed
   - Pull request merged

### 6. Update Project URL in Configuration

After creating the project, update the `.env` file with the project URL:

```
GITHUB_PROJECT_URL=https://github.com/users/SplinteredSunlight/projects/X
```

Replace `X` with the actual project number.

## Automation with GraphQL and GitHub CLI

While the classic Projects API is deprecated, you can still automate GitHub Projects using GraphQL and the GitHub CLI.

### Using the GraphQL Setup Script

We've provided a script that uses GraphQL to set up a GitHub Project:

```bash
python scripts/setup_github_project_graphql.py
```

This script:
1. Authenticates with GitHub using your token or the GitHub CLI
2. Creates a new project
3. Adds custom fields (Priority, Component, Effort)
4. Creates project views (Board, Roadmap, Component, Priority, All Items)

### Using the GraphQL Workflow

We've also provided a GitHub Actions workflow that automates project management:

`.github/workflows/project-automation-graphql.yml`

This workflow:
1. Adds new issues and PRs to the project
2. Updates the status field based on the item type and action
3. Uses GraphQL to interact with the GitHub Projects API

Before using this workflow, you need to:
1. Replace `YOUR_PROJECT_ID` with your actual project ID
2. Replace `YOUR_STATUS_FIELD_ID` with your actual status field ID
3. Ensure the status values match your project's status options

### Finding Project and Field IDs

To find your project and field IDs:

1. Install the GitHub CLI: https://cli.github.com/
2. Run the following command to get your project ID:

```bash
gh api graphql -f query='
  query {
    viewer {
      projectsV2(first: 10) {
        nodes {
          id
          title
          url
        }
      }
    }
  }
'
```

3. Once you have your project ID, run this command to get field IDs:

```bash
gh api graphql -f query='
  query($projectId: ID!) {
    node(id: $projectId) {
      ... on ProjectV2 {
        fields(first: 20) {
          nodes {
            ... on ProjectV2Field {
              id
              name
            }
            ... on ProjectV2SingleSelectField {
              id
              name
              options {
                id
                name
              }
            }
          }
        }
      }
    }
  }
' -F projectId=YOUR_PROJECT_ID
```

Replace `YOUR_PROJECT_ID` with the actual project ID.

## Using the Project

### Adding Issues to the Project

When creating a new issue:

1. Fill out the issue template
2. On the right sidebar, click "Projects"
3. Select "Performance Suite Development"
4. Set the appropriate Priority, Component, and Effort values

### Adding Pull Requests to the Project

When creating a new pull request:

1. Fill out the pull request template
2. On the right sidebar, click "Projects"
3. Select "Performance Suite Development"
4. Set the appropriate values for the custom fields

## Troubleshooting

### Issues Not Appearing in Project

If issues or pull requests aren't appearing in your project:

1. Go to the issue or pull request
2. On the right sidebar, click "Projects"
3. Manually add it to the "Performance Suite Development" project

### Custom Fields Not Working

If custom fields aren't working as expected:

1. Go to the project settings
2. Check that the fields are configured correctly
3. Try removing and re-adding the field if necessary

### GraphQL Automation Not Working

If the GraphQL automation isn't working:

1. Check that you have the correct project and field IDs
2. Ensure your GitHub token has the necessary permissions
3. Check the Actions tab in your repository for error logs