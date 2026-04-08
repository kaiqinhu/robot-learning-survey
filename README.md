# Robot Learning Survey 2026

2026 年机器人学习领域综述，涵盖 87+ 篇论文，横跨五大技术范式。部署于 GitHub Pages 静态站点。

**在线阅读:** [https://kaiqinhu.github.io/robot-learning-survey](https://kaiqinhu.github.io/robot-learning-survey)

## 内容导航

| 页面 | 主题 | 说明 |
|------|------|------|
| `survey.html` | 完整综述 | 万字长文，含引用和参考文献 |
| `p1-vla.html` | VLA | 视觉-语言-动作模型 |
| `p2-wam.html` | 世界模型 | 物理预测与世界动作模型 |
| `p3-rl-sim2real.html` | RL & Sim2Real | 强化学习与仿真到真实迁移 |
| `p4-diffusion.html` | 扩散策略 | Diffusion / Flow Matching 动作生成 |
| `p5-hybrid.html` | 混合范式 | VLA + 世界模型 + RL 三路融合 |
| `p6-unitree.html` | 宇树生态 | Unitree 人形机器人技术栈 |
| `p7-citation-graph.html` | 引用图谱 | 交互式论文引用网络可视化 |

## 项目结构

```
papers.json     # 论文数据库（87+ 条目、引用图谱、时间线）
papers.js       # 由 papers.json 自动生成的 JS 包装
render.js       # 共享渲染器（导航栏、论文卡片、时间线）
shared.css      # 共享样式，支持移动端响应式
index.html      # 首页
```

站点采用数据驱动架构：HTML 页面通过 `data-ids` 属性声明所需论文，`render.js` 在运行时从 `papers.json` 渲染卡片、时间线和导航栏。

## 开发

修改论文数据后，运行以下命令重新生成 JS 文件：

```bash
python3 -c "
f=open('papers.json'); d=f.read(); f.close()
f=open('papers.js','w'); f.write('window.SURVEY_DATA = '+d.rstrip()+';\n'); f.close()
print('done')
"
```

本地预览：直接在浏览器中打开任意 HTML 文件即可。

## 许可

本仓库内容仅供学习和研究使用。
