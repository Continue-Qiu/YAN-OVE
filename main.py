# 从 Kivy 里把"App"这个总开关请出来，整个程序说白了就是个 App
from kivy.app import App
# 把系统自带的"路径工具"请出来，待会儿拼字体路径要用
import os
# 把"网络请求库"请出来，App 要能联网、去后端要数据
import requests
# 把"线程"请出来——联网要等网络，不能卡住界面，得丢到后台去慢慢跑
import threading
# 把 Kivy 的"闹钟"请出来，它能让某段代码"回到主线程"再执行
# （Kivy 的规矩：改界面只能主线程干，后台线程取完数据得靠它切回来）
from kivy.clock import Clock
# 请出"按钮"这个零件，底部导航、购买按钮都用它
from kivy.uix.button import Button
# 请出"标签"这个零件，用来显示文字
from kivy.uix.label import Label
# 请出"盒子布局"，能把东西横着排或竖着排
from kivy.uix.boxlayout import BoxLayout
# 请出"滚动视图"，内容多了可以上下滑
from kivy.uix.scrollview import ScrollView
# 请出"基础方块"（什么都不显示，专门用来占位、撑开空间）
from kivy.uix.widget import Widget
# 请出"屏幕管家"和"单个页面"，管家管翻页，页面就是每一屏
from kivy.uix.screenmanager import ScreenManager, Screen
# 请出"颜色""矩形""圆角矩形"：涂底色、做圆角卡片都靠它们
from kivy.graphics import Color, Rectangle, RoundedRectangle
# 请出"字体注册器"——这是让中文能正常显示的关键工具
from kivy.core.text import LabelBase
# 请出"窗口"，用来设置它的底色（控件没盖满时，露出的就是窗口底色）
from kivy.core.window import Window

# ------------------ 注册中文字体（解决乱码的关键一步）------------------
# __file__ 是当前这个 py 文件本身；下面算出它所在的文件夹（绝对路径）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 拼出项目内字体的完整路径：字体放在 fonts/simhei.ttf
FONT_PATH = os.path.join(BASE_DIR, 'fonts', 'simhei.ttf')
# 把黑体注册成 Kivy 的默认字体名 'Roboto'，这样所有控件默认都用它，中文不再乱码
LabelBase.register(name='Roboto', fn_regular=FONT_PATH)

# ================== 后端地址 ==================
# App 要连的服务器地址。现在后端跑在你自己电脑上，所以是 127.0.0.1（本机）
# ⚠️ 以后打包成 APK 装到手机上，127.0.0.1 会变成"手机自己"，就连不到电脑了
#    到时候要改成电脑的局域网 IP（形如 http://192.168.x.x:8000）或线上域名
BASE_URL = 'http://127.0.0.1:8000'

# ================== 设计令牌（照抄 LinkPass「现代通」）==================
# 整套配色都收在这一段，想换肤只改这里就行
# 主色 indigo #4f46e5（购买按钮、选中项、价格用它）
PRIMARY = (0.31, 0.27, 0.90, 1)
# 主色的浅色版 #eef2ff（公告条那种浅底用它）
PRIMARY_SOFT = (0.93, 0.95, 1.00, 1)
# 页面底色 #f5f6fa（很浅的灰）
BG = (0.96, 0.965, 0.98, 1)
# 卡片底色：白
CARD = (1, 1, 1, 1)
# 正文文字色 #1f2430（近黑）
TEXT = (0.12, 0.14, 0.19, 1)
# 次要文字色 #6b7280（灰）
MUTED = (0.42, 0.45, 0.50, 1)
# 纯白
WHITE = (1, 1, 1, 1)
# 圆角半径，跟 LinkPass 保持一致
RADIUS = 14

# 把"窗口底色"也设成 App 背景色（默认是黑色，控件没盖满时会露出难看的黑边）
Window.clearcolor = BG

# ================== 小工具函数 ==================
# 小工具：给任意盒子涂底色；radius>0 就是圆角卡片
def paint(widget, color, radius=0):
    # 在组件"画自己之前"先铺一层底
    with widget.canvas.before:
        # 选颜色
        Color(*color)
        # 想圆角就画圆角矩形，否则画普通矩形
        if radius:
            rect = RoundedRectangle(pos=widget.pos, size=widget.size, radius=[radius])
        else:
            rect = Rectangle(pos=widget.pos, size=widget.size)
    # 位置/大小一变，底板跟着变（不然缩放窗口会露馅）
    def update(*args):
        rect.pos = widget.pos
        rect.size = widget.size
    widget.bind(pos=update, size=update)

