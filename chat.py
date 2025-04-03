import os
import sys
import sublime
import sublime_plugin
import json
import subprocess
from datetime import datetime
from threading import Thread
lib_path = os.path.join(os.path.dirname(__file__), "lib")
if lib_path not in sys.path:
    sys.path.insert(0, lib_path)
from openai import OpenAI

messages = []
types = ''
record_name = ''
new_view = None


def get_time(is_name=False):
    '''获取当前时间'''
    fmt = '%Y-%m-%d %H:%M:%S'
    if is_name:
        fmt = '%Y_%m_%d__%H_%M_%S'
    return datetime.now().strftime(fmt)


class ViewCloseDetector(sublime_plugin.EventListener):
    def on_close(self, view):
        # file_name = view.file_name() or "未命名文件"

        global new_view
        if new_view:
            if new_view.id() == view.id():
                if messages:
                    if types in ['import', 'record']:
                        if record_name:
                            path = record_name
                        else:
                            path = './temp/' + get_time(True) + '.json'
                        print(path)
                        with open(path, 'w') as file:
                            data = {"data": messages}
                            json.dump(data, file)


class ChatCommand(sublime_plugin.WindowCommand):
    def run(self, view_type):
        '''主程序入口'''
        global types
        types = view_type
        parameter = sublime.load_settings('chat.sublime-settings')
        key = parameter.get('api_key')
        self.NAME = parameter.get('name')
        self.AI_NAME = parameter.get('ai_name')
        self.INTERVAL = parameter.get('interval')
        self.SHOW_LINE_NUMBER = parameter.get('show_line_number')
        self.PREFIX = parameter.get('prefix')

        self.client = OpenAI(api_key=key, base_url="https://api.deepseek.com")

        self.main()

    def main(self):
        global new_view
        new_view = self.window.new_file()  # 创建新文件（View对象）
        new_view.set_syntax_file('Packages/Text/Plain text.tmLanguage')  # 设置文件语法
        self.window.focus_view(new_view)  # 聚焦到新标签页
        new_view.set_name(self.AI_NAME)  # 设置临时文件名
        new_view.set_scratch(True)  # 标记为临时文件（关闭时提示保存）
        new_view.settings().set("line_numbers", self.SHOW_LINE_NUMBER)
        self.read_type()
        self.show_in()

    def on_input_cancel(self):
        '''取消输入时的回调函数'''
        sublime.status_message("输入已取消...")

    def on_input_done(self, user_input):
        '''
        输入框中用户按下回车后的处理
        设置文字格式
        '''
        sublime.status_message("已输入...")
        msg = self.NAME + '\t' + get_time() + ':\n' + user_input + '\n' * (self.INTERVAL + 1)
        self.window.run_command('append', {'characters': msg})
        user_input = self.PREFIX + user_input

        # answer = ''
        msg = self.AI_NAME + '\t' + get_time() + ':\n'
        self.window.run_command('append', {'characters': msg})

        messages.append({"role": "user", "content": user_input, "time": get_time()})

        def inner():
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                stream=True
            )
            sublime.status_message("正在思考...")
            ai_content = ''
            for each in response:
                content = each.choices[0].delta.content
                ai_content += content
                self.window.run_command('append', {'characters': content})

            self.window.run_command('append', {'characters': '\n' * 3})
            print('finish')
            messages.append({"role": "assistant", "content": ai_content, "time": get_time()})

            self.show_in()
        Thread(target=inner).start()

    def show_in(self):
        '''调取输入框,获取用户输入'''
        self.window.show_input_panel(
            caption="",  # 输入提示
            initial_text="",  # 默认文本
            on_done=self.on_input_done,  # 回车确认回调
            on_change=None,  # 实时输入变化回调（可选）
            on_cancel=self.on_input_cancel  # 取消输入回调（ESC键）
        )

    def read_type(self):
        global messages
        global record_name
        global types
        if types == 'temp':
            messages = []
        elif types == 'record':
            messages = []
        elif types == 'import':
            root = os.path.dirname(os.path.abspath(__file__)).replace('/', '\\') + 'temp'  # 获取当前路径
            print(root)
            command = f'powershell -Command "Add-Type -AssemblyName System.Windows.Forms; $dialog = New-Object Windows.Forms.OpenFileDialog; $dialog.InitialDirectory = \'{root}\'; $dialog.ShowDialog() | Out-Null; Write-Output $dialog.FileName"'
            print(command)
            record_name = subprocess.check_output(command, shell=True).decode().strip()
            if record_name:
                with open(record_name, 'r', encoding='utf-8') as file:
                    messages = json.load(file)['data']
                for each in messages:
                    if each['role'] == 'user':
                        msg = self.NAME + '\t' + each['time'] + ':\n' + each['content'] + '\n' * (self.INTERVAL + 1)

                    else:
                        msg = self.AI_NAME + '\t' + each['time'] + ':\n' + each['content'] + '\n' * (self.INTERVAL + 1)
                    self.window.run_command('append', {'characters': msg})
            else:
                types = 'record'

        else:
            messages = []
