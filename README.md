# YAN-OVE

用 **Kivy + Python** 边做边学的安卓 APP 入门练习。**界面照搬了 LinkPass「现代通」的设计语言**（同一个作者的另一套 Web 项目）。界面已全面中文化。

## 怎么跑起来
- 装依赖：`pip install kivy`
- 准备字体：把任一中文 `.ttf` 放到 `fonts/simhei.ttf`（本项目用系统黑体，未入库）
- 运行：`python main.py`
- 会在电脑上弹出一个窗口（要变成手机 APK 还得走 WSL + 打包工具，后面再说）

## 设计来源：LinkPass「现代通」
从 `E:\LinkPass\linkpass\website-project` 借来的设计：
- **纯 tab 应用式布局**：底部导航 `首页 / 发现 / 我`，**没有顶栏**（现代通买家端就是这种）
- **设计令牌**（见 main.py 顶部，换肤只改这里）：
  - 主色 indigo `#4f46e5`、浅主色 `#eef2ff`、页面底 `#f5f6fa`
  - 卡片白、正文 `#1f2430`、次要 `#6b7280`
  - 圆角 14
- **内容样式**：
  - 首页 = 公告条（仿跑马灯）+ 商品卡片（标题/价格/立即购买）
  - 我的 = 设置分组卡片（偏好设置 / 关于）

## 中文字体（已解决）
- 字体文件放 `fonts/simhei.ttf`，`main.py` 顶部用 `LabelBase.register(name='Roboto', fn_regular=FONT_PATH)` 把它**注册成全局默认字体**，所有控件自动用中文，不再乱码
- 路径用 `os.path.join(BASE_DIR, 'fonts', 'simhei.ttf')` 拼（脚本相对路径，跟当前目录无关）
- ⚠️ 字体**不入 git**（体积大 + 授权问题），换机器需自行放回 `fonts/simhei.ttf`；公开发布建议换开源字体（思源黑体 / Noto Sans SC）

## 程序结构（main.py）
- `MindApp(App)`：入口，`build()` 返回根控件（竖排：内容区 + 底部导航栏）
- `ScreenHome` / `ScreenDiscover` / `ScreenMe`：三个页面
- 小工具函数：
  - `paint(w, color, radius)`：给布局涂底色，`radius>0` 就是圆角卡片
  - `left_label` / `section_title`：左对齐文字 / 分区小标题
  - `product_card` / `me_card`：商品卡片 / 设置卡片（可复用）

## 关键概念（新手先记这几个）
- `LabelBase.register(name='Roboto', ...)`：换掉 Kivy 的默认字体（中文关键）
- `self.sm.current = '名字'`：让管家切到指定那一屏
- `RoundedRectangle(..., radius=[r])`：画圆角矩形 = 卡片
- `ScrollView` + `inner.bind(minimum_height=inner.setter('height'))`：内容多了能上下滑
- `super().__init__(**kwargs)`：子类的规矩，先让父类做完初始化

## 已知坑
- **LinkPass 原版**：`E:\LinkPass\linkpass` 是 FastAPI 项目，含 `.env`（密钥）和 `data/uploads/`（收款码），**只读参考，别提交到仓库**

## 进度
- [x] 第一个能按的按钮（已推 GitHub）
- [x] git 全流程（SSH 免令牌，分支 main）
- [x] 多页面框架骨架（ScreenManager + 多屏）
- [x] 底部导航栏（首页 / 发现 / 我 三页切换）
- [x] 界面美化：照搬 LinkPass 设计语言（indigo 主色 / 白卡片 / 圆角 / 商品卡 / 设置卡）
- [x] **中文字体**（项目内置 simhei.ttf + 全局注册，界面全中文）
- [ ] 打通数据：配服务器地址，首页拉真实商品（`GET /`、`/api/stock`）
- [ ] 支付流程 / 订单页 / 我页交互 / 跳转链接
- [ ] 打包成 APK