# 小工具：造一个"靠左对齐"的文字（Kivy 的 Label 默认居中，左对齐要配 text_size）
def left_label(text, color, size, bold=False):
    # 造标签，指定左对齐、垂直居中
    lab = Label(text=text, color=color, font_size=size, bold=bold, halign='left', valign='middle')
    # 让文字区域等于标签自身大小，halign 才会生效
    lab.bind(size=lambda *a, w=lab: setattr(w, 'text_size', w.size))
    # 交出去
    return lab

# 小工具：把太长的文字截短（手机屏幕窄，一行放不下就得裁掉，免得溢出卡片）
# 估宽度按"半个汉字"算：半角字符（英文字母、数字）算 1，汉字/全角符号算 2
def clip_text(text, max_units):
    # total 是已经攒了多少宽度，out 是攒出来的结果
    total = 0
    out = ''
    # 一个字一个字过
    for ch in text:
        # 编码大于 0x2E80 的基本都是中日韩文字或全角符号，按 2 个宽算
        w = 2 if ord(ch) > 0x2E80 else 1
        # 再塞这一个就超宽了 → 收工，末尾补个省略号
        if total + w > max_units:
            return out + '…'
        # 没超就收进来
        total += w
        out += ch
    # 一路都没超，原样返回
    return text

# 小工具：造一个"分区小标题"（灰色小字，比如 发现 / 偏好设置）
def section_title(text):
    # 先造一个左对齐的粗体小灰字
    lab = left_label(text, MUTED, 13, bold=True)
    # 只占一条小高度，不要被拉伸
    lab.size_hint_y = None
    # 高度定成 24
    lab.height = 24
    # 交出去
    return lab

# 小工具：去后端要一段 JSON 数据
def fetch_json(path, timeout=5):
    # 万一网络不通、或后端没开，不能让整个 App 崩掉，所以整段都包起来
    try:
        # 发 GET 请求；超时设 5 秒（等太久用户会觉得卡死了）
        resp = requests.get(BASE_URL + path, timeout=timeout)
        # 如果服务器返回的不是 200（比如 404/500），这一行会主动抛错
        resp.raise_for_status()
        # 把服务器返回的 JSON 文本变成 Python 的字典/列表交出去
        return resp.json()
    # 任何网络异常都在这里被接住（连不上、超时、格式不对……）
    except Exception as e:
        # 用一个特殊 key 把错误信息带回去，让界面能友好地提示，而不是崩掉
        return {'__error__': str(e)}

# 小工具：造一张"商品卡片"（白底圆角 + 标题 + 备注 + 价格 + 购买按钮）
# item 就是后端 /api/home 里 products 数组中的一个商品字典
def product_card(item):
    # 先把常用字段取出来，省得下面反复写 item.get(...)
    # 标题：手机一行放不下就截断（约 17 个汉字宽）
    title = clip_text(item.get('title', ''), 34)
    # 价格：后端在价格是 0（免费/议价）时会返回空串，这里统一显示成"议价"
    has_price = bool((item.get('price_text') or '').strip())
    price = item.get('price_text') if has_price else '议价'
    # 备注：后端可能给很长、还带换行，卡片上只取第一行、太长就截断（约 20 个汉字宽）
    note = clip_text((item.get('note') or '').split('\n')[0].strip(), 40)
    limited = item.get('limited', False)      # 是不是"限量商品"
    left = item.get('left', 0)                # 今天还剩多少
    sold_out = item.get('sold_out', False)    # 是不是卖完了

    # 卡片里每一块的高度：标题固定 26、价格行 34、按钮 34，备注有就 20
    # 卡片总高必须"正好等于"里面所有东西之和，否则内容会沉到底部（Kivy 的坑）
    blocks = 3 + (1 if note else 0)           # 标题 + 备注(可选) + 价格行 + 按钮
    height = 14 + 14 + 4 * (blocks - 1) + 26 + (20 if note else 0) + 34 + 34

    # 卡片是竖排盒子，固定高度、留上下内边距
    card = BoxLayout(orientation='vertical', size_hint_y=None, height=height, padding=(16, 14), spacing=4)
    # 涂成白色圆角
    paint(card, CARD, RADIUS)

    # 标题（粗体深色，固定一行高）
    t = left_label(title, TEXT, 18, bold=True)
    t.size_hint_y = None
    t.height = 26
    card.add_widget(t)

    # 备注（灰色小字）；没有备注就整块跳过
    if note:
        n = left_label(note, MUTED, 13)
        n.size_hint_y = None
        n.height = 20
        card.add_widget(n)

    # "价格 + 限量"那一行（横排）
    line = BoxLayout(size_hint_y=None, height=34)
    # 左边：有价格就用主色大字，"议价"就用灰色小字（跟网页"0 元不显价"的意思对齐）
    if has_price:
        line.add_widget(left_label(price, PRIMARY, 22, bold=True))
    else:
        line.add_widget(left_label(price, MUTED, 16))
    # 右边：限量余量 / 已售完（只有限量商品才显示）
    if limited:
        if sold_out:
            tag_text, tag_color = '今日已售完', MUTED
        else:
            tag_text, tag_color = '今日剩 %d' % left, PRIMARY
        # 靠右的小标签
        tag = Label(text=tag_text, color=tag_color, font_size=13, size_hint_x=None, width=110,
                    halign='right', valign='middle')
        # 让右对齐生效
        tag.bind(size=lambda *a, w=tag: setattr(w, 'text_size', w.size))
        # 加进这一行
        line.add_widget(tag)
    # 把价格行加进卡片
    card.add_widget(line)

    # 购买按钮（主色底白字）；售罄就变灰、并按不动
    buy = Button(text=('已售完' if sold_out else '立即购买'),
                 size_hint=(None, None), size=(110, 34),
                 background_normal='', background_down='', font_size=14,
                 background_color=(MUTED if sold_out else PRIMARY), color=WHITE,
                 disabled=sold_out)
    # 现在点它先打印一句，P2 再接真正的支付流程
    buy.bind(on_press=lambda *a, t=title: print('点了购买：', t))
    # 把按钮加进卡片
    card.add_widget(buy)

    # 交出去
    return card

