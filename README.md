# YAN-OVE

用 **Kivy + Python** 边做边学的安卓 APP 入门练习。**界面照搬了 LinkPass「现代通」的设计语言**（同一个作者的另一套 Web 项目）。界面已全面中文化。

## 怎么跑起来
- 装依赖：`pip install kivy requests`（requests 是用来调后端接口的）
- 准备字体：把任一中文 `.ttf` 放到 `fonts/simhei.ttf`（本项目用系统黑体，未入库）
- **先启动后端**（首页商品数据来自它）—— 见下面一节
- 运行：`python main.py`
- 会在电脑上弹出一个窗口（要变成手机 APK 还得走 WSL + 打包工具，后面再说）

## 后端（首页真实数据来源）
- 首页**不再写死假商品**了，会去请求后端 `GET /api/home`（商品 + 公告 + 广告 + 联系方式）
- 后端项目在 `E:\LinkPass\linkpass\website-project`（FastAPI「现代通」）；该项目的 JSON 接口层就是 `app/routes/api.py`
- 启动后端：在那个目录下执行 `uvicorn app.main:app --host 127.0.0.1 --port 8000`
- App 要连的地址写在 `main.py` 顶部常量 `BASE_URL`，本地是 `http://127.0.0.1:8000`
- ⚠️ **打包成 APK 装到手机后**，`127.0.0.1` 会变成"手机自己"，就连不到电脑了 —— 要改成电脑的局域网 IP（形如 `http://192.168.x.x:8000`）或线上域名
- 后端没启动时，首页会显示「连不上后端，请先启动服务后重进本页」，**不会崩**

## 网络层怎么写（P1 打通数据）
- `fetch_json(path)`：统一发请求 + 兜底异常；失败时返回 `{'__error__': '原因'}`，界面据此给提示
- **Kivy 铁律：改界面只能在主线程**。所以用 `threading.Thread` 在后台取数据，取完再用 `Clock.schedule_once(...)` 切回主线程更新 UI
- `ScreenHome._worker()` 只管取数据、**绝不碰界面**；`ScreenHome._apply(data)` 只管把数据铺到界面
- 每次切回首页都会自动重新拉一次（`switch_to('home')` 里触发 `load_data()`）

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
  - `clip_text(text, max_units)`：文字太长就截断加省略号（手机一行放不下时用）
  - `fetch_json(path)`：去后端要 JSON，失败也不崩
  - `product_card(item)` / `me_card(rows)`：商品卡片 / 设置卡片（可复用）

## 关键概念（新手先记这几个）
- `LabelBase.register(name='Roboto', ...)`：换掉 Kivy 的默认字体（中文关键）
- `self.sm.current = '名字'`：让管家切到指定那一屏
- `RoundedRectangle(..., radius=[r])`：画圆角矩形 = 卡片
- `ScrollView` + `inner.bind(minimum_height=inner.setter('height'))`：内容多了能上下滑
- `super().__init__(**kwargs)`：子类的规矩，先让父类做完初始化

## 已知坑
- **LinkPass 原版**：`E:\LinkPass\linkpass` 是 FastAPI 项目，含 `.env`（密钥）和 `data/uploads/`（收款码），**只读参考，别提交到仓库**
- **后端 `/api/home` 的 `marquee` 是"列表"不是字符串**（每项形如 `{"text": 文案, "link": 跳转}`），直接对它 `.strip()` 会崩，要遍历取 `text` 再拼
- **商品价格 0 的显示口径**：网页首页是整行不显示价格；App 里改成显示灰色的「议价」（对齐"价格面谈 / 联系客服"的语义，也让卡片不那么空）
- **真实商品标题/备注很长**：手机上会溢出卡片，用 `clip_text` 截断（标题约 34、备注约 40 个"半角宽度单位"）

## 进度
- [x] 第一个能按的按钮（已推 GitHub）
- [x] git 全流程（SSH 免令牌，分支 main）
- [x] 多页面框架骨架（ScreenManager + 多屏）
- [x] 底部导航栏（首页 / 发现 / 我 三页切换）
- [x] 界面美化：照搬 LinkPass 设计语言（indigo 主色 / 白卡片 / 圆角 / 商品卡 / 设置卡）
- [x] **中文字体**（项目内置 simhei.ttf + 全局注册，界面全中文）
- [x] **打通数据**：首页拉真实商品（`GET /api/home`，含公告 / 限量余量 / 售罄 / 连不上提示）
- [ ] 支付流程（点「立即购买」→ 下单 / 付款）
- [ ] 商品详情页 / 订单页 / 我页交互 / 跳转链接
- [ ] 打包成 APK
