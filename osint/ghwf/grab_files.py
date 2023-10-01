import requests
import argparse
import os


def call_api(api_key, keywords, extensions, sort, sort_direction, fullpath, max_files, start_offset=0):
    max_files = min(max_files, 1000)
    querystring = {
        "keywords": " ".join(keywords),
        "start": start_offset,
        "limit": max_files,
        }

    if sort is not None and sort != "none":
        querystring["order"] = sort
        querystring["direction"] = sort_direction
    
    if fullpath:
        querystring["full-path"] = 1

    if extensions is not None:
        querystring["extensions"] = extensions

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0",
        }

    print(f"Querying API with parameters, starting at offset {start_offset} and returning {max_files} results: {querystring}")

    return requests.request("GET", "https://buckets.grayhatwarfare.com/api/v2/files", headers=headers, params=querystring)

def download_file(file_obj, output_dir):
    file_name = file_obj["filename"]
    url = file_obj["url"]
    file_subdir = "/".join(file_obj["fullPath"].removeprefix("/").split("/")[:-1])
    bucket_name = file_obj["bucket"]
    local_path = os.path.join(output_dir, bucket_name, file_subdir)
    os.makedirs(local_path, exist_ok=True)
    local_file = os.path.join(local_path, file_name)
    if not os.path.exists(local_file):
        try:
            with open(local_file, "wb") as f:
                f.write(requests.get(url).content)
                print(f"Downloaded file {file_name} to {local_file} from {url}")
        except Exception as e:
            pass
    # print(f"Downloading file {file_name} to {local_path} from {url}")
    # requests.request("GET", url, stream=True)

def query(api_key, keywords, extensions, output_dir, sort, sort_direction, fullpath, max_files: int):
    start_offset = 0
    dl_max = min(max_files, 1000)
    while True:
        response = call_api(api_key, keywords, extensions, sort, sort_direction, fullpath, dl_max, start_offset)
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            break

        json = response.json()
        r_query = json["query"]
        r_meta = json["meta"]
        print(f"Query object: {r_query}")
        print(f"Meta object: {r_meta}")
        query_limit: int = r_query["limit"]
        downloaded_files: int = query_limit + r_query["start"]
        r_total: int = r_meta["results"]
        print(f"Total results: {r_total}, downloaded: {downloaded_files} of {max_files}")

        for file in json["files"]:
            download_file(file, output_dir)

        
        if downloaded_files >= max_files or downloaded_files  >= r_total:
            break
        else:
            start_offset += query_limit
            dl_max = min(max_files - downloaded_files, query_limit)
        


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--api-key", help="The API-key for GHWF", required=True)
    parser.add_argument("-m", "--max", help="The maximum number of results to return (will page if over 1000)", default=1000, type=int)
    parser.add_argument("-e", "--extensions", help="The file extensions to search for, comma separated")
    parser.add_argument("-o", "--output", help="The directory to output the results to", default="./results")
    parser.add_argument("-s", "--sort", help="The sort order", choices=["none", "last_modified", "size", "name"], default="none")
    parser.add_argument("-d", "--sort-direction", help="The sort direction", choices=["desc", "asc"], default="desc")
    parser.add_argument("-f", "--fullpath", help="Indicator if the query is searching in the full-path", action='store_true', default=False)
    parser.add_argument("-x", "--exclude", help="The keywords to exclude from the search, comma separated")
    parser.add_argument("keywords", nargs="*", help="The keywords to search for")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    keywords = args.keywords
    exclude = args.exclude.split(",") if args.exclude is not None else []
    exclude = [f"-{x}" for x in exclude if x != ""]
    keywords = keywords + exclude
    query(args.api_key, keywords, args.extensions, args.output, args.sort, args.sort_direction, args.fullpath, args.max)