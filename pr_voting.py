










import os
import sys
from github import Github, GithubException
from collections import defaultdict

# ====================== CONFIGURATION ======================
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
REPO_OWNER = os.getenv('REPO_OWNER', 'yourusername')   # e.g. "octocat"
REPO_NAME = os.getenv('REPO_NAME', 'your-repo')        # e.g. "awesome-project"
PR_NUMBER = int(os.getenv('PR_NUMBER'))                # Passed from Actions or CLI

# Voting options and their corresponding reactions
VOTE_OPTIONS = {
    "Approve": "👍",
    "Request Changes": "👎",
    "Abstain": "👀"
}

# Minimum approvals needed to consider "Passed" (customize as needed)
MIN_APPROVALS = 2

# ==========================================================

def get_repo():
    if not GITHUB_TOKEN:
        raise ValueError("GITHUB_TOKEN environment variable is required")
    g = Github(GITHUB_TOKEN)
    return g.get_repo(f"{REPO_OWNER}/{REPO_NAME}")

def create_or_find_poll_comment(repo, pr):
    """Create voting poll if not exists, or find existing one"""
    poll_body = "## 🗳️ Community Voting on this PR\n\n"
    poll_body += "Please vote by reacting to **this comment** with one of the emojis below:\n\n"
    
    for option, emoji in VOTE_OPTIONS.items():
        poll_body += f"{emoji} **{option}**\n"
    
    poll_body += "\n**Rules:** One reaction per user. Only reactions on this comment count.\n"
    poll_body += f"Vote closes when {MIN_APPROVALS} approvals are reached or manually.\n"

    # Check if poll comment already exists
    for comment in pr.get_issue_comments():
        if "## 🗳️ Community Voting on this PR" in comment.body:
            print(f"Existing poll found (Comment ID: {comment.id})")
            return comment

    # Create new poll
    comment = pr.create_issue_comment(poll_body)
    print(f"✅ New voting poll created! Comment ID: {comment.id}")
    return comment

def tally_votes(poll_comment):
    """Count reactions on the poll comment"""
    votes = defaultdict(int)
    voters = defaultdict(str)  # user -> their vote

    try:
        for reaction in poll_comment.get_reactions():
            user = reaction.user.login
            content = reaction.content

            # Map reaction to vote option
            for option, emoji in VOTE_OPTIONS.items():
                if emoji == content or (content == "+1" and emoji == "👍"):
                    if user not in voters:  # Only count first vote
                        votes[option] += 1
                        voters[user] = option
                    break
    except GithubException as e:
        print(f"Warning: Could not fetch reactions: {e}")

    return votes, voters

def post_results(repo, pr, poll_comment, votes):
    """Update or post results summary"""
    total_votes = sum(votes.values())
    approve_count = votes.get("Approve", 0)
    status = "✅ **PASSED**" if approve_count >= MIN_APPROVALS else "⏳ **In Progress**"

    results = f"\n\n---\n## 📊 Current Voting Results\n\n"
    results += f"**Status:** {status} (Need {MIN_APPROVALS} approvals)\n\n"
    results += "| Option | Votes | Percentage |\n"
    results += "|--------|-------|------------|\n"

    for option in VOTE_OPTIONS:
        count = votes.get(option, 0)
        percent = round((count / total_votes * 100), 1) if total_votes > 0 else 0
        results += f"| {option} | {count} | {percent}% |\n"

    results += f"\n**Total votes:** {total_votes}\n"

    # Update the poll comment with results
    try:
        # Append results if not already there, or replace
        if "## 📊 Current Voting Results" in poll_comment.body:
            new_body = poll_comment.body.split("## 📊 Current Voting Results")[0] + results
        else:
            new_body = poll_comment.body + results
        
        poll_comment.edit(new_body)
        print("✅ Results updated in poll comment")
    except Exception as e:
        print(f"Failed to update comment: {e}")

def main():
    try:
        repo = get_repo()
        pr = repo.get_pull(PR_NUMBER)
        
        print(f"Processing PR #{PR_NUMBER}: {pr.title}")
        
        poll_comment = create_or_find_poll_comment(repo, pr)
        votes, voters = tally_votes(poll_comment)
        
        post_results(repo, pr, poll_comment, votes)
        
        # Optional: Print summary to console / logs
        print("\nFinal Tally:")
        for opt, cnt in votes.items():
            print(f"  {opt}: {cnt}")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
