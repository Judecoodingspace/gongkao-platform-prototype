# 公务员考试题库人工抽检中台

本仓库用于建设一个面向公务员考试历年真题的人工拆题、标注、审核与题库沉淀系统。

当前阶段是项目 Infra 与文档基线阶段，暂不进入正式业务代码开发。仓库内先沉淀：

- 项目原则与工程约束
- PRD 与规格文档
- 题目数据模型草案
- 人工拆题工作台临时可点击原型
- 后续 Codex / Claude Code 协作说明

## 目录结构

```text
.
├── AGENTS.md
├── HANDOFF.md
├── README.md
├── docs/
│   ├── PRD.md
│   ├── constitution.md
│   └── specs/
│       └── 001-question-annotation-workbench/
│           ├── acceptance-checklist.md
│           ├── data-model.md
│           ├── plan.md
│           ├── spec.md
│           └── tasks.md
└── prototypes/
    └── question-bank-prototype/
        ├── README.md
        └── index.html
```

## 当前原型

打开：

```text
prototypes/question-bank-prototype/index.html
```

该原型来自第一版手绘草图，覆盖题本上传、解析区、题目结构化录入、答案与审核流程提示。

## 开发原则

- 先规格，后代码。
- 任何 AI 解析结果不得绕过人工审核直接入正式题库。
- 所有题目必须保留来源追溯和版本历史。
- 所有重要改动都要有验收标准与验证方式。
