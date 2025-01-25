from requests import get as  get_request
from html.parser import HTMLParser
from pathlib import Path
class ExternalResourceParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.resources:list[str] = []
    def handle_starttag(self, tag, attrs):
        if tag == 'link':
            for k, v in attrs:
                if k == 'href':
                    self.resources.append(v)
        if tag == 'script':
            for k, v in attrs:
                if k == 'src':
                    self.resources.append(v)

def patch_file(index_html_content: str, extra: dict[str,bytes] = None):
    return index_html_content.replace(
        '<footer>',
        f'''<footer><script>
        var patched_jsons_content={{{','.join(["'/" + k + "':" + v.decode() + "" for k, v in extra.items()])}}};
        '''+
        '''const origFetch = window.fetch;
        window.fetch = function () {
            const e = arguments[0]
            if (patched_jsons_content.hasOwnProperty(e)) {
                return Promise.resolve({
                    json: () => Promise.resolve(patched_jsons_content[e]),
                    headers: new Headers({'content-type': 'application/json'}),
                    status: 200,
                });
            } else {
                return origFetch.apply(this, arguments)
            }
        }
        </script>''').replace('href="/','href="').replace('src="/','src="')


def write_file(resurl: str, content: bytes, target_dir:Path):
    file_path = target_dir/ resurl.lstrip('/').split('?')[0]
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(content)



def make_static(base_url:str,json_paths:list[str] ,extra_js:list[str],target_dir:Path):
    parser = ExternalResourceParser()
    res = get_request(base_url)
    res.encoding = 'utf-8'
    patched = patch_file(res.text, {json_path:get_request(base_url + json_path).content for json_path in json_paths})
    parser.feed(patched)
    write_file('index.html', patched.encode(), target_dir)
    for resource_url in parser.resources + extra_js:
        write_file(resource_url, get_request(base_url + resource_url).content, target_dir)


def process_log(log_lines:list[str]):
    json_paths = set()
    js_script = set()
    for line in log_lines:
        if '"GET ' in line:
            path = line.split('"GET ')[1].split(' ')[0]
            if path.startswith("/_") and not path.startswith("/_favicon.ico"):
                if path.endswith(".js"):
                    js_script.add(path)
                else:
                    json_paths.add(path.split("/")[1])
    return json_paths, js_script
