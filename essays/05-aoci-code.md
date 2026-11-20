# 让编码 Agent 从手头的仓库找到相关记忆

[English](05-aoci-code.en.md) · 中文

本文读的是上游提交 [`5f68ace`](https://github.com/aoci-spec/aoci-code/commit/5f68ace)，该版本的许可证为 [FSL-1.1-MIT](https://github.com/aoci-spec/aoci-code/blob/5f68ace/LICENSE)。

编码 Agent 接到一个任务时，往往已经知道自己在哪个仓、正在看哪个文件。读完 AOCI-CODE，我想试试能不能用这些开工时就有的线索，先找出值得读的几页记忆。

AOCI-CODE 把仓库地图和代码一起放在 Git 里。模型给文件和数据库表写短条目，记下职责、强关系、接口和容易漏掉的约束。程序拿源码指纹发现变动，再把需要更新的对象交给模型。Agent 可以通过 MCP 加载概览、按对象读条目，也可以用关键词和标签查找。 [AOCI-CODE README](https://github.com/aoci-spec/aoci-code/blob/5f68ace/README.md) · [MCP 规范](https://github.com/aoci-spec/aoci-code/blob/5f68ace/spec/public/aoci-mcp-runtime-v1.txt)

这里有个容易混淆的地方。假设一页经验提到重试，链接指向一个确实存在的重试函数。这个函数可能被几个服务共用，而页面讲的是其中一个服务的一次迁移。文件存在、版本对得上，只能证明引用可查。要把整页挂到某个服务，还得看这页的主题和适用范围。AOCI-CODE 的关系也是模型写的，程序从能解析的引用派生图，业务含义仍需核对。 [系统关系规范](https://github.com/aoci-spec/aoci-code/blob/5f68ace/spec/public/aoci-system-cognition-runtime-v1.txt)

我会先用公开仓库和合成记忆试一个小对照。给两组同样的题、同样的全局结果、同样的阅读预算。一组顺着搜索结果读，另一组用几个阅读位看任务实体下已经核过的页面。题里加上同名模块、过时页面和没有可靠锚点的例子。最后逐题检查必读页是否读全、是否读到错页，以及 Agent 有没有做对下一步。实验设想见[从任务上下文找实体的计划](../plans/plan-context-anchored-recall.md)。上游的黑盒验证提供了固定夹具和检查末态的方法，读页与行动的差异需要任务对照来量。 [上游黑盒套件](https://github.com/aoci-spec/aoci-code/blob/5f68ace/scripts/blackbox/README.md)
