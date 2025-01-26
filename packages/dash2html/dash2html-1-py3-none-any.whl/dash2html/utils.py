from requests import get as  get_request
from html.parser import HTMLParser
from zipfile import ZipFile
from io import BytesIO
class ExternalResourceParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.resources:set[str] = set()
    def handle_starttag(self, tag, attrs):
        if tag == 'link':
            for k, v in attrs:
                if k == 'href':
                    self.resources.add(v)
        if tag == 'script':
            for k, v in attrs:
                if k == 'src':
                    self.resources.add(v)

def patch_file(index_html_content: str, extra: dict[str,bytes] = None):
    return index_html_content.replace(
        '<footer>',
f'''
<footer>
<script>
var patched_jsons_content={{{','.join(["'/" + k + "':" + v.decode() + "" for k, v in extra.items()])}}};
'''+'''
const origFetch = window.fetch;
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
</script>
''').replace('href="/','href="').replace('src="/','src="')

def make_static(base_url:str,json_paths:set[str] ,extra_res:set[str]):
    res = get_request(base_url)
    res.encoding = 'utf-8'
    patched = patch_file(res.text, {json_path:get_request(base_url + json_path).content for json_path in json_paths})
    filedata:dict[str,bytes] = {}
    filedata['index.html'] = patched.encode()
    parser = ExternalResourceParser()
    parser.feed(patched)
    for resource_path in parser.resources.union(extra_res):
        filedata[resource_path.lstrip('/').split('?')[0]] = get_request(base_url + resource_path).content
    del filedata['']
    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, 'w') as zip_file:
        for filename, content in filedata.items():
            zip_file.writestr(filename, content)
    zip_buffer.seek(0)
    return zip_buffer

def process_log(log:str):
    json_paths = set()
    paths = set()
    for line in log.splitlines():
        if '"GET ' in line:
            routepath = line.split('"GET ')[1].split(' ')[0]
            if routepath.startswith("/_") and not routepath.startswith("/_favicon.ico") and not routepath.endswith(".js"):
                json_paths.add(routepath.split("/")[1])
            else:
                paths.add(routepath)
    return json_paths, paths
