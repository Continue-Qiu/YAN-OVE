# 从 Kivy 里把"App"这个总开关请出来，整个程序说白了就是个 App
from kivy.app import App
# 把系统自带的"路径工具"请出来，待会儿拼字体路径要用
import os
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

# 小工具：造一张"商品卡片"（白底圆角 + 标题 + 价格 + 购买按钮）
def product_card(title, price):
    # 卡片是竖排盒子，固定高度、留上下内边距
    card = BoxLayout(orientation='vertical', size_hint_y=None, height=150, padding=(16, 14), spacing=6)
    # 涂成白色圆角
    paint(card, CARD, RADIUS)
    # 加标题（粗体深色）
    card.add_widget(left_label(title, TEXT, 18, bold=True))
    # 加价格（主色、更大更粗）
    card.add_widget(left_label(price, PRIMARY, 22, bold=True))
    # 加购买按钮（主色底白字、固定大小）
    buy = Button(text='立即购买', size_hint=(None, None), size=(110, 34),
                 background_normal='', background_down='', background_color=PRIMARY, color=WHITE, font_size=14)
    # 把按钮放进卡片
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

# 首页：公告条 + 商品卡片列表
class ScreenHome(Screen):
    # 页面刚被造出来时先跑这里
    def __init__(self, **kwargs):
        # 先让父类 Screen 做完初始化
        super().__init__(**kwargs)
        # 起名 'home'，管家靠它认这一屏
        self.name = 'home'
        # 整页涂浅灰底
        paint(self, BG)
        # 外层一个竖排盒子，四周留边距、行间距 12
        col = BoxLayout(orientation='vertical', padding=(14, 14), spacing=12)
        # 公告条：浅主色底的小长条（仿 LinkPass 顶部跑马灯，先用静态文字）
        notice = BoxLayout(size_hint_y=None, height=34)
        # 涂上浅主色圆角
        paint(notice, PRIMARY_SOFT, 10)
        # 公告文字（主色、居中）
        nlab = Label(text='公告 · 欢迎使用 YAN-OVE', color=PRIMARY, font_size=13,
                     halign='center', valign='middle')
        # 让居中生效
        nlab.bind(size=lambda *a, w=nlab: setattr(w, 'text_size', w.size))
        # 把公告文字放进公告条
        notice.add_widget(nlab)
        # 把公告条放进外层
        col.add_widget(notice)
        # 商品列表放进滚动视图，内容多了能上下滑
        scroll = ScrollView(bar_width=0)
        # 滚动区里的竖排盒子，高度跟着内容自动长
        inner = BoxLayout(orientation='vertical', spacing=12, size_hint_y=None)
        # 让 inner 的高度 = 它所有子项高度之和（滚动必须这么写）
        inner.bind(minimum_height=inner.setter('height'))
        # 摆第一张商品卡片
        inner.add_widget(product_card('商品 A', '￥ 10.00'))
        # 摆第二张商品卡片
        inner.add_widget(product_card('商品 B', '￥ 25.00'))
        # 摆第三张商品卡片
        inner.add_widget(product_card('商品 C', '￥ 8.80'))
        # 把商品列表装进滚动视图
        scroll.add_widget(inner)
        # 把滚动视图放进外层
        col.add_widget(scroll)
        # 最后把整个外层放进这一屏
        self.add_widget(col)

# 发现页：分区标题 + 几张卡片
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
        # 加第一张探索卡片（先用商品卡片样式占位）
        col.add_widget(product_card('探索项一', '免费'))
        # 加第二张探索卡片
        col.add_widget(product_card('探索项二', '免费'))
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
        # 一开始停在首页
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
