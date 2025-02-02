import base64
import requests

# get all file names
def get_all_filenames_from_github(owner: str, repo: str, branch: str, token: str):
	url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
	r = requests.get(url,
									headers = {
										"Accept": "application/vnd.github+json",
										"Authorization": f"Bearer {token}"
									})
	if (r.status_code != 200):
		raise Exception("Get trees API failed")
	result = r.json()
	return [f["path"] for f in result["tree"]]

def get_file_contents(owner: str, repo: str, filepaths: list[str], token: str):
	paths2content: dict[str, str] = dict()
	for path in filepaths:
		r = requests.get(
				f"https://api.github.com/repos/{owner}/{repo}/contents/{path}",
				headers={
						"Authorization": f"Bearer {token}",
						"Accept": "application/vnd.github.v3+json"
				})
		content = base64.b64decode(r.json()["content"]).decode()
		paths2content[path] = content
	return paths2content

def parse_comments_from_content(content: str):
	pass
