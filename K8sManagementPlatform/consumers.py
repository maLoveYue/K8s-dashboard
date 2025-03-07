from channels.generic.websocket import WebsocketConsumer
from kubernetes.stream import stream
from threading import Thread
from kubernetes import client
from scripts import auth




# 多线程
class K8sStreamThread(Thread):
    def __init__(self, websocket, container_stream):
        Thread.__init__(self)
        self.websocket = websocket
        self.stream = container_stream

    def run(self):
        while self.stream.is_open():
            # 读取标准输出
            if self.stream.peek_stdout():
                stdout = self.stream.read_stdout()
                self.websocket.send(stdout)
            # 读取错误输出
            if self.stream.peek_stderr():
                stderr = self.stream.read_stderr()
                self.websocket.send(stderr)
        else:
            self.websocket.close()

# 继承WebsocketConsumer 类，并修改下面几个方法，主要连接到容器
class StreamConsumer(WebsocketConsumer):

    def connect(self):
        # self.scope 请求头信息
        self.namespace = self.scope["url_route"]["kwargs"]["namespace"]
        self.pod_name = self.scope["url_route"]["kwargs"]["pod_name"]
        self.container = self.scope["url_route"]["kwargs"]["container"]

        k8s_auth = self.scope["query_string"].decode()  # b'auth_type=kubeconfig&token=7402e616e80cc5d9debe66f31b7a8ed6'
        print(k8s_auth)
        auth_type = k8s_auth.split('&')[0].split('=')[1]
        token = k8s_auth.split('&')[1].split('=')[1]

        auth.load_k8s(auth_type, token)
        core_api = client.CoreV1Api()

        exec_command = [
            "/bin/sh",
            "-c",
            'TERM=xterm-256color; export TERM; [ -x /bin/bash ] '
            '&& ([ -x /usr/bin/script ] '
            '&& /usr/bin/script -q -c "/bin/bash" /dev/null || exec /bin/bash) '
            '|| exec /bin/sh']
        try:
            self.conn_stream = stream(core_api.connect_get_namespaced_pod_exec,
                                 name=self.pod_name,
                                 namespace=self.namespace,
                                 command=exec_command,
                                 container=self.container,
                                 stderr=True, stdin=True,
                                 stdout=True, tty=True,
                                 preload_content=False)
            kube_stream = K8sStreamThread(self, self.conn_stream)
            kube_stream.start()
        except Exception as e:
            print(e)
            status = getattr(e, "status")
            if status == 403:
                msg = "你没有进入容器终端权限！"
            else:
                msg = "连接容器错误，可能是传递的参数有问题！"
            print(msg)

        self.accept()

    def disconnect(self, close_code):
        self.conn_stream.write_stdin('exit\r')

    def receive(self, text_data):
        self.conn_stream.write_stdin(text_data)