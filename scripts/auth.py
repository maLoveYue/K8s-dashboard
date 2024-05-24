from kubernetes import client, config
from django.shortcuts import redirect
from dashboard.models import User
import os
import yaml
import datetime
from dateutil.tz import tzutc
#通过认证k8s集群来判断登录是否成功
def self_check_auth(auth_type, token):
    if auth_type == 'token':
        # configuration = client.Configuration()
        # configuration.host = "https://192.168.0.110:8443"  # APISERVER地址
        # ca_file = os.path.join(os.getcwd(), "ca.pem")  # K8s集群CA证书（/etc/kubernetes/pki/ca.crt）
        # configuration.ssl_ca_cert = ca_file
        # configuration.verify_ssl = True  # 启用证书验证
        # token = token  # 指定Token字符串，下面方式获取
        # configuration.api_key = {"authorization": "Bearer " + token}
        # client.Configuration.set_default(configuration)
        load_k8s(auth_type, token)
        try:
            core_api = client.CoreApi()
            core_api.get_api_versions()  # 查看k8s版本，由此验证是否有效的
            return True
        except Exception as e:
            print(e)
            return False

    elif auth_type == 'kubeconfig':
        # user_obj = User.objects.get(token=token)
        # content = user_obj.content
        # yaml_content = yaml.load(content, Loader=yaml.FullLoader)  # 将yaml文件转为json
        # config.load_kube_config_from_dict(yaml_content)
        load_k8s(auth_type, token)
        try:

            core_api = client.CoreApi()
            core_api.get_api_versions()  # 查看k8s版本，由此验证是否有效的
            return True
        except Exception as e:
            print(e)
            return False

#对视图是否登录进行验证

def self_login_auth(func):
    def inner(request):
        is_login = request.session.get('is_login', False)
        if is_login:
            return func(request)
        else:
            return redirect("login")
    return inner

# 请求资源前加载k8s认证
def load_k8s(auth_type,token):
    if auth_type == 'token':
        configuration = client.Configuration()
        configuration.host = "https://192.168.0.110:8443"  # APISERVER地址
        ca_file = os.path.join(os.getcwd(), "ca.pem")  # K8s集群CA证书（/etc/kubernetes/pki/ca.crt）
        configuration.ssl_ca_cert = ca_file
        configuration.verify_ssl = True  # 启用证书验证
        configuration.api_key = {"authorization": "Bearer " + token}
        client.Configuration.set_default(configuration)

    elif auth_type == 'kubeconfig':
        user_obj = User.objects.get(token=token)
        content = user_obj.content
        yaml_content = yaml.load(content, Loader=yaml.FullLoader)  # 将yaml文件转为json
        config.load_kube_config_from_dict(yaml_content)

# 时间格式化

def time_format(timestamp):
    time = timestamp + datetime.timedelta(hours=8)
    return datetime.date.strftime(time, '%Y-%m-%d %H:%M:%S')


