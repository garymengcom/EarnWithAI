import requests
import os

GITHUB_API = "https://api.github.com/search/repositories"
HEADERS = {"Authorization": f"token {os.getenv('GITHUB_TOKEN')}"}
TOPICS = ["ai", "ai-agent", "llm"]  # Fetch separately for each topic
PER_PAGE = 50
PAGES = 10
MIN_STARS = 5000
OUTPUT_FILE = "README.md"  # Output file name changed to README.md
EXCLUDE_FILE = "excluded-repos.txt"  # File containing repos to exclude


def fetch_repositories(topic):
    repos = []
    for page in range(1, PAGES + 1):
        params = {
            "q": f"topic:{topic} stars:>={MIN_STARS}",
            "sort": "stars",  # Sort by stars
            "order": "desc",   # Descending order
            "per_page": PER_PAGE,
            "page": page
        }
        response = requests.get(GITHUB_API, headers=HEADERS, params=params)
        repos_curr = response.json().get("items", [])
        if len(repos_curr) == 0:
            break
        repos.extend(repos_curr)
        print(f"Repos added {len(repos_curr)} of {len(repos)} at topic [{topic}] page [{page}]")
    
    return repos


def format_stars(stars):
    """Format the number of stars to be in k or m units."""
    if stars >= 1_000_000:
        return f"{stars / 1_000_000:.1f}m"  # Format to 'm' for millions
    elif stars >= 1_000:
        return f"{stars / 1_000:.1f}k"  # Format to 'k' for thousands
    else:
        return str(stars)  # No formatting for less than 1000

def load_excluded():
    with open(EXCLUDE_FILE, "r") as file:
        return {line.strip() for line in file.readlines()}

def load_extra_repos():
    """Load additional repositories from extra-repos.txt."""
    extra_repos = []
    with open("extra-repos.txt", "r") as file:
        for line in file:
            owner_repo = line.strip()
            if owner_repo:
                owner, repo = owner_repo.split("/")
                extra_repos.append({"owner": owner, "name": repo})
    return extra_repos

def fetch_extra_repo_details(extra_repos):
    """Fetch details for repositories listed in extra-repos.txt."""
    detailed_repos = []
    for repo in extra_repos:
        url = f"https://api.github.com/repos/{repo['owner']}/{repo['name']}"
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            detailed_repos.append(response.json())
        else:
            print(f"Failed to fetch details for {repo['owner']}/{repo['name']}")
    return detailed_repos

def save_to_markdown(repositories, excluded_repos):
    seen = set()
    unique_repos = []

    # Remove duplicates (repos appearing in both topics)
    for repo in repositories:
        if repo["id"] not in seen and repo["name"] not in excluded_repos:
            seen.add(repo["id"])
            unique_repos.append(repo)

    # Sort repositories by stars in descending order
    unique_repos.sort(key=lambda x: x["stargazers_count"], reverse=True)

    with open(OUTPUT_FILE, "w") as file:
        file.write("# Earn With AI\n\n")
        file.write("**Earn Money** with Open Source AI Project.\n\n")
        file.write("| No. | Name | Stars | Description |\n")
        file.write("|-----|------|-------|-------------|\n")
        for index, repo in enumerate(unique_repos, start=1):
            stars = format_stars(repo['stargazers_count'])
            file.write(f"| {index} | [{repo['name']}]({repo['html_url']}) | ⭐ {stars} | {repo['description'] or 'No description'} |\n")


if __name__ == "__main__":
    all_repos = []
    excluded_repos = load_excluded()
    for topic in TOPICS:
        all_repos.extend(fetch_repositories(topic))
    
    # Add extra repositories
    extra_repos = load_extra_repos()
    all_repos.extend(fetch_extra_repo_details(extra_repos))
    print("Loaded extra repositories")
    
    save_to_markdown(all_repos, excluded_repos)
