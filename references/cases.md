# 案例导航

案例按材料关系选择，不按相同名词硬套。下面为历史样本或教学示范，不证明复用效果；只借机制，人物、金额、收入和经历不迁移。

## 完整范例优先入口

| 当前材料 | 可读范例 | 可借的选题动作 |
|---|---|---|
| 一个可检验的问题和操作条件 | `cases/script_exemplar/exemplar-process-128` 轻食半成品实测 | 疑问→样本→操作→比较观察→限制外推 |
| 一个设想和制作过程 | `cases/script_exemplar/exemplar-process-149` 厨房模型 | 设想→原型→过程→结果；模型不能冒充实际交付 |
| 想体验一个职业 | `cases/script_exemplar/exemplar-story-061` 宠物殡葬师 | 系列框架、本期职业、工作过程与人物关切 |
| 一段身份转变经历 | `cases/script_exemplar/exemplar-story-071` 烂尾楼业主到律师 | 用事件、行动和阶段变化收束履历 |
| 对一个消费/服务过程有疑问 | `cases/script_exemplar/exemplar-process-047` 体验变化 | 现场问题、条件、互动、体验；原例为演绎，不当调查证据 |

## 教学模板里的其他题源

| 模板 | 选题机制 | slug |
|---|---|---|
| 地州孩子在省会安家 | 抽象压力落成具体账目与选择 | `cases/community_template/xiaoe-06a48e05111edfb0` |
| 妈妈改造出租屋 | 一次可见行动承载身份与情绪 | `cases/community_template/xiaoe-3f1da4d170719708` |
| 上课爱睡觉的人当老师 | 过去的小缺点与现在身份反差 | `cases/community_template/xiaoe-a95ac1a51474fd73` |
| 手机店转型 | 行业变化落到经营者的选择 | `cases/community_template/xiaoe-3756ff11c99164d0` |
| 同城信息 | 地点＋具体任务＋人群关切 | `cases/community_template/xiaoe-6445eeaba2333253` |
| 大米价格阶梯 | 同一物品按受众、属性、便利性等变化提问 | `cases/community_template/xiaoe-e27a7846fb8d0eb3` |

## 历史标题样本

`cases/topic_title/topic-case-8de99457aa582b62`：少量收入与失败复盘；`cases/topic_title/topic-case-c01183f48bc47825`：等待裁员还是主动离职的两难。

这些仅有标题机制与兑现要求，不是完整范文，不补写“原标题作者怎么做到的”。257条标题样本偏公众号、职业、副业与成长，不能代表所有平台和题材。

## 如何扩大

`source-index.jsonl` 保留435条案例入口，包括160个教学模板、18个完整范例、257条标题案例。本次入口只直连少数教学模板，不能只沿工作流链接就宣布案例查全。用查询脚本按人物、场景、任务和关系寻找，读取命中的完整页面再借鉴。

示例：`python3 scripts/lookup.py --query '过程 体验' --kind case --limit 8`。多词按命中数排序；结果总数与分页可见。默认元数据命中不是语义穷举，没找到时换同义词或查 Wiki 关联。
