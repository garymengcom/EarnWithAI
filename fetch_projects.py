import requests
import os

GITHUB_API = "https://api.github.com/search/repositories"
HEADERS = {"Authorization": f"token {os.getenv('GITHUB_TOKEN')}"}
TOPICS = ["ai", "ai-agent"]  # Fetch separately for each topic
PER_PAGE = 50
PAGES = 10
MIN_STARS = 5000
OUTPUT_FILE = "README.md"  # Output file name changed to README.md

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

def save_to_markdown(repositories):
    seen = set()
    unique_repos = []

    # Remove duplicates (repos appearing in both topics)
    for repo in repositories:
        if repo["id"] not in seen:
            seen.add(repo["id"])
            unique_repos.append(repo)

    # Sort repositories by stars in descending order
    unique_repos.sort(key=lambda x: x["stargazers_count"], reverse=True)

    with open(OUTPUT_FILE, "w") as file:
        file.write("# Earn With AI\n\n")
        file.write("**Earn Money** with Open Source AI Project.\n\n")
        file.write("| Name | Stars | Description |\n")
        file.write("|------|-------|------------|\n")
        for repo in unique_repos:
            file.write(f"| [{repo['name']}]({repo['html_url']}) | ⭐ {repo['stargazers_count']} | {repo['description'] or 'No description'} |\n")


if __name__ == "__main__":
    all_repos = []
    for topic in TOPICS:
        all_repos.extend(fetch_repositories(topic))
    
    save_to_markdown(all_repos)
