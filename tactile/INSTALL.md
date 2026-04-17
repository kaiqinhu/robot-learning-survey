# 安装说明

将 `tactile-site/` 中的所有文件复制到 `robot-learning-survey-pages/tactile/` 目录：

```bash
cp -r /Users/hukaiqin/claude/tactile-site/* /Users/hukaiqin/robot-learning-survey-pages/tactile/
# 不要复制 INSTALL.md 和 main-index-patch.html
```

## 主站 index.html 修改

在 `robot-learning-survey-pages/index.html` 的 `</div><!-- end pill-grid -->` 之后、`</section>` 之前，添加以下内容：

```html
<section>
  <h2>深度专题: 触觉与具身智能</h2>
  <div class="pill-grid">
    <a href="tactile/index.html" class="pill-card">
      <div class="icon" style="background:#e0f2fe;color:#0e7490">T</div>
      <div>
        <h3>Tactile & Embodied AI Deep Dives</h3>
        <p>触觉采集硬件 / 具身 SoC / 模型融合 / 力觉世界模型 / 评测体系 / TTT — 垂直技术栈专题</p>
      </div>
    </a>
  </div>
</section>
```

或者直接用 `main-index-patch.html` 中的完整修改后 index.html 替换。
