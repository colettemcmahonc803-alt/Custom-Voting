
import os
from github import Github

# === CONFIGURATION ===
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')  # Set as secret in GitHub Actions or env
REPO_OWNER = "yourusername"               # e.g. "octocat"
REPO_NAME = "your-repo-name"              # e.g. "hello-world"
ISSUE_NUMBER = 42                         # The issue where voting happens

# Options for the poll
POLL_OPTIONS = ["Option A", "Option B", "Option C"]

def create_poll():
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(f"{REPO_OWNER}/{REPO_NAME}")
    issue = repo.get_issue(ISSUE_NUMBER)

    poll_text = "## Community Vote\n\n"
    poll_text += "React with the corresponding emoji to vote:\n\n"
    emojis = ["👍", "❤️", "🚀"]  # One per option

    for i, option in enumerate(POLL_OPTIONS):
        poll_text += f"{emojis[i]} **{option}**\n"

    poll_text += "\nVote by reacting to this comment!"

    comment = issue.create_comment(poll_text)
    print(f"Poll created! Comment ID: {comment.id}")
    return comment

def tally_votes():
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(f"{REPO_OWNER}/{REPO_NAME}")
    issue = repo.get_issue(ISSUE_NUMBER)

    votes = {option: 0 for option in POLL_OPTIONS}
    emojis = ["👍", "❤️", "🚀"]

    # Get reactions on the issue itself (or specific comment)
    for reaction in issue.get_reactions():
        if reaction.content == "+1":
            votes[POLL_OPTIONS[0]] += 1
        # Add more mapping as needed

    print("Vote Results:")
    for option, count in votes.items():
        print(f"{option}: {count} votes")

    return votes

if __name__ == "__main__":
    # Uncomment one:
    # create_poll()
    tally_votes()
