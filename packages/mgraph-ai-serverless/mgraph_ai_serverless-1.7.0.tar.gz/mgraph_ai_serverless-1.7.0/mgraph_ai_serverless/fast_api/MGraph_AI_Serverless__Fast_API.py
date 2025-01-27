import mgraph_ai_serverless
from mgraph_ai_serverless.graph_engines.playwright.routes.Routes__Web_Root import Routes__Web_Root
from osbot_utils.utils.Files                                                import path_combine
from mgraph_ai_serverless.fast_api.routes.Routes__Debug                     import Routes__Debug
from mgraph_ai_serverless.graph_engines.graphviz.routes.Routes__Graphviz    import Routes__Graphviz
from mgraph_ai_serverless.graph_engines.playwright.routes.Routes__Browser   import Routes__Browser
from osbot_fast_api.api.Fast_API                                            import Fast_API
from mgraph_ai_serverless.fast_api.routes.Routes__Info                      import Routes__Info


class MGraph_AI_Serverless__Fast_API(Fast_API):
    base_path  : str  = '/'
    enable_cors: bool = True

    def path_static_folder(self):        # override this to add support for serving static files from this directory
        return path_combine(mgraph_ai_serverless.path, 'web_root')

    def setup_routes(self):
        self.add_routes(Routes__Info    )
        self.add_routes(Routes__Web_Root)
        self.add_routes(Routes__Graphviz)
        self.add_routes(Routes__Browser )
        self.add_routes(Routes__Debug   )


