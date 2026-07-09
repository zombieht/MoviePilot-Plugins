# Jackett 索引器

将 Jackett 的 Torznab 接口注册为 MoviePilot 内建索引站点，启用后可以在 MoviePilot 搜索、订阅搜索等流程中使用 Jackett 返回的资源。

## 使用方式

1. 在 Jackett 中添加并配置好需要使用的 Indexer。
2. 打开 Jackett Dashboard，复制右上角的 API Key。
3. 在 MoviePilot 插件配置中填写：
   - `Jackett 服务地址`：例如 `http://jackett:9117`
   - `API Key`：Jackett Dashboard 中显示的 API Key
   - `Jackett Indexer ID`：默认 `all`，表示搜索 Jackett 中全部 Indexer；也可以填写具体 Indexer ID。
4. 保存并启用插件后，MoviePilot 会新增一个名为 `JackettIndexers` 的索引站点。

## 注意事项

- Jackett 需要先能正常搜索对应站点，MoviePilot 才能获取结果。
- 插件通过 Jackett 的 Torznab XML 返回值解析标题、下载链接、发布时间、大小、做种数、下载数和完成数。
- MoviePilot 的搜索日志会记录请求 URL，Jackett API Key 可能出现在调试日志中，请勿公开日志。
- 如果 MoviePilot 与 Jackett 不在同一网络，请确认容器网络、端口映射和代理配置可达。
