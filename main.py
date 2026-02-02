import json
import os
from typing import List

import yaml

from lib import Project


def parse_markdown(file_path):
    '''
    Parse a markdown file and return the metadata and content.
    '''
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Separate metadata and markdown content
    if content.startswith('---'):
        end_metadata = content.find('---', 3)
        metadata_raw = content[3:end_metadata].strip()
        markdown_content = content[end_metadata+3:].strip()

        # Parse metadata as YAML
        metadata = yaml.safe_load(metadata_raw)
    else:
        metadata = {}
        markdown_content = content

    return metadata, markdown_content


def discover_projects(directory):
    '''
    Discover all projects in the given directory and return them as a list.
    '''
    projects = []

    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist")
        return projects

    for file in os.listdir(directory):
        if file.endswith('.md'):
            path = os.path.join(directory, file)
            try:
                frontmatter, content = parse_markdown(path)
                if frontmatter:  # Only process files with frontmatter
                    frontmatter["path"] = path
                    project = Project(frontmatter, content)
                    projects.append(project)
            except Exception as e:
                print(f"Error processing {path}: {e}")

    return projects


def generate_and_save_index(projects: List[Project]):
    '''
    Generate an index.json file with the given projects and save it.
    '''
    projects.sort(key=lambda x: x.date, reverse=True)
    with open("index.json", "w", encoding="utf-8") as f:
        json.dump([project.index_data()
                  for project in projects], f, ensure_ascii=False, indent=2)
        print("index.json has been updated")


def generate_and_save_readme(projects: List[Project]):
    '''
    Generate a README.md file with the given projects and save it.
    '''
    readme_title = "# Projects"
    readme_description = 'A collection of project writeups and case studies. These are used as a source for my personal website [abhin.dev](https://www.abhin.dev).'

    readme_content = f'{readme_title}\n\n{readme_description}\n\n'

    if not projects:
        readme_content += "No projects yet.\n"
    else:
        projects.sort(key=lambda x: x.date, reverse=True)
        for project in projects:
            if project.published:
                line = f'- **{project.title}** '
                line += f'[[Markdown]]({project.path})'
                line += f'[[Website]]({project.canonical_url})'
                line += f' - {project.date.strftime("%B %Y")}\n'
                if project.description:
                    line += f'  > {project.description}\n'
                line += '\n'
                readme_content += line

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
        print("README.md has been updated")


def main():
    '''
    Main function to discover projects and update the index and README.
    '''
    projects = discover_projects("projects")

    print(f"Found {len(projects)} projects")

    generate_and_save_index(projects)
    generate_and_save_readme(projects)


if __name__ == "__main__":
    main()