# 小工具：造一张"设置卡片"（白底圆角，里面一行行设置项），照搬 LinkPass「我」页
def me_card(rows):
    # 卡片竖向排列，高度 = 每行 56 × 行数（再加 8 给上下内边距）
    card = BoxLayout(orientation='vertical', size_hint_y=None, height=56 * len(rows) + 8, padding=(0, 4))
    # 白底圆角
    paint(card, CARD, RADIUS)
    # 一行行往里加
    for title, right in rows:
        # 一行是个横排盒子
        row = BoxLayout(size_hint_y=None, height=56, padding=(18, 0))
        # 左边：设置项名字
        row.add_widget(left_label(title, TEXT, 16))
        # 右边：值 / 箭头（靠右、灰色、固定宽度）
        rlab = Label(text=right, color=MUTED, font_size=15, size_hint_x=None, width=96,
                     halign='right', valign='middle')
        # 让右对齐生效
        rlab.bind(size=lambda *a, w=rlab: setattr(w, 'text_size', w.size))
        # 把这一行加进卡片
        row.add_widget(rlab)
        # 把整行加进卡片
        card.add_widget(row)
    # 交出去
    return card

# ================== 三个页面 ==================

# 首页：公告条 + 真实商品列表（数据来自后端 /api/home）
class ScreenHome(Screen):
    # 页面刚被造出来时先跑这里
    def __init__(self, **kwargs):
        # 先让父类 Screen 做完初始化
        super().__init__(**kwargs)
        # 起名 'home'，管家靠它认这一屏
        self.name = 'home'
        # 整页涂浅灰底
        paint(self, BG)
        # 外层一个竖排盒子，四周留边距、行间距 10
        col = BoxLayout(orientation='vertical', padding=(14, 14), spacing=10)

        # 公告条：浅主色底的小长条
        notice = BoxLayout(size_hint_y=None, height=34)
        # 涂上浅主色圆角
        paint(notice, PRIMARY_SOFT, 10)
        # 公告文字（主色、居中）；用 self. 存一下，等真实公告来了再改文字
        self.notice_label = Label(text='公告 · 加载中…', color=PRIMARY, font_size=13,
                                  halign='center', valign='middle')
        # 让居中生效
        self.notice_label.bind(size=lambda *a, w=self.notice_label: setattr(w, 'text_size', w.size))
        # 把公告文字放进公告条
        notice.add_widget(self.notice_label)
        # 把公告条放进外层
        col.add_widget(notice)

        # 状态提示（加载中 / 出错 / 暂无商品），平时是空的、不占地方
        self.status_label = Label(text='', color=MUTED, font_size=13, size_hint_y=None, height=20)
        # 放进外层
        col.add_widget(self.status_label)

        # 商品列表放进滚动视图，内容多了能上下滑
        scroll = ScrollView(bar_width=0)
        # 滚动区里的竖排盒子，高度跟着内容自动长
        self.list_box = BoxLayout(orientation='vertical', spacing=12, size_hint_y=None, padding=(0, 2))
        # 让 list_box 的高度 = 它所有子项高度之和（滚动必须这么写）
        self.list_box.bind(minimum_height=self.list_box.setter('height'))
        # 把商品列表装进滚动视图
        scroll.add_widget(self.list_box)
        # 把滚动视图放进外层
        col.add_widget(scroll)

        # 最后把整个外层放进这一屏
        self.add_widget(col)

    # 去后端要首页数据（切到首页时会自动调用）
    def load_data(self):
        # 先给用户一个"正在加载"的提示
        self.set_status('正在加载…')
        # 联网会慢，丢到后台线程去跑，别卡住界面
        # daemon=True 表示：主程序关了，这条后台线程也自动跟着结束，不会留幽灵
        threading.Thread(target=self._worker, daemon=True).start()

    # 后台线程：只负责"把数据取回来"，绝不碰界面
    def _worker(self):
        # 去要首页数据（公告 + 商品 + 广告 + 联系方式……）
        data = fetch_json('/api/home')
        # 数据到手，用闹钟切回主线程再改界面
        Clock.schedule_once(lambda dt: self._apply(data))

    # 主线程：把拿到的数据铺到界面上（改界面只在这里干）
    def _apply(self, data):
        # 先清空旧的商品卡（可能是上一次留下的）
        self.list_box.clear_widgets()

        # 情况一：后端没连上（fetch_json 把错误塞在 __error__ 里）
        if '__error__' in data:
            # 给个能看懂的提示，顺便告诉用户要先启动后端
            self.set_status('连不上后端，请先启动服务后重进本页')
            # 公告也别停在"加载中"让人误会
            self.notice_label.text = '公告 · 未连接'
            # 到此结束
            return

        # 公告：后端返回的是一个"列表"（每项长这样 {"text": 文案, "link": 跳转}）
        # 把每条的文案抽出来，用 " · " 连成一句话
        marquee = data.get('marquee') or []
        # 准备一个空篮子装文案
        texts = []
        # 是列表就一条条看
        if isinstance(marquee, list):
            for m in marquee:
                # 是字典、且有文字，才收进来
                if isinstance(m, dict) and (m.get('text') or '').strip():
                    texts.append(m['text'].strip())
            # 拼成一句话
            marquee_text = ' · '.join(texts)
        # 万一后端哪天改成直接给字符串，也别崩
        else:
            marquee_text = str(marquee).strip()
        # 有公告就显示，没有就显示默认欢迎语
        self.notice_label.text = ('公告 · ' + marquee_text) if marquee_text else '公告 · 欢迎使用 YAN-OVE'

        # 商品列表
        items = data.get('products') or []
        # 情况二：后端正常但一件商品都没有
        if not items:
            self.set_status('暂无商品')
            return

        # 情况三：有数据 —— 把状态提示清掉
        self.set_status('')
        # 一件件铺成卡片
        for it in items:
            self.list_box.add_widget(product_card(it))

    # 改状态提示的小方法（统一入口，省得到处写）
    def set_status(self, text):
        self.status_label.text = text

