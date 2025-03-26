from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# GitHub Actions token (use a secret environment variable)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = "The-Bulls/.github"  # Replace with your repository where the workflow lives

@app.route("/webhook", methods=["POST"])
def github_webhook():
    data = request.json
    if data.get("action") == "created":
        repo_name = data.get("repository", {}).get("full_name")

        if not repo_name:
            return jsonify({"error": "Repository name not found"}), 400
        
        print(f"New repository detected: {repo_name}")

        # Trigger GitHub Actions workflow
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.everest-preview+json"
        }
        payload = {
            "event_type": "new_repo_created",
            "client_payload": {"repo_full_name": repo_name}
        }

        response = requests.post(
            f"https://api.github.com/repos/{GITHUB_REPO}/dispatches",
            json=payload,
            headers=headers
        )

        if response.status_code == 204:
            return jsonify({"message": f"Workflow triggered for {repo_name}"}), 200
        else:
            return jsonify({"error": "Failed to trigger workflow", "details": response.text}), 500

    return jsonify({"message": "Not a repository creation event"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
