#从 Kivy 里把"App"这个最核心的东西请出来。你的整个程序说白了就是个 App
from kivy.app import App
#把"按钮"这个零件请出来（uix 就是"界面"的意思）
from kivy.uix.button import Button
#给你的 APP 画个蓝图、起个名。App 是我起的，叫啥都行
class MindApp(App):
#App 一启动就执行这里，相当于"开门第一眼看到啥"
    def build(self):
        
        # 让它第一眼就显示一个写着"NewLife"的按钮
        return Button(text="NewLife!")
# 最后这行是"发车"，把 APP 真正跑起来
MindApp().run()
