# CHANGELOG(omni2docx)

### 0.6.7 — 2026-10-14（描述句收进帽内：长度 360→292，语义零变化）

- 只做一件事：把 frontmatter 的 `description` 压到长度帽内（现测 **292**，帽 300；`summary` 64 未动）。压的是连接词与冗饰（「将…重建为保真/展示/汇报」「grounded…→源页分页」「导出打印件」「粘贴微信公众号」这类），**十一项信息单元逐条复测仍在**：三格式、页锚点分页、真标题+目录、表格脚注溯源、多源证据附录、`--profile` 公文/诉讼/研报制式、`--pdf` 打印件、`--inline` 公众号不重排、版式池 kpi/compare/timeline、`Do NOT use for` 边界句、`Triggers:` 全族——触发词**一个未删**（词例 8 处、标签 1 处，与改前同数）。
- 没玩纸面达标：长句没有被整段搬去 README 充数——`README.md` 与 `README.en.md` 本轮 diff 为 0，被压掉的字面在两面上也查不到（现测各 0 处）。
- 如实报两件事：票面列的四件要素里，「离线／零网络」句与「评级·目标价待人工」这类合规句**原本就不在本件描述面**（改前现测各 0 处，且整份 SKILL 正文内「零网络／离线／待人工／评级／目标价」也各 0 处）——本轮按「语义零变化」执行，没有为了凑清单往描述面新加没做过的承诺；要不要补这两句属能力句新增，另票再裁。
- 版本位：0.6.6 → 0.6.7（描述句压缩＝patch，**语义零变化**：判据、参数、产物形制与两面 README 均未动）。历史条目不回改。

### 0.6.6 — 2026-10-14（文档跟码：验收规则编号补进 README 双语，逐号写判什么／为何命中／怎么改）

