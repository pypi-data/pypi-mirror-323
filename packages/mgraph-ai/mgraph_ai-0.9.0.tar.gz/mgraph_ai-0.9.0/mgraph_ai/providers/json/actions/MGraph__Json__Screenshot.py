import requests
from mgraph_ai.providers.json.actions.MGraph__Json__Export          import MGraph__Json__Export
from mgraph_ai.providers.json.domain.Domain__MGraph__Json__Graph    import Domain__MGraph__Json__Graph
from osbot_utils.utils.Files                                        import file_create_from_bytes
from osbot_utils.utils.Http                                         import url_join_safe
from osbot_utils.utils.Env                                          import get_env

from osbot_utils.type_safe.Type_Safe import Type_Safe

ENV_NAME__URL__MGRAPH_AI_SERVERLESS = 'URL__MGRAPH_AI_SERVERLESS'
PATH__RENDER_MERMAID                = '/web_root/render-mermaid'
PATH__RENDER_DOT                    = '/graphviz/render-dot'

class MGraph__Json__Screenshot(Type_Safe):
    graph       : Domain__MGraph__Json__Graph
    target_file : str = None

    def handle_response(self, response):
        if response.status_code == 200:
            screenshot_bytes = response.content
            if self.target_file:
                file_create_from_bytes(self.target_file, screenshot_bytes)
            return screenshot_bytes

    def execute_request(self, method_path, method_params):
        target_url       = self.url__render_method(method_path)
        response         = requests.post(target_url, json=method_params)
        screenshot_bytes = self.handle_response(response)
        return screenshot_bytes

    def export(self):
        return MGraph__Json__Export(graph=self.graph)

    def dot(self):
        dot_source       = self.export().to_dot().to_string()
        method_path      = PATH__RENDER_DOT
        method_params    = {'dot_source': dot_source}
        return self.execute_request(method_path, method_params)

    def mermaid(self):
        mermaid_code     = self.export().to_mermaid().to_string()
        method_path      = PATH__RENDER_MERMAID
        method_params    = {'mermaid_code': mermaid_code}
        return self.execute_request(method_path, method_params)

    def save_to(self, target_file):
        self.target_file = target_file
        return self

    def url__render_method(self, path):
        return url_join_safe(self.url__render_server(), path)

    def url__render_server(self):
        url = get_env(ENV_NAME__URL__MGRAPH_AI_SERVERLESS)
        # if not url:                                                                         # todo: see if there is a better place to put this check (maybe in a setup method)
        #     raise ValueError(f"in MGraph__Json__Screenshot.url__render_server, missing env var: {ENV_NAME__URL__MGRAPH_AI_SERVERLESS}")
        return url