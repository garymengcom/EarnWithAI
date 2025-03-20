import requests
import os

GITHUB_API = "https://api.github.com/search/repositories"
HEADERS = {"Authorization": f"token {os.getenv('GITHUB_TOKEN')}"}
QUERY = "topic:ai topic:ai-agent"
PER_PAGE = 100
PAGES = 10
OUTPUT_FILE = "README.md"

def fetch_repositories():
    repos = []
    for page in range(1, PAGES + 1):
        params = {"q": QUERY, "per_page": PER_PAGE, "page": page}
        response = requests.get(GITHUB_API, headers=HEADERS, params=params)
        if response.status_code == 200:
            repos.extend(response.json().get("items", []))
        else:
            print(f"Error fetching page {page}: {response.text}")
            break
    return repos


def save_to_markdown(repositories):
    with open(OUTPUT_FILE, "w") as file:
        file.write("# AI Open-Source Projects for Earning Money\n\n")
        file.write("| Name | Stars | Description |\n")
        file.write("|------|-------|------------|\n")
        for repo in repositories:
            file.write(f"| [{repo['name']}]({repo['html_url']}) | ⭐ {repo['stargazers_count']} | {repo['description'] or 'No description'} |\n")


if __name__ == "__main__":
    repos = fetch_repositories()
    save_to_markdown(repos)
