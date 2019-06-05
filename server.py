# -*- coding=utf-8 -*-
import socket
import threading
import queue
from http import HttpRequest


# 每个任务线程
class WorkThread(threading.Thread):
    def __init__(self, work_queue):
        super().__init__()
        self.work_queue = work_queue
        self.daemon = True

    def run(self):
        while True:
            func, args = self.work_queue.get()
            func(*args)
            self.work_queue.task_done()


# 线程池
class ThreadPoolManger:
    def __init__(self, thread_number):
        self.thread_number = thread_number
        self.work_queue = queue.Queue()
        for i in range(self.thread_number):  # 生成一些线程来执行任务
            thread = WorkThread(self.work_queue)
            thread.start()

    def add_work(self, func, *args):
        self.work_queue.put((func, args))


def tcp_link(sock, addr):
    # 获取到客户端发来的请求体
    request = sock.recv(1024).decode('utf-8')
    http_req = HttpRequest()
    http_req.pass_request(request)
    sock.send((http_req.response_line + http_req.get_response_head() + "\r\n").encode('utf-8'))
    if isinstance(http_req.response_body, bytes):
        sock.send(http_req.response_body)
    else:
        sock.send(http_req.response_body.encode('utf-8'))
    sock.close()


def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 9999))
    s.listen(10)
    thread_pool = ThreadPoolManger(5)
    print('服务启动成功 http://%s:%d' % ('127.0.0.1', 9999))
    while True:
        sock, addr = s.accept()
        thread_pool.add_work(tcp_link, *(sock, addr))


if __name__ == '__main__':
    start_server()
    pass
