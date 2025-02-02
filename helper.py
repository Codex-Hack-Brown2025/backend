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




# parse all py files, replace comments with landmarks
# share comments to mongodb
# add hooks or setup for hooks
# commit to main branch
	
	{
  "sha": "d66b519aaf5329d1dac8452a2a6882fbed08b567",
  "url": "https://api.github.com/repos/deeja/bing-maps-loader/git/trees/d66b519aaf5329d1dac8452a2a6882fbed08b567",
  "tree": [
    {
      "path": ".gitignore",
      "mode": "100644",
      "type": "blob",
      "sha": "bd07d4e1bc26979c14a11a72824f88d59b8f0498",
      "size": 19,
      "url": "https://api.github.com/repos/deeja/bing-maps-loader/git/blobs/bd07d4e1bc26979c14a11a72824f88d59b8f0498"
    },
    {
      "path": ".npmignore",
      "mode": "100644",
      "type": "blob",
      "sha": "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391",
      "size": 0,
      "url": "https://api.github.com/repos/deeja/bing-maps-loader/git/blobs/e69de29bb2d1d6434b8b29ae775ad8c2e48c5391"
    },
    {
      "path": "README.md",
      "mode": "100644",
      "type": "blob",
      "sha": "4db4bf948b31018af23745e9487453ecd873b390",
      "size": 6481,
      "url": "https://api.github.com/repos/deeja/bing-maps-loader/git/blobs/4db4bf948b31018af23745e9487453ecd873b390"
    },
    {
      "path": "index.ts",
      "mode": "100644",
      "type": "blob",
      "sha": "8b0dca649f6a562b22687694e7113f73b2e5eece",
      "size": 3648,
      "url": "https://api.github.com/repos/deeja/bing-maps-loader/git/blobs/8b0dca649f6a562b22687694e7113f73b2e5eece"
    },
    {
      "path": "package.json",
      "mode": "100644",
      "type": "blob",
      "sha": "3ed4cd18d25dcf32f7aa6bbb907068a790341f84",
      "size": 702,
      "url": "https://api.github.com/repos/deeja/bing-maps-loader/git/blobs/3ed4cd18d25dcf32f7aa6bbb907068a790341f84"
    },
    {
      "path": "tsconfig.json",
      "mode": "100644",
      "type": "blob",
      "sha": "1ab481a6063b28bcad5beba2c701d8b9ad8bfd89",
      "size": 295,
      "url": "https://api.github.com/repos/deeja/bing-maps-loader/git/blobs/1ab481a6063b28bcad5beba2c701d8b9ad8bfd89"
    },
    {
      "path": "yarn.lock",
      "mode": "100644",
      "type": "blob",
      "sha": "8f35ab09cfcdb84606d61e5a4c3429397869ed96",
      "size": 543,
      "url": "https://api.github.com/repos/deeja/bing-maps-loader/git/blobs/8f35ab09cfcdb84606d61e5a4c3429397869ed96"
    }
  ],
  "truncated": false
}