# 发现页：分区标题 + 几张卡片（暂时还是占位内容）
class ScreenDiscover(Screen):
    # 页面刚被造出来时先跑这里
    def __init__(self, **kwargs):
        # 先让父类 Screen 做完初始化
        super().__init__(**kwargs)
        # 起名 'discover'
        self.name = 'discover'
        # 整页涂浅灰底
        paint(self, BG)
        # 外层竖排，留边距和行间距
        col = BoxLayout(orientation='vertical', padding=(14, 14), spacing=12)
        # 加一个分区小标题
        col.add_widget(section_title('发现'))
        # 加第一张探索卡片（先用商品卡片样式占位，所以传一个"像商品"的字典）
        col.add_widget(product_card({'title': '探索项一', 'price_text': '免费'}))
        # 加第二张探索卡片
        col.add_widget(product_card({'title': '探索项二', 'price_text': '免费'}))
        # 加一个会自动撑开的空方块，把上面的内容"顶"到页面顶部（否则内容会沉到底部）
        col.add_widget(Widget(size_hint_y=1))
        # 把整个外层放进这一屏
        self.add_widget(col)

# 我的页：设置分组（仿 LinkPass「我」页）
class ScreenMe(Screen):
    # 页面刚被造出来时先跑这里
    def __init__(self, **kwargs):
        # 先让父类 Screen 做完初始化
        super().__init__(**kwargs)
        # 起名 'me'
        self.name = 'me'
        # 整页涂浅灰底
        paint(self, BG)
        # 外层竖排，留边距和行间距
        col = BoxLayout(orientation='vertical', padding=(14, 14), spacing=10)
        # 第一组分标题：偏好设置
        col.add_widget(section_title('偏好设置'))
        # 第一组卡片：外观 / 联系客服
        col.add_widget(me_card([('外观', '浅色 >'), ('联系客服', '打开 >')]))
        # 第二组分标题：关于
        col.add_widget(section_title('关于'))
        # 第二组卡片：协议三连
        col.add_widget(me_card([('用户协议', '查看 >'), ('隐私政策', '查看 >'), ('免责声明', '查看 >')]))
        # 加一个会自动撑开的空方块，把上面的内容"顶"到页面顶部（否则内容会沉到底部）
        col.add_widget(Widget(size_hint_y=1))
        # 把整个外层放进这一屏
        self.add_widget(col)

