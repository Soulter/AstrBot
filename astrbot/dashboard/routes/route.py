from astrbot.core.config.astrbot_config import AstrBotConfig
from dataclasses import dataclass
from quart import Quart


class Route():
    def __init__(self, config: AstrBotConfig, app: Quart):
        self.app = app
        self.config = config
    
    def register_routes(self):
        for route, (method, func) in self.routes.items():
            self.app.add_url_rule(f"/api{route}", view_func=func, methods=[method])

@dataclass
class Response():
    status: str = None
    message: str = None
    data: dict = None

    def error(self, message: str):
        self.status = "error"
        self.message = message
        return self

    def ok(self, data: dict={}, message: str=None):
        self.status = "ok"
        self.data = data
        self.message = message
        return self