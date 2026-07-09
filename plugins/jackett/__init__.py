from typing import Any, Dict, List, Tuple
from urllib.parse import quote, urlparse

from app.db.systemconfig_oper import SystemConfigOper
from app.helper.sites import SitesHelper
from app.log import logger
from app.plugins import _PluginBase
from app.schemas.types import SystemConfigKey


class Jackett(_PluginBase):
    # 插件名称
    plugin_name = "Jackett索引器"
    # 插件描述
    plugin_desc = "将 Jackett Torznab 接口注册为 MoviePilot 搜索索引站点。"
    # 插件图标
    plugin_icon = "Jackett_A.png"
    # 插件版本
    plugin_version = "1.2"
    # 插件作者
    plugin_author = "Codex"
    # 作者主页
    author_url = "https://github.com/jxxghp/MoviePilot-Plugins"
    # 插件配置项ID前缀
    plugin_config_prefix = "jackett_"
    # 加载顺序：需早于常规搜索任务读取站点列表
    plugin_order = 30
    # 可使用的用户级别
    auth_level = 1

    # 私有配置
    _enabled = False
    _server_url = ""
    _api_key = ""
    _indexer_id = "all"
    _site_id = "JackettIndexers"
    _site_name = "JackettIndexers"
    _result_num = 100
    _timeout = 30
    _proxy = False
    _message = "插件未启用"

    def init_plugin(self, config: dict = None):
        """
        初始化插件配置，并在启用时把 Jackett 注册为 MoviePilot 索引站点。
        """
        config = config or {}
        self._enabled = bool(config.get("enabled"))
        self._server_url = self.__normalize_server_url(config.get("server_url"))
        self._api_key = (config.get("api_key") or "").strip()
        self._indexer_id = (config.get("indexer_id") or "all").strip()
        self._site_id = (config.get("site_id") or "JackettIndexers").strip()
        self._site_name = (config.get("site_name") or "JackettIndexers").strip()
        self._result_num = self.__to_positive_int(config.get("result_num"), 100)
        self._timeout = self.__to_positive_int(config.get("timeout"), 30)
        self._proxy = bool(config.get("proxy"))
        self._message = "插件未启用"

        if not self._enabled:
            return

        if not self._server_url or not self._api_key:
            self._message = "请先填写 Jackett 服务地址和 API Key"
            logger.warn(self._message)
            self.systemmessage.put(self._message, title=self.plugin_name)
            return

        try:
            register_domain = self.__get_register_domain(self._server_url)
            if not register_domain:
                raise ValueError("Jackett 服务地址格式不正确")

            SitesHelper().add_indexer(register_domain, self.__build_indexer())
            self.__ensure_search_site_enabled()
            self._message = f"已注册 Jackett 索引器并加入搜索站点范围：{self._site_name}（{self._indexer_id}）"
            logger.info(self._message)
        except Exception as err:
            self._message = f"Jackett 索引器注册失败：{err}"
            logger.error(self._message)
            self.systemmessage.put(self._message, title=self.plugin_name)

    def get_state(self) -> bool:
        """
        返回插件是否处于启用状态。
        """
        return self._enabled

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        """
        当前插件不提供远程命令。
        """
        return []

    def get_api(self) -> List[Dict[str, Any]]:
        """
        当前插件不暴露独立 API。
        """
        return []

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        """
        拼装插件配置页面，需要返回两块数据：1、页面配置；2、默认数据结构。
        """
        return [
            {
                "component": "VForm",
                "content": [
                    {
                        "component": "VRow",
                        "content": [
                            {
                                "component": "VCol",
                                "props": {"cols": 12, "md": 4},
                                "content": [
                                    {
                                        "component": "VSwitch",
                                        "props": {
                                            "model": "enabled",
                                            "label": "启用插件",
                                        },
                                    }
                                ],
                            },
                            {
                                "component": "VCol",
                                "props": {"cols": 12, "md": 4},
                                "content": [
                                    {
                                        "component": "VSwitch",
                                        "props": {
                                            "model": "proxy",
                                            "label": "使用系统代理访问 Jackett",
                                        },
                                    }
                                ],
                            },
                        ],
                    },
                    {
                        "component": "VRow",
                        "content": [
                            {
                                "component": "VCol",
                                "props": {"cols": 12, "md": 8},
                                "content": [
                                    {
                                        "component": "VTextField",
                                        "props": {
                                            "model": "server_url",
                                            "label": "Jackett 服务地址",
                                            "placeholder": "http://jackett:9117",
                                        },
                                    }
                                ],
                            },
                            {
                                "component": "VCol",
                                "props": {"cols": 12, "md": 4},
                                "content": [
                                    {
                                        "component": "VTextField",
                                        "props": {
                                            "model": "api_key",
                                            "label": "API Key",
                                            "type": "password",
                                            "placeholder": "Jackett Dashboard 右上角 API Key",
                                        },
                                    }
                                ],
                            },
                        ],
                    },
                    {
                        "component": "VRow",
                        "content": [
                            {
                                "component": "VCol",
                                "props": {"cols": 12, "md": 4},
                                "content": [
                                    {
                                        "component": "VTextField",
                                        "props": {
                                            "model": "indexer_id",
                                            "label": "Jackett Indexer ID",
                                            "placeholder": "all",
                                        },
                                    }
                                ],
                            },
                            {
                                "component": "VCol",
                                "props": {"cols": 12, "md": 4},
                                "content": [
                                    {
                                        "component": "VTextField",
                                        "props": {
                                            "model": "site_id",
                                            "label": "MoviePilot 站点ID",
                                            "placeholder": "JackettIndexers",
                                        },
                                    }
                                ],
                            },
                            {
                                "component": "VCol",
                                "props": {"cols": 12, "md": 4},
                                "content": [
                                    {
                                        "component": "VTextField",
                                        "props": {
                                            "model": "site_name",
                                            "label": "MoviePilot 站点名称",
                                            "placeholder": "JackettIndexers",
                                        },
                                    }
                                ],
                            },
                        ],
                    },
                    {
                        "component": "VRow",
                        "content": [
                            {
                                "component": "VCol",
                                "props": {"cols": 12, "md": 4},
                                "content": [
                                    {
                                        "component": "VTextField",
                                        "props": {
                                            "model": "result_num",
                                            "label": "单次最多结果数",
                                            "type": "number",
                                        },
                                    }
                                ],
                            },
                            {
                                "component": "VCol",
                                "props": {"cols": 12, "md": 4},
                                "content": [
                                    {
                                        "component": "VTextField",
                                        "props": {
                                            "model": "timeout",
                                            "label": "请求超时（秒）",
                                            "type": "number",
                                        },
                                    }
                                ],
                            },
                        ],
                    },
                    {
                        "component": "VAlert",
                        "props": {
                            "type": "info",
                            "variant": "tonal",
                            "text": (
                                "Indexer ID 填 all 可搜索 Jackett 中全部索引器；"
                                "也可以填写 Jackett 里某个具体 Indexer 的 ID。"
                            ),
                        },
                    },
                ],
            }
        ], {
            "enabled": False,
            "server_url": "",
            "api_key": "",
            "indexer_id": "all",
            "site_id": "JackettIndexers",
            "site_name": "JackettIndexers",
            "result_num": 100,
            "timeout": 30,
            "proxy": False,
        }

    def get_page(self) -> List[dict]:
        """
        返回插件详情页，用于展示当前注册状态和实际 Torznab 入口。
        """
        return [
            {
                "component": "VAlert",
                "props": {
                    "type": (
                        "success"
                        if self._enabled and self._server_url and self._api_key
                        else "info"
                    ),
                    "variant": "tonal",
                    "text": self._message,
                },
            },
            {
                "component": "VTable",
                "props": {"density": "compact"},
                "content": [
                    {
                        "component": "tbody",
                        "content": [
                            self.__table_row("Jackett 地址", self._server_url or "-"),
                            self.__table_row("Jackett Indexer ID", self._indexer_id or "-"),
                            self.__table_row("MoviePilot 站点ID", self._site_id or "-"),
                            self.__table_row("MoviePilot 站点名称", self._site_name or "-"),
                        ],
                    }
                ],
            },
        ]

    def stop_service(self):
        """
        退出插件。
        """
        pass

    def __ensure_search_site_enabled(self):
        """
        把 Jackett 加入搜索站点范围，避免系统配置中没有任何有效站点。
        """
        selected_sites = SystemConfigOper().get(SystemConfigKey.IndexerSites) or []
        if not isinstance(selected_sites, list):
            selected_sites = []
        if self._site_id in selected_sites:
            return
        selected_sites.append(self._site_id)
        SystemConfigOper().set(SystemConfigKey.IndexerSites, selected_sites)
        logger.info(f"已将 {self._site_id} 加入搜索站点范围")

    def __build_indexer(self) -> dict:
        """
        构造 MoviePilot 内建 SiteSpider 可识别的 Torznab XML 索引器配置。
        """
        indexer_id = quote(self._indexer_id, safe="")
        api_key = quote(self._api_key, safe="")
        torznab_path = (
            f"api/v2.0/indexers/{indexer_id}/results/torznab/api"
            f"?t=search&apikey={api_key}&q={{keyword}}"
        )

        return {
            "id": self._site_id,
            "name": self._site_name,
            "domain": self._server_url,
            "is_active": True,
            "encoding": "UTF-8",
            "public": True,
            "proxy": self._proxy,
            "result_num": self._result_num,
            "timeout": self._timeout,
            "search": {
                "paths": [
                    {
                        "path": torznab_path,
                        "method": "get",
                    }
                ]
            },
            "torrents": {
                "list": {
                    "selector": "item",
                },
                "fields": {
                    "title": {
                        "selector": "title",
                    },
                    "details": {
                        "selector": "comments",
                        "optional": True,
                    },
                    "download": {
                        "selector": "enclosure",
                        "attribute": "url",
                    },
                    "date_added": {
                        "selector": "pubDate",
                    },
                    "size": {
                        "selector": "size",
                    },
                    "seeders": {
                        "selector": "torznab\\:attr[name=\"seeders\"]",
                        "attribute": "value",
                        "optional": True,
                    },
                    "leechers": {
                        "selector": "torznab\\:attr[name=\"peers\"]",
                        "attribute": "value",
                        "optional": True,
                    },
                    "grabs": {
                        "selector": "torznab\\:attr[name=\"grabs\"]",
                        "attribute": "value",
                        "optional": True,
                    },
                    "imdbid": {
                        "selector": "torznab\\:attr[name=\"imdb\"]",
                        "attribute": "value",
                        "optional": True,
                        "filters": [
                            {
                                "name": "re_search",
                                "args": [
                                    "(tt\\d+|\\d+)",
                                    0,
                                ],
                            }
                        ],
                    },
                    "downloadvolumefactor": {
                        "case": {
                            "*": 1,
                        }
                    },
                    "uploadvolumefactor": {
                        "case": {
                            "*": 1,
                        }
                    },
                },
            },
        }

    @staticmethod
    def __normalize_server_url(server_url: str) -> str:
        """
        规范化 Jackett 地址，保证后续拼接 API 路径时不会出现双斜杠。
        """
        server_url = (server_url or "").strip()
        if not server_url:
            return ""
        if not server_url.startswith(("http://", "https://")):
            server_url = f"http://{server_url}"
        return f"{server_url.rstrip('/')}/"

    @staticmethod
    def __get_register_domain(server_url: str) -> str:
        """
        提取 SitesHelper 注册用域名；本地 IP 或局域网域名会原样保留主机名。
        """
        parsed_url = urlparse(server_url)
        return parsed_url.hostname or ""

    @staticmethod
    def __to_positive_int(value: Any, default: int) -> int:
        """
        将配置中的数字转换为正整数，避免空值或非法输入导致插件初始化失败。
        """
        try:
            value = int(value)
        except (TypeError, ValueError):
            return default
        return value if value > 0 else default

    @staticmethod
    def __table_row(label: str, value: str) -> dict:
        """
        构造详情页表格行，减少重复的 Vuetify JSON 结构。
        """
        return {
            "component": "tr",
            "content": [
                {
                    "component": "td",
                    "props": {"class": "text-subtitle-2"},
                    "text": label,
                },
                {
                    "component": "td",
                    "text": value,
                },
            ],
        }
