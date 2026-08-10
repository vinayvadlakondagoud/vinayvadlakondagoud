import json
import os
import subprocess

OWNER = "vinayvadlakondagoud"


def gh(*args):
    env = dict(os.environ)
    return json.loads(subprocess.check_output(["gh", "api", *args], env=env))


def latest_commits(limit=5):
    repos = gh("users/{}/repos?per_page=100".format(OWNER))
    entries = []
    for repo in repos:
        if repo["fork"] or repo["private"]:
            continue
        try:
            commits = gh("repos/{}/{}/commits?per_page=1".format(OWNER, repo["name"]))
        except subprocess.CalledProcessError:
            continue
        if not commits:
            continue
        c = commits[0]
        entries.append(
            {
                "repo": repo["name"],
                "message": c["commit"]["message"].splitlines()[0][:80],
                "date": c["commit"]["committer"]["date"],
                "url": c["html_url"],
            }
        )
    entries.sort(key=lambda e: e["date"], reverse=True)
    return entries[:limit]


def main():
    entries = latest_commits()
    block = "\n".join(
        "- **{}** — {} ([commit]({}))".format(e["repo"], e["message"], e["url"])
        for e in entries
    )

    start_marker = "<!-- LATEST_COMMITS:START -->"
    end_marker = "<!-- LATEST_COMMITS:END -->"

    with open("README.md", encoding="utf-8") as f:
        content = f.read()

    start = content.index(start_marker)
    end = content.index(end_marker) + len(end_marker)
    content = content[:start] + start_marker + "\n" + block + "\n" + end_marker + content[end:]

    with open("README.md", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("Updated {} entries".format(len(entries)))


if __name__ == "__main__":
    main()
