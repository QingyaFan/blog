# 目录

收藏点star，订阅点watch

## 系列

按阅读顺序整理的系列入口；单篇索引见下方 ML/AI。

### 从零训练一个 360M 语言模型

固定双卡预算下，从规划、数据、评测一路做到 SFT、偏好优化与 RLHF。按训练生命周期顺序阅读。

| #    | 文章                                                      | 状态       |
| ---- | --------------------------------------------------------- | ---------- |
| 总纲 | 从零训练一个 360M 语言模型：系列总纲                      | 待发布     |
| 1    | 规划与验证：算力预算、MFU 标定与最小闭环                  | 待发布     |
| 2-10 | 数据、Tokenizer、评测、预训练、SFT、DPO、RLHF、迭代、复盘 | 随发布追加 |

### Agent Harness 工程

理论篇回答“为什么”，实现篇回答“怎么落地”。建议从实现篇导读开始，再按阅读路径选读。

| 篇目  | 文章                                                                                        | 状态       |
| ----- | ------------------------------------------------------------------------------------------- | ---------- |
| T0    | [Harness Engineering：从裸循环到可验证运行时](https://github.com/QingyaFan/blog/issues/231) | 已发布     |
| T1    | [Loop Engineering：让循环可信](https://github.com/QingyaFan/blog/issues/254)                | 已发布     |
| T2    | [Graph Engineering：让图可信](https://github.com/QingyaFan/blog/issues/255)                 | 已发布     |
| T3    | [拆解 Claude Code 的 Harness](https://github.com/QingyaFan/blog/issues/233)                 | 已发布     |
| T4    | [智能体评测：方法论全景与框架选型](https://github.com/QingyaFan/blog/issues/245)            | 已发布     |
| I0    | 从零打造 Agent Harness：实现篇导读                                                          | 待发布     |
| I1    | 从零打造 Agent Harness：最小循环                                                            | 待发布     |
| I2–I7 | 工具事务、上下文预算、生命周期、权限与沙箱、技能、观测与评测                                | 随发布追加 |

## ML/AI

1. [【工程】Agent 网关的职责边界：两条流量方向，一条状态线 — 2026/10/16](https://github.com/QingyaFan/blog/issues/253)
2. [【工程】模型服务网关的职责边界：LiteLLM 覆盖了什么，漏了什么 — 2026/10/16](https://github.com/QingyaFan/blog/issues/252)
3. [【工程】AI 写码时代的软件质量保障：一份完整的纵深防线清单 — 2026/10/12](https://github.com/QingyaFan/blog/issues/227)
4. [【Agent Skill】 最佳实践：写法、反模式与有证据的取舍 — 2026/10/12](https://github.com/QingyaFan/blog/issues/232)
5. [【Agent Skill】从哪里来，能做什么，走到哪一步了 — 2026/10/11](https://github.com/QingyaFan/blog/issues/249)
6. [【模型】决策模型与 Decision API：把「判断」从生成模型里拆出来 — 2026/10/10](https://github.com/QingyaFan/blog/issues/248)
7. [【智能体 + 知识库】智能体 + 知识库优化：哪些手段常用、哪些被高估 — 2026/10/05](https://github.com/QingyaFan/blog/issues/246)
8. [【Agent 知识库】AI 知识库演进：从经典检索到 Agentic RAG — 2026/10/03 ](https://github.com/QingyaFan/blog/issues/244)
9. [【Agent 记忆】AI Agent 的记忆：分类、来源、写入与使用 — 2026/10/02](https://github.com/QingyaFan/blog/issues/104)
10. [【Agent 记忆】Working Memory 中的 Blackboard（黑板）](https://github.com/QingyaFan/blog/issues/218)
11. [【工程】Python 做 AI 应用的性能考虑 — 2026/07/22](https://github.com/QingyaFan/blog/issues/210)
12. [【推理】vLLM 启动时加载 LLM 全过程解析](https://github.com/QingyaFan/blog/issues/202)
13. [【推理】推理引擎的 KV cache](https://github.com/QingyaFan/blog/issues/190)
14. [【推理】LLM 推理过程详解](https://github.com/QingyaFan/blog/issues/201)
15. [【推理】推理引擎与GPU环境](https://github.com/QingyaFan/blog/issues/212)
16. [【智能体】智能体与用户的交互协议：AG-UI 与 A2UI — 2026/10/13](https://github.com/QingyaFan/blog/issues/199)
17. [【智能体】智能体系统中两个角色：System和LLM](https://github.com/QingyaFan/blog/issues/220)
18. [【模型】BERT 系列进化史：三代各改一层——配方、结构、训练目标，2021 之后改效率 — 2026/10/15](https://github.com/QingyaFan/blog/issues/172)
19. [【模型-压缩】模型压缩方法概述](https://github.com/QingyaFan/blog/issues/217)
20. [【模型】深度学习模型与大模型](https://github.com/QingyaFan/blog/issues/75)
21. [【推理】vLLM入门](https://github.com/QingyaFan/blog/issues/85)
22. [【推理】测试大模型的推理性能](https://github.com/QingyaFan/blog/issues/93)
23. [【智能体】Tool-Calling 全链路：模型只提议，其余都是工程 — 2026/10/13](https://github.com/QingyaFan/blog/issues/96)

## Cloud Native

1. [【Kubernetes】CRD 设计：什么时候需要 Claim — 2026/10/22](https://github.com/QingyaFan/blog/issues/256)
2. [GMP：Go 并发的基础](https://github.com/QingyaFan/blog/issues/3)
3. [Go 写并发程序的模式](https://github.com/QingyaFan/blog/issues/44)
4. [通过可观测分析 go web apiserver 性能](https://github.com/QingyaFan/blog/issues/39)
5. [使用 go pprof 定位 web apiserver 性能瓶颈](https://github.com/QingyaFan/blog/issues/36)
6. [Go实现一个轻量工作流](https://github.com/QingyaFan/blog/issues/49)
1. [PaaS应该是一种什么形态？](https://github.com/QingyaFan/blog/issues/73)
2. [Kubernetes调度原理和扩展方法](https://github.com/QingyaFan/blog/issues/56)
4. [Batch Schedule 和 Volcano 的实现](https://github.com/QingyaFan/blog/issues/65)
5. [Kubernetes编排原理和定制（CRD）](https://github.com/QingyaFan/blog/issues/41)
6. [CRD Controller多副本选主](https://github.com/QingyaFan/blog/issues/55)
7. [CRD Controller 事件机制的设计](https://github.com/QingyaFan/blog/issues/58)
8. [在Kubernetes中使用GPU](https://github.com/QingyaFan/blog/issues/53)
9. [Kubernetes的核心编排调度能力们](https://github.com/QingyaFan/blog/issues/52)
10. [Configmap热更新原理](https://github.com/QingyaFan/blog/issues/2)
11. [Pod生命周期状态](https://github.com/QingyaFan/blog/issues/31)
12. [OpenKruise的CloneSet如何利用Pod状态实现原地变更](https://github.com/QingyaFan/blog/issues/42)
13. [Kubernetes的组件以及交互过程](https://github.com/QingyaFan/blog/issues/46)
14. [Docker的隔离原理](https://github.com/QingyaFan/blog/issues/47)
3. [OpenTelemetry 的设计](https://github.com/QingyaFan/blog/issues/57)
4. [Prometheus 横向扩展](https://github.com/QingyaFan/blog/issues/37)
5. [Prometheus 数据压缩](https://github.com/QingyaFan/blog/issues/38)
