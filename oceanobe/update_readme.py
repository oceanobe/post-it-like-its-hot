import os
import requests
from bs4 import BeautifulSoup
from github import Github

# Configuration
GITHUB_TOKEN = os.getenv("API_GITHUB_TOKEN")  # GitHub personal access token
ORG_REPO = "oceanobe/.github"  # GitHub organization/repository
README_PATH = "profile/readme.md"
BLOG_URL = "https://oceanobe.com/news"  # URL of the news page
MAX_POSTS = 5  # Number of recent posts to display


def fetch_latest_blog_posts():
    """Scrape the latest blog posts from the website."""
    response = requests.get(BLOG_URL)
    if response.status_code != 200:
        print(f"Failed to fetch blog page: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    posts = []

    # Find all blog articles
    for article in soup.find_all("div", class_="article")[:MAX_POSTS]:
        # Find the title and link
        title_tag = article.find("span", class_="news-title")
        link_tag = article.find("a", class_="post-link")
        date_tag = article.find("span", class_="news-date small-secondary")

        if title_tag and link_tag and date_tag:
            title = title_tag.get_text(strip=True)
            link = link_tag["href"]
            date = date_tag.get_text(strip=True)

            # Handle relative URLs (adding domain if needed)
            full_link = link if link.startswith("http") else f"https://oceanobe.com{link}"

            posts.append(f"- [{title}]({full_link}) ({date})")

    return posts


def update_readme():
    """Fetches and updates the .github/profile/readme.md file"""

    # Authenticate with GitHub
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(ORG_REPO)

    try:
        contents = repo.get_contents(README_PATH)
        readme_text = contents.decoded_content.decode("utf-8")
    except Exception as e:
        print(f"❌ Error fetching README: {e}")
        return

    # Fetch latest blog posts
    new_posts = fetch_latest_blog_posts()

    # Define Blog Posts section
    blog_section_header = "## Blog Posts\n"
    new_blog_section = blog_section_header + "\n".join(new_posts) + "\n"

    # Check if README already has a "## Blog Posts" section
    if blog_section_header in readme_text:
        # Replace existing Blog Posts section
        before, _ = readme_text.split(blog_section_header, 1)
        updated_readme = before + new_blog_section
    else:
        # Append the Blog Posts section at the end
        updated_readme = readme_text.strip() + "\n\n" + new_blog_section

    # Commit changes only if the README actually changed
    if updated_readme != readme_text:
        repo.update_file(
            path=README_PATH,
            message="Update README with latest blog posts",
            content=updated_readme,
            sha=contents.sha
        )
        print("✅ README updated successfully!")
        print(updated_readme)
    else:
        print("✅ No changes needed. README is up to date.")


if __name__ == "__main__":
    update_readme()