# ================== APP 本体 ==================

# 我们自己的 APP 类，继承 App
class MindApp(App):
    # APP 一启动就会跑这里
    def build(self):
        # 建一个屏幕管家
        self.sm = ScreenManager()
        # 给管家也铺一层 App 背景色（兜底，防止边缘露底）
        paint(self.sm, BG)
        # 把首页加进管家
        self.sm.add_widget(ScreenHome())
        # 把发现页加进管家
        self.sm.add_widget(ScreenDiscover())
        # 把我的页加进管家
        self.sm.add_widget(ScreenMe())
        # 造底部导航栏（LinkPass 买家端是纯 tab 布局，没有顶栏，这里也一样）
        nav = BoxLayout(orientation='horizontal', size_hint_y=None, height=58)
        # 导航栏白底
        paint(nav, CARD)
        # 造"首页"按钮：背景透明只剩文字，当前页用主色
        self.btn_home = Button(text='首页', background_normal='', background_down='', background_color=(0, 0, 0, 0), color=PRIMARY, font_size=16)
        # 造"发现"按钮，默认灰色（未选中）
        self.btn_discover = Button(text='发现', background_normal='', background_down='', background_color=(0, 0, 0, 0), color=MUTED, font_size=16)
        # 造"我"按钮，默认灰色（未选中）
        self.btn_me = Button(text='我', background_normal='', background_down='', background_color=(0, 0, 0, 0), color=MUTED, font_size=16)
        # 给三个按钮分别绑上"按下要做的事"
        self.btn_home.bind(on_press=self.goto_home)
        # 同上
        self.btn_discover.bind(on_press=self.goto_discover)
        # 同上
        self.btn_me.bind(on_press=self.goto_me)
        # 把三个按钮加进导航栏
        nav.add_widget(self.btn_home)
        # 同上
        nav.add_widget(self.btn_discover)
        # 同上
        nav.add_widget(self.btn_me)
        # 记下导航顺序和按钮，切换时好统一刷高亮
        self.nav_order = ['home', 'discover', 'me']
        # 按钮列表，和上面的顺序一一对应
        self.nav_buttons = [self.btn_home, self.btn_discover, self.btn_me]
        # 整页 = 上面内容区 + 下面导航栏
        root = BoxLayout(orientation='vertical')
        # 放内容区（它会占满中间剩下的空间）
        root.add_widget(self.sm)
        # 放底部导航栏
        root.add_widget(nav)
        # 一开始停在首页（顺手把首页数据也拉了）
        self.switch_to('home')
        # 交出去，当整个 APP 的根
        return root

    # 统一切换：换页面 + 刷新导航高亮
    def switch_to(self, name):
        # 让管家切到指定那一屏
        self.sm.current = name
        # 三个导航按钮过一遍
        for key, btn in zip(self.nav_order, self.nav_buttons):
            # 是当前页就主色，不是就灰色
            btn.color = PRIMARY if key == name else MUTED
        # 每次切回首页，都顺手重新拉一次数据（方便看到最新的商品/公告）
        if name == 'home':
            self.sm.get_screen('home').load_data()

    # 按"首页"时干的事
    def goto_home(self, instance):
        # 切到首页
        self.switch_to('home')

    # 按"发现"时干的事
    def goto_discover(self, instance):
        # 切到发现页
        self.switch_to('discover')

    # 按"我"时干的事
    def goto_me(self, instance):
        # 切到我的页
        self.switch_to('me')

# 只有"被直接运行"（python main.py）时才发车；被别的文件 import 时不会自动跑，方便做测试
if __name__ == '__main__':
    # 把 APP 真正跑起来
    MindApp().run()