- 上一版给验收器挂了稳定编号（PPTX 八条 PX-01..PX-08、DOCX 两条 DX-01/DX-02），但两面 README 一处没写、SKILL 只有一句「带稳定编号」的概括——用户从 README 装完包，看到一条 `PX-08` 不知道该改什么。本轮补文档面：README 双语各加一节，十枚编号逐号写清**判什么（码内现值）／为什么会命中／怎么改源 md 或渲染参数才过**，全部含一次逐号在场（现测两面各 10/10）。
- 语义一律从 `scripts/validate_pptx.py` 与 `scripts/validate_docx.py` 码内现值取，不凭编号名猜、也不把 SKILL 那句复写一遍：覆盖率是 CJK 逐字口径（PPTX 合并正文＋表格单元格＋演讲者备注；DOCX 锚句命中率只作参考不计入判定）、空页容差是 max(1, 页数//10)、有彩色上限 `MAX_CHROMATIC`＝3 且饱和度 >24 才算有彩色（近灰不计）、字号反差下限 `MIN_CONTRAST`＝2.0、严重溢出按估计行高 > 盒高 1.3 倍（估宽 CJK≈1em/字、ASCII≈0.56em、空格≈0.3em）、圆角与阴影按形状 XML 的 `roundRect`／`a:outerShdw`/`a:innerShdw` 计数、DX-02 按未应用边框的表格数。**几何审计里的越界／重叠／过小字号是信息项，不判 PASS/FAIL**，这一条也写进面内，免得读者把计数当判分。
- 面内加了一句边界：编号是回归定位用的地址、不是能力承诺，阈值改了以码为准。
- 零改动清单：两支验收器与渲染器、`tests/` 全部判据与用例、SKILL 正文与上一版条目里那句制式经验记述（它在历史条目内，三面成品面现测均 0 处，本轮也未回改）——本轮只动文档；`python3 tests/run_all.py` 复跑退码 0，自报「合计 35 例，PASS 35，FAIL 0」＋末行「全部回归通过」，证明判据未受影响。
- 版本位：0.6.5 → 0.6.6（文档跟码＝patch，无能力增减）。历史条目不回改。

### 0.6.5 — 2026-10-14（验收器规则编号 + PPTX 文本框溢出门禁 + docx 表格边框护栏）

- **验收违规带稳定规则编号**（汲取 workbuddy-office 质量门禁经验：编号可定位到行、便于回归）：`validate_pptx.py` 七条既有违规改挂 `PX-01…PX-07`（CJK 覆盖率/零页/空页/圆角矩形/阴影/有彩色数/字号反差），`validate_docx.py` 覆盖率判 `DX-01`。
- **PPTX 文本框溢出估算（PX-08）**：python-pptx 不自动裁剪，文字超出盒子高度会被 PowerPoint 截断/挤压。新增 `box_overflow` 估算器（逐段按字号估折行 × 行高(1.2×字号) + 段后距 + 文本框内外边距，与盒子高度比较；CJK≈1em/字、ASCII≈0.56em、空格≈0.3em）。几何审计新增「文本框溢出 / 严重」计数；**严重溢出（估需高 > 盒高 1.3×）判 FAIL**。
- **docx 表格边框护栏（DX-02）**：`table_borders_audit` 在单元格级（`tblPr/tblBorders`）核验每张表都经 `style_table` 写入边框——引擎所有 `add_table` 路径（正文表 + 溯源附录表）必经 `style_table`，若某表 tblPr 无 `tblBorders` 即疑似绕过（回归/第三方改造风险）。命名样式（Table Grid 等）边框不在此层，但 `style_table` 会覆盖式写入，故正常产物必带。
- 回归：`tests/run_all.py` 双套件全 PASS（35 例 + docx 13 例，新增 PX/DX 编号与溢出/边框护栏零误报）。

### 0.6.4 — 2026-10-12（主指令瘦身 + 封面标记扩展 + 限制诚实化）

- **SKILL.md 瘦身**（368→约 350 行决策面）：「解析侧能力现状」五行长单元格收敛为四行一句话口径表（决策要点保留，完整取数纪律仍在步骤 1，不丢信息）；「验收口径」两张大实测表 + 溯源附录实测表压成三条结论行，逐版数据指向 CHANGELOG——实测证据不删，只是从每次加载的主指令挪到版本史。
- **封面标题标记扩展**：`extract_title`（build_docx，三渲染器共用）从只认「标题：」扩为三种显式标记 `标题：` / `题目：` / `Title:`（大小写不敏感）；仍**不做**「首行像标题就提」的启发式——误提正文首行会静默毁结构，需要封面时显式给标记或 `--title`。单测 5 例全过。
- **HTML 打印页码：诚实记为限制而非假实现**：Chromium 不支持 `@page` margin-box 的 `counter(page)`，引入 paged-media polyfill 违背自包含单文件原则——不做。SKILL.md 已知限制第 9 条 + README 能力边界明示：要页码的定稿走 Word（`--page-numbers`）或 PPTX（页脚），HTML 源页信息用 `--page-marks` 文内标注。
- 回归：`tests/run_all.py` 双套件全 PASS（extract_title 改动经 docx 矩阵覆盖）。

### 0.6.3 — 2026-10-12（验收入口补齐 + --inline 回归 + 文档口径）

- **validate_docx.py 增加 `--md` 源输入**：此前只收 `--json`，场景①（`--md` 直出，无中间 JSON）的保真验收无路可走——README 上手流程照抄即报错。现与 validate_html/validate_pptx 同口径：`--json`（场景②③）/`--md`（场景①）互斥二选一。实测 edge_case `--md` 直出 + `--md` 验收 PASS。
- **回归矩阵补 `--inline` 用例**（专项 4，此前 0.6.0 只靠手工验证）：渲染 `--inline` 后验收 PASS + 三条断言——style 属性内联落地（≥20 处）、`<style>` 块之外 var() 零残留（块内 var 是刻意保留的悬停/斑马纹，不算残留）、无外链（自包含保持）。实测样本 43 处内联 PASS。
- **测试计数 bug 修复**：带附加信息的 PASS 变体（`PASS（…）`）被 `res == "PASS"` 误计为失败，改为前缀匹配。
- **文档口径**：SKILL.md 步骤 4 补 validate_docx `--md` 与三验收器同口径说明；新增「PPTX `--profile` 与 Word 不同语义」段（deck 主题预设 vs Word 制式参数，HTML 与 Word 同口径）；README 上手补场景①验收命令、验收口径段补 `--no-toc` 与 `--inline` 矩阵覆盖说明。
- 回归：`tests/run_all.py` 双套件全 PASS（docx 矩阵 + 三格式闭环 35 例，含新增 inline 用例）。

### 0.6.2 — 2026-10-12（用户视角全面打磨）

- **修复 SKILL.md 结构缺陷**：步骤 4 验收器路径误写 `<skill_dir>/validate_*.py`（实际在 `scripts/` 下，照抄会 FileNotFoundError）；「验收口径」第二组实测行缺表头（markdown 断表，渲染为纯文本），并入上方主表；残留 HTML 实体 `&#x6210;` 改回「成」；步骤 3 开关清单补 `--page-numbers` / `--strip-emoji`。
- **删除死参数 `--brand`**（render_pptx.py）：0.5.0 移除顶部导航条后 `self.brand` 无任何渲染消费，`--brand` 成了静默无效的用户开关——连同 Deck/build 的 brand 参数管道一并清除；`--strip-emoji` 补 help 文案；validate_docx.py 的 ArgumentParser 补 description（唯一没有描述的 CLI）。
- **README 补齐**：文件表补 `CHANGELOG.md` 与 `tests/`（clone 后可复现）；上手段补 `--inline` 公众号用法；渲染器描述补版式池/几何审计能力。
- **frontmatter**：description 补 `--inline` 公众号粘贴与 PPT 版式池触发词（公众号排版 / 汇报 deck）。
- **术语口径修正**：公开面统一以「用户」指称交付物的读者，不再泛称「人」——人层→用户层、人可读可编辑→用户可读可编辑、给人→给用户、agent→人粘合→agent→用户粘合（SKILL.md / README.md / build_docx.py 文档注释），功能零改动。
- **条目归位修正**：上一条术语口径改动实际随本版发出（0.6.1 在架件内不含它），故从 0.6.1 段移入本段——渠道上的 0.6.1 从未载有该条。

- 回归：`tests/run_all.py` 全 PASS；PPTX 渲染冒烟通过（brand 管道清除无回归）。

### 0.6.1 — 2026-10-12（不变性承诺收窄：只覆盖原文/证据位）

- **修正定位表述**：引擎不承诺「同输入恒同输出」的整体确定性。不变性只覆盖**原文/证据位**——引文、数字、日期、名称、〔来源〕标注、说话人/画面转写、页码锚点、脚注，一经写入不得被排版或重写改动；标题措辞组织、切页、版式、要点取舍属设计决策，同一输入两次生成允许合理差异。验收（覆盖率/分页/表格数）本就只对证据位与结构计数断言，与此口径一致。SKILL.md「不许编造」铁律旁补记该边界。

### 0.6.0 — 2026-10-12（设计铁律断言 + PPT 语义版式池 + 微信 inline CSS 导出）

- **校验器新增「设计铁律」断言**（业界同类排版工具把设计约束写成可机械判定铁律的通行做法，翻成验收断言）：validate_pptx/validate_html 各增 `[设计铁律]` 节并参与判定——直角（圆角矩形/非零 border-radius=0）、禁阴影（outerShdw/box-shadow=0）、有彩色 ≤3（RGB 极差 >24 计彩，近灰不计）、字号极端反差（deck 最大字号 ≥2× 最小）、HTML 必含 CJK 字体栈、主文对比度 ≥4.5（--ink vs --panel，WCAG 公式实算）。现有产物实测：有彩色 1 种（#8C6A3F）、反差 5.0（deck）/16.67（HTML），全 PASS。
- **PPT 语义版式池**（锁定契约：版式锁死、数量由内容决定，agent 按内容语义选用）：提纲 md 用 `<!-- layout:kpi|compare|timeline -->` 指令绑定版式（支持写在标题前/后，双向绑定）；`kpi`=强制 KPI 塔看板（宽松数字抽取：数字开头即入塔、单位 ≤2 字、剩余作看板标签，≤4 列竖 hairline 分隔）；`compare`=两栏对比（垂直 hairline 中分）；`timeline`=纵向时间线（左 hairline 轴+方形节点，遵守直角铁律）。前置条件不满足自动回退 auto；XML 特征实证三版式生效（大数字 3/中分线 1/节点 4）。
- **HTML `--inline` 导出**：新增 CSS 内联器（纯 stdlib）——解析 `<style>`（剥注释/跳过 at-rules/@media print 绝不内联/解 :root 变量/丢弃伪类规则），按选择器复合匹配 + 祖先链粗匹配 + 可继承属性（color/font-family/font-size/line-height/text-align）级联，把全部排版写入元素 style 属性（实测 55 元素、var 零残留）。`<style>` 保留（悬停/斑马纹本地不退化；微信粘贴被剥离也无损）。粘贴公众号不重排。
- **SKILL.md**：新增版式池用法与「不许编造」agent 编排铁律（数字/日期/名称必须来自 Omni 解析原文，KPI 塔只收真实数字，无数据留白不造）。
- 验收：docx 回归矩阵 13/13 PASS（覆盖率 100%）；layouts.pptx 三版式 deck 几何 0/0/0 + 设计铁律 PASS；demo_inline.html 保真 PASS + 铁律 PASS。

### 0.5.2 — 2026-10-12（公开面口径清理：不点名任何第三方平台；回归用例名改能力描述）

- 依据套件级红线「不点名任何平台、不以对抗平台为叙事」与 CONTRIBUTING「记录性引用不复现词面」：本包公开面（历史条目与三支脚本的注释）中原先点名某第三方产品视觉语言的字样**共 25 处**，一律改为不可命中的形制指代（写作「克制体系（细线＋大留白）」「去掉色块语言」「避免与任何同类产品雷同」一类）；另把一处回归用例名从内部流水号形制改为能力描述。
- **动因、动作与事实一律不改**：视觉体系的实现、色板与版式代码零改动，本次只改记法与注释文字。
- 改后复测（与改前逐项同值）：三格式产物字节一致——PPTX 61,341 B／HTML 30,562 B／DOCX 出口行 `blocks=117 outline_nodes=62 segments=7 pagebreaks=6`；件内回归矩阵全部通过；三道验收器（docx／html／pptx）均 PASS，其中 pptx 几何审计越界 0／重叠 0／过小字号 0、html 自包含无外链；缺 headless 浏览器时 PDF 走**明示跳过**而非静默或假成功。
- 全包点名词面复算 0、流水号形制复算 0；`git diff` 内功能行 0（仅注释与文档文字）。

### 0.5.1 — 2026-10-12（0.5.0 复审修复：目录溢出回归 / 圆角残留 / 封面强调线统一）

- **PPTX `toc_slide` 行高回归修复**：0.5.0 误将行高改为 `max(0.62in, min(0.92in, …))`，目录条目 ≥8 时会挤出页面底部（几何审计只查形状边界、目录文本框自适应掩盖了问题）。改回纯自适应 `min(0.92in, 可用高度/n)`；条目 >10 时目录字号自动降为 16pt 保持可读。已用 12 条目压力样本验证：越界 0/重叠 0/过小字号 0。
- **HTML `code` 圆角残留**：0.5.0 宣言"去掉所有 border-radius"，但 `code` 内联样式的 `border-radius:3px` 漏改。已改 `border-radius:0`（全格式直角一致；已验证渲染产物中 `border-radius:[1-9]` 计数为 0）。
- **封面强调线三格式统一**：0.5.0 中 Word 封面标题下线误用 hairline，而 PPTX 封面/HTML hero 用 accent 短细线（全格式唯一强调点）。Word 已改 accent（`sz=16`），三格式封面语义一致。
- **代码卫生**：PPTX `_kw_runs` 硬编码 `#0F172A/#334155` 改为主题驱动（`theme["ink"]`/`theme["text"]`，去掉 `@staticmethod`）；`_bullet` 有序编号清理元组残留写法；`build_docx.py` 两处过时注释（"第三方同类产品：表头填充+斑马纹"→"编辑式极简"）与 `cover()` 调用处无效 `kicker` 传参清理。
- 回归：`run_matrix_test.py` 13/13 全 PASS（覆盖率 100%）；docx 验收 PASS（字符零丢失）；PPTX 几何审计 PASS；12 条目 TOC 压力样本 PASS。

### 0.5.0 — 2026-10-12（视觉重新实现：原创「编辑式极简」体系，四格式统一，避免与任何同类产品雷同）

- 需求：四格式统一原创、编辑式极简方向；**不再沿用 第三方同类产品 的色块语言**（顶部导航条 / kicker 角标 / PART 0X / 填充色块 / 表头填充 / 斑马纹 / 圆角卡片 / 左 accent 竖条）。改为**近单色 + 单一克制强调色（仅用于微小标记：序号、短细线）+ 大留白 + 强字号层级 + 细灰 hairline**：
  - **PPTX（`render_pptx.py`）**：删顶部导航带（`_nav` 置空）、封面去左色块/kicker 改「白底大留白 + 墨色大标题 + 标题下短 accent 细线 + 灰副标」；目录去序号卡改「序号（淡灰）+标题」；章节页去顶带/PART kicker 改「右侧幽灵大序号（淡灰）+墨色标题」；内容页去 kicker 改「墨色结论式标题+细灰线」；**KPI 看板去填充/边框**改「无填充列 + 竖 hairline 分隔 + 墨色大数字」；**表格去填充/斑马/四边框**改「表头墨色加粗+底部墨色粗线、行间 hairline」；要点引导符 accent→灰；结束页去上下色带。
  - **Word（`build_docx.py`）**：封面去 kicker/顶线改「Title 墨色大标题+底部细灰线+灰副标」；`目录` 标题改细灰下划、条目去彩色 `▪/·` 项目符号；`accent_heading` 仅 H1 底部细灰线、**H2 去左 accent 竖条**（纯字号层级）；`style_table` 去表头填充/斑马/四边框改「表头墨色加粗+底部粗线、行间 hairline、无竖线/外框」（新增幂等 `set_cell_shading`，删 `set_table_borders`）；引用/标注段去底纹改「细灰左线+灰字」；页脚 accent 线→hairline。
  - **HTML（`render_html.py`）**：`css_for` 重写——hero 去 primary 满底改「白底+墨色标题+accent 细线下划」；`h2` 去左 accent 竖条改底部 hairline、`h3` 降为灰字；表格去表头填充/外框/阴影/斑马改「表头底部墨色粗线+行间 hairline」；`blockquote`/`.visual` 去底色/圆角改「细灰左线+灰字」；`nav.toc` 去圆角卡片改「底部 hairline 分隔」；去掉所有 `border-radius`（直角）。
  - **PDF**：仍走 HTML→headless 打印，自动继承同套编辑式极简样式（`@media print` 保留 hero 与配色）。
- 主题令牌：`THEME`/`THEMES`/`HTML_THEMES` 统一为 `ink(#1A1A1A)/muted(#6E6E6E)/faint(#9A9A9A)/hairline(#DCDCDC)` + 每 profile 单一强调色（default 铜 `#8C6A3F`、academic 蓝 `#2E4A7A`、gov 红 `#8A2B2B`、legal 褐红 `#7A3B2E`、finance 青 `#1F6F6B`）；`primary` 保留为强调色别名。
- 保真与校验口径**不变**：字符零丢失；`目录`=Heading 1、`Title` 样式保留；分页/层级/表格数未改。
- 回归：`run_matrix_test.py` 13/13 全 PASS（覆盖率 100%，专项断言全绿）；PPTX 几何审计越界 0/重叠 0/过小字号 0；docx 验收 PASS；确认 deck 无大色块填充（accent 仅作细线）。

### 0.4.2 — 2026-10-12（Word 视觉重做：克制体系（细线＋大留白），四格式统一）

- 参照 第三方同类产品 共用设计哲学，对 `build_docx.py` 视觉层提质，使 **Word 与已完成的 PPTX(0.4.1)/HTML(0.4.0) 在同一套三色主题**（primary/accent/ink/panel/muted，default/academic/gov/legal/finance 各一套）下观感一致——PDF 走 HTML 打印，自动继承同套样式：
  - **封面 hero**：顶部 accent 细线 + accent kicker（如"Omni 解析重建"）+ 标题（保留 Word `Title` 样式，底部 primary 下划）+ 来源·日期副标题（灰）。
  - **目录美化**：`目录` 标题底部 accent 下划；条目按层级缩进，一级 `▪` accent 标记、次级 `·` 灰标记。
  - **标题装饰**：H1（含 level1） 底部 primary 下划；H2 左侧 accent 竖条（与 HTML `h2` 左竖条、PPTX accent 短下划一致）；标题文字仍走样式深墨色（保留"黑色基线"，不整段染色）。
  - **表格美化**：表头 primary 填充 + 白字、偶数行 panel 斑马纹、整表细灰边框（XML 直设，不依赖模板内置表样式，跨 Word/WPS 一致）。
  - **引用/标注段**：accent 左条 + panel 浅灰底 + 灰字，明示"引用/视觉理解"区别于正文。
  - **页脚**：顶部 accent 细线 + 来源（左，灰） + `PAGE` 域页码（右），域随分页自动更新。
  - **hr**：改为居中 accent 短下划（替代原灰色长虚线）。
- 保真与校验口径**不变**：字符零丢失（`validate_docx` 覆盖率口径）；`目录` 仍为 `Heading 1`、`Title` 样式保留；分页/标题层级/表格数量未被改动。
- 回归：`tests/run_matrix_test.py` 13/13 全 PASS（覆盖率 100%，`page_field`/`no_emoji`/`quote_kaiti`/`nested_inline`/`cjk_space_clean` 等专项断言全绿）。

### 0.4.1 — 2026-10-12（PPTX 视觉重做：克制体系（细线＋大留白），修正"空/丑"）

- 参照 第三方同类产品 `pptx` skill 的**克制设计哲学**（work_report / strategic / academic 规范）重做 `render_pptx.py` 视觉层，修正上一版"内容页只剩标题+`▪`平铺"的空与丑：
  - **双框结构**：顶部导航带（品牌 + 当前章节，白字）+ 底部页脚（来源 + 页码），专业且能跟踪进度。
  - **字号层级**（第三方同类产品 规范）：封面 44+、页标题 30、正文 19、KPI 44-54、导航/页脚 12。
  - **KPI 大数字看板**：自动识别数字型要点（如 `78 年`/`12 部`/`5 个`），渲染为直角卡片（浅 primary 底 + primary 边框 + 大号主色数字）。
  - **要点加粗首关键词** + accent 短引导符（`—`）；有序列表带 `01/02` 编号；≥6 条且偏短自动双栏。
  - **封面左色块 hero**（直角主色块 + accent 右缘线 + 品牌 kicker + 大标题 + accent 短下划线 + 副标题）；**章节页**幽灵大序号（浅 tint）+ `PART 0X` kicker；**结束页**上下主色带框定。
  - **禁用圆角矩形**（第三方同类产品 明确禁止），一律直角；颜色 ≤3；形状无文本不触发重叠审计。
  - 新增 `--brand`（顶部导航品牌字）。
- 几何审计零越界 / 零重叠 / 零过小字号；CJK 覆盖率 100%；回归 docx 13/13 + 三格式 34/34 全绿。

### 0.4.0 — 2026-10-12（视觉提质：主题色系统 + 分页型版式 + 装饰体系）

- 参照 第三方同类产品 `pptx` skill 的设计哲学重做两个展示渲染器的视觉层（解析/build 管线、chunk/flush/prose 语义、CLI 与多源合并均不变，回归全绿）。
- `render_pptx.py` 重做：
  - **主题色系统**：每个 profile 一套克制三色（primary / accent / 中性灰，背景以白或极浅灰为主，符合学术/商务规范；default/academic/gov/legal/finance 各一套）。
  - **分页型版式**：`封面`（左侧主色竖条 + 顶部分隔线 + 大标题 + 副标题 + 页脚）→ `章节分隔`（顶部主色条 + 大号序号 + 章节标题）→ `内容`（标题栏 + 主题色下划线 + 内容区左侧 accent 竖条 + 彩色项目符号 `▪` + 页脚来源/页码）→ `结束页`。不再把正文逐段平铺成上百页。
  - **栅格平衡 + 装饰克制**：统一页边距、底部页脚分隔线、序号、彩色项目符号；装饰元素均为无文本形状，不触发几何重叠审计。
  - **表格美化**：表头主题色底 + 白字、斑马纹、四边细灰边框（XML 设置，python-pptx Cell 无 `border_size`）。
  - 新增 `--source-label`（页脚来源署名）、`--ratio` 支持自定义尺寸。
- `render_html.py` 升级：CSS 引入主题变量（与 PPTX 同套配色，跨格式一致）；新增**封面 hero**（主题色块 + 标题 + 来源/日期）；目录改为卡片网格；`h2/h3` 左侧 accent 竖条；表格表头主题色底白字 + 斑马纹 + 阴影；引用/视觉块 accent 左边框；代码/强调色提纯。
- 跨格式语义固化：**HTML=展示（全量正文）**，**PPTX=汇报（要点上页、正文进演讲者备注）**——两者视觉提质但职责不变。
- 版本位：0.3.0 → 0.4.0（展示渲染器视觉重大增强；docx 引擎与解析行为不变）。

### 0.3.0 — 2026-10-11（效果维度：视觉评审驱动 + 无分隔行表格 + 目录治理）

- 效果验证新增两链：**视觉评审**（headless 浏览器截图逐制式人审——本轮即靠它抓出四项）与**几何审计**（`validate_pptx.py` 内置形状越界/文本框重叠/过小字号检查，信息项输出）。
- 修复**来源路径泄漏**：HTML 页首不再印原始解析路径（含本机目录，丑且泄隐私）；需要溯源用 `render_html.py --source-label "XX研报"` 显式署名。
- 表格识别兼容**无分隔行表格**：连续 `|` 行（xlsx/部分导出常见）按表处理、首行作表头（≥2 行且八成以上行含 ≥2 单元格才判表；不达标的孤立 `|` 行按普通段消费——本分支必须至少消费 1 行，否则 para 空转死循环，实测已踩）。正文内嵌 `|` 分隔文本属源数据质量，原样保留不猜结构。
- 目录治理：`render_html.py --toc-depth N`（默认 2）控目录深度；目录列表去 `<ol>` 自动编号（标题多自带"一、/3.1"编号，叠加即双重编号）。
- OCR 件已知边界：逐字母拆字标题词边界不可还原，引擎不强修；SKILL.md 明确建议 agent 渲染前先清洗 markdown。
- PPTX 几何审计实测 13 例真实语料全 0（越界/重叠/过小字号）；视觉复审三制式截图确认四项全消。
- 版本位：0.2.1 → 0.3.0（新 CLI 参数 + 解析行为增强）。

### 仓库基础设施（不计入运行时版本）— 2026-10-11

- 新增 `omni2docx/tests/` 回归套件，把渲染引擎的"闭环"固化进仓库、可复现：
  - `run_matrix_test.py`（docx 12 例 + XML 级断言：PAGE 域/emoji 剥离/引用块楷体/嵌套 inline）、`run_matrix_multi.py`（三格式 34 例：13 例 ×HTML/PPTX + 4 专项）、`run_all.py`（CI 总入口）。
  - `fixtures/` 全部为**合成占位语料**（`generate_fixtures.py` 生成 + 手写 `edge_case.md`），与任何真实机构/个人/数据无关，可安全公开、对任意 clone 可复现；结构等价真实语料并保留断言锚点。
  - `out/` 生成物 `.gitignore`；新增 `.github/workflows/omni2docx-regression.yml`（python-docx + python-pptx，push/PR 触发）。
  - 套件实测：docx 12/12、三格式 34/34，合计 46 全 PASS；`check_skills.py --strict` 全仓 18 skill 0/0。
- 回归套件增补 **OCR 间距专项OCR 间距专项用例**（`generate_fixtures.py` 新增 `D11_OCR_SPACING` → `m11_ocr_spacing.omni.md`，`run_matrix_test.py` 加 `cjk_space_clean` / `latin_space_preserved` 两项 XML 级断言）：确定性固化 OCR 已知限制行为——CJK 逐字空格被 `clean_cjk_spaces` 清理、拉丁逐字母空格按已知限制原样保留（引擎不修）。套件现 docx 13 例、三格式 34 例；P2 真机另以一份 1990 年 USPTO 图像型专利（12 页真实扫描件）走全链路，确认真实扫描 PDF 可正常解析渲染，但该件 omni 重 OCR 干净、未触发拆字，印证限制为**源质量依赖型**（须低质量 CJK 扫描件才暴露）。
### 0.2.1 — 2026-10-11（验收闭环：HTML/PPTX 验收器 + 两处保真修复）

- 新增 `scripts/validate_html.py`：HTML 产物验收器，与 `validate_docx.py` 同口径（字符级 CJK 覆盖率 ≥99% 判 PASS，emoji 以 `--strip-emoji` 同口径从源文剥离防误报），附加目录/锚点/源页标注/溯源附录/自包含（无外链）结构检查；`--json`/`--md` 二选一，与渲染输入保持一致。
- 新增 `scripts/validate_pptx.py`：PPTX 产物验收器，**幻灯片正文 + 表格单元格 + 演讲者备注合并计入覆盖口径**（汇报版式"要点上页、正文进备注"）；附加空页/页数/表格/图像/截断检查。
- 修复 `render_pptx.py` 尾部正文静默丢失：deck 正常时，最后一段纯正文节（如免责声明）残留在 `pending_notes` 被丢弃——实测 61k 字法务研报覆盖率仅 66.86%；现追加到最后一张幻灯片备注，同源复测 99.17%（剩余 0.83% 为源文档逐页重复的页眉页脚 chrome 行，非正文）。
- 修复 `render_pptx.py` 空节标题丢失：标题下只有图片/分隔线的节（如"## 6. 图像与分隔"），标题只存 `cur_title`，被下一标题覆盖丢失；现空节标题保入备注流。
- 回归升级：`run_matrix_multi.py` 改为直接调用随包验收器（回归同时覆盖验收器本身），并新增专项用例——多源合并（3 源 + analysis）、`--md` 直出、空 markdown、纯表格，共 34 例全 PASS；docx 12 例矩阵回归无回归。
- 版本位：0.2.0 → 0.2.1（新增验收器 = minor 伴随修复，docx/HTML/PPTX 渲染口径不变）。

### 0.2.0 — 2026-10-11（多格式：展示 HTML + 汇报 PPT + 打印 PDF）

- 新增 `scripts/render_html.py`（展示）：把同一份解析结果渲染为**自包含单文件 HTML**——目录锚点跳转、源页标注（grounded）、GFM 表格/引用（楷体）/脚注尾注/溯源标注段还原，内联 CSS 按 `--profile` 制式（字体/字号/行距/首行缩进/页边距），打印样式 `@page A4`；`--pdf` 调用本机 headless 浏览器（Edge/Chrome/Chromium）导出打印件，缺浏览器时明确提示跳过、不静默失败。
- 新增 `scripts/render_pptx.py`（汇报）：标题页 / 章节页 / 要点页 / 表格页；**要点上页、正文细节进演讲者备注**（汇报语义，避免长文档被逐段平铺成上百页）；要点超 `--max-bullets`/`--max-chars` 自动续页；表格按列数降字号、超长标题自动降字号；支持 `data:image` 图像嵌入；无标题层级的文档有兜底分页；`--max-slides`（默认 80）截断并告警，提示先提炼提纲。
- 架构取舍：不重构为 block IR，采用**轻量契约**（markdown + grounding + outline + profile，各渲染器自消费），docx 引擎零改动、旧产出不受影响。
- 实测：真实语料 13 例 ×（HTML 覆盖率 + PPTX 页数/可打开）全 PASS，HTML CJK 覆盖率 100%；docx 侧 12 例矩阵回归无回归；HTML→PDF 打印件中文抽取 100%。

### 0.1.2 — 2026-10-10（大结果取数路径改正为条件句：按该 part 的存储形制分流＋选 detail 口径）

- 凭据＝双 part artifact 实据的四条读数（①侧车可按游标分块读回，条件是服务端把该 part 判为 artifact，游标绑死 part 与 offset；②`save_result` 只交 content，两种交付形制都交不出侧车；③`result_delivery_effective` 四种组合都不回显于 MCP 回执；④换 detail 只换侧车表示、正文不动）。本轮未复跑任何付费件，字节数与跳数以那份账为准，成品面只写形制不写数。
- 「解析侧能力现状」表：content／grounded 两行由「从内联回执取」改为**按该 part 的 `storage.kind` 现值分流**；`read_result` 行状态由「条件可用」改判为**按 part 分流时可用**，并写明游标绑 part 与 offset、跨 part 借游标或自造前进 offset 一律 `INVALID_RESULT_CURSOR`（`retryable:false`、`billed:false`），且 `result_delivery_effective` 不回显、不得据请求值推交付形制。
- 工作流「使用纪律」块与步骤 1 新增**大件分支**段：`inline` 直取回执、`artifact` 顺游标逐跳到 `next_cursor` 消失并与声明 digest 对拍（实测无损）；**两枚 part 各走各路不混用**，内联侧车要当场整段存住（事后无游标可补取），`save_result` 导出件两种形制都只交正文一枚、Bridge 私有缓存不是公开面本件不依赖。`result_delivery` 项把「小包两枚 part 仍内联返回」改为由该 part 自身字节数判定的表述。
- 选 detail 口径句落地（步骤 1 的 `detail` 项＋已知限制第 1 条）：要页码用 `grounded`、要坐标用 `layout`，**换 detail 不动正文**——同一件在两种表示下 content 的字节与 digest 实测逐字同值，选「页码保真」还是「版面坐标」不必重跑正文核对；同时明写本件映射引擎当前消费页级锚、layout 消费属后续阶段（不把未接上的能力写成已接）。
- `README.md`／`README.en.md` 同步三处：取数纪律段、命令注释行、能力边界两枚 bullet（双语对点，未增裸中文散文句）。
- 代码零动：`build_docx.py`／`validate_docx.py` 与夹具一字未改——本轮改的是取数路径的描述与分流条件，引擎消费什么形制由中间 JSON 决定，与取数分支无关。
- 版本位：0.1.1 → 0.1.2（取数分支与流程表述的改正＝patch，无新增能力；本件唯一版本锁在 `SKILL.md`，改后该面旧字面复算＝0，历史条目里的 0.1.1 不回改）。
- 复验（取脚本自报行）：`check_skills.py --strict` 本包 OK v0.1.2、全仓 17 skill(s), 0 error(s), 0 warning(s)；成品面逐面卫生闸 exit 0；旧句「从 parse 内联回执取」「不必也不靠这个工具」grep＝0 命中，条件句关键词（游标／以实际返回／`storage.kind`）在同段共现；同一 markdown 双跑引擎出口逐字节一致。

### 0.1.1 — 2026-10-10（取数可靠性句改写＋误喂输入的指引化）

- 取数第一性改为**只依赖 `parse` / `get_parse_status` 的内联回执**：content 与 grounding 两枚 part 随回执同进程返回；请求 artifact 形制时小包仍内联返回，一切以实际返回为准。
- `read_outline` / `read_result` 由「可用」改判为**可选续调用、不保证可得**：同一 result_id 上可返回不可重试的 `RESULT_NOT_FOUND`（同时刻落盘类调用仍可成功），无 cursor 时 `read_result` 无法起步。不可得时不重试、不报故障、不猜原因——直接由引擎从干净 markdown 重建章节层级，**outline 缺省是本件常规路径**。原「同会话即天然直接可用」「跨进程属自造假故障」两句撤除（前者把充分条件写成保证，后者把责任写死给调用方，事实都不支持）。
- 能力现状表两行状态列改为可核对形制（可用条件＋不可得时行为），不再裸判「可用」；已知限制第 2 条同改；`README.md` 与 `README.en.md` 各三处同步，与主指令不互相矛盾。
- 路径成立性本轮复跑取到：一份 7 页研报的中间件（键集 detail/grounding/markdown/source，**无 outline 字段**，正文 20,153 字节）喂引擎仍打印 `blocks=117 outline_nodes=62 toc=True segments=7 pagebreaks=6`、退码 0，校验判定 PASS——「outline 缺省仍能重建目录」是实测形制，不是兜底说辞。
- 输入护栏：`--json` 指向不可解析内容（整份 markdown 误喂、或非法字节流）不再抛裸 traceback，退码 1 并给出「整份 markdown 请改用 `--md` 直出；中间 JSON 按步骤 2 从回执组装」的可执行指引。探针三则：误喂 markdown exit=1 且 stderr 含 `--md`、不含 Traceback；形状错守卫句原样不退化；真中间件正例 exit=0。
- 版本位：0.1.0 → 0.1.1（文案与报错形制整改＝patch，无能力增减）。名述面三枚现测：displayName 23／summary 70／description 298（脚本实测，非手数；距 300 上限仅余 2 字，入债务册）。

### 0.1.0 — 2026-10-10（首发）

- 双层管线：Omni 原生 `parse`（grounded）→ 中间 JSON（markdown+grounding+outline）→ `build_docx.py` 渲染；agent markdown 产物可 `--md` 直出（免中间 JSON，不依赖解析层）。
- 映射能力：grounded 页锚点→源页分页符；官方 outline→真 Heading+可见目录（缺失时从 markdown 保守重建：中文序号 H1/指数型 H2/`###` 标题）；GFM 表格（列一致性护栏）；脚注上标+文末注释节；〔来源〕灰色小字；溯源标注段（【画面】/【说话人N 时间段】/【图说】带底纹）；base64 图像引用剥离字节留说明。
- 多源合并：`sources` 每源一章 + 总目录 + 章间分页 + 文末「证据溯源附录」（页码范围/画面时间点/说话人转写段自动回灌成表）；`analysis` 渲染为首章。
- 排版：`--profile` 五预设（gov 公文 GB/T 9704 / legal / finance / academic / default）+ 内联 JSON/.json 文件任意参数覆盖（字体/字号/行距/缩进/页边距/表样式，行距接受 `28pt`/`1.5倍` 等字符串）；标题黑色+层级字号、零 CJK 伪斜体；`--page-numbers` 页脚 PAGE 域；`--strip-emoji` 剥离装饰符；`--page-marks` 页边界源页码标注。
- 校验：`validate_docx.py` 字符级 CJK 覆盖率（≥99% PASS）+ 锚句命中 + 结构统计，与 `--strip-emoji` 同口径防误报。
- 实测：真实语料矩阵 12 例（xlsx/PDF 研报/债券书/HTML/音频/docx/PPTX/JPG OCR/千页 PDF/截断 PDF/边界×2）× 多制式，覆盖率全部 100%；端到端（原生 parse→渲染→校验）通过。已知限制见 README「能力边界」。

> CI：本目录改动由 GitHub Actions「omni2docx regression」自动跑回归矩阵（`run_all.py` 自报两组：docx 侧 13 例与三格式侧 34 例），入口与清单见 .github/workflows/omni2docx-regression.yml。
