from django.http import JsonResponse
from django.shortcuts import render, redirect
from scripts.auth import self_check_auth, self_login_auth, load_k8s
from kubernetes import client
from dashboard.models import User
from kubernetes.client.rest import ApiException
import os
import hashlib
import random
import yaml, json

@self_login_auth
def index(request):
    return render(request, 'index.html')

#登录
def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        '''
        获取token
        验证有效性
        token入session
        返回状态码
        '''
        auth_type = request.headers.get('Auth-Type')
        if auth_type == 'token':
            token = request.POST.get('token', None)
            if self_check_auth(auth_type, token):
                request.session['is_login'] = True
                request.session['auth_type'] = 'token'
                request.session['token'] = token
                code = 0
                msg = '登录成功'
            else:
                code = 1
                msg = 'token无效！'

        elif auth_type == 'kubeconfig':
            #生成一个随机数token
            token_random = hashlib.md5(str(random.random()).encode()).hexdigest()
            file_obj = request.FILES.get('file')
            content = file_obj.read().decode('utf8')
            # 将kubeconfig认证的信息入库User表
            User.objects.create(token=token_random, auth_type=auth_type, content=content)
            if self_check_auth(auth_type, token_random):
                request.session['is_login'] = True
                request.session['auth_type'] = 'kubeconfig'
                request.session['token'] = token_random
                code = 0
                msg = '登录成功'
            else:
                code = 1
                msg = 'kubeconfig文件无效！'

            res = {'code': code, 'msg': msg}

        res = {'code': code, 'msg': msg}
        return JsonResponse(res)


#退出登录
def logout(request):
    request.session.flush()
    return redirect('login')

from django.views.decorators.clickjacking import xframe_options_exempt
@self_login_auth
@xframe_options_exempt
def ace_editor(request):
    name = request.GET.get("name", None)
    namespace = request.GET.get("namespace", None)
    resource = request.GET.get("resource", None)
    res = {"name": name, "namespace": namespace, "resource": resource }
    return render(request, 'ace-editor.html', {"data": res})

@self_login_auth
def export_resource_api(request):
    auth_type = request.session.get("auth_type")
    token = request.session.get("token")
    load_k8s(auth_type, token)
    core_api = client.CoreV1Api()  # namespace,pod,service,pv,pvc, cm, secret
    apps_api = client.AppsV1Api()  # deployment
    networking_api = client.NetworkingV1Api()  # ingress
    storage_api = client.StorageV1Api()  # storage_class
    name = request.GET.get("name", None)
    namespace = request.GET.get("namespace", None)
    resource = request.GET.get("resource", None)
    result = ""
    code = 0
    msg = ""
    if resource == 'node':
        try:
            result = core_api.read_node(name=name, _preload_content=False).read().decode('utf-8')
            result = yaml.safe_dump(json.loads(result))
        except ApiException as e:
            code = 1
            msg = e
    elif resource == 'namespace':
        try:
            result = core_api.read_namespace(name=name, _preload_content=False).read().decode('utf-8')
            result = yaml.safe_dump(json.loads(result))
        except ApiException as e:
            code = 1
            msg = e
    elif resource == 'pv':
        try:
            result = core_api.read_persistent_volume(name=name, _preload_content=False).read().decode('utf-8')
            result = yaml.safe_dump(json.loads(result))
        except ApiException as e:
            code = 1
            msg = e
    elif resource == 'deployment':
        try:
            result = apps_api.read_namespaced_deployment(name=name, namespace=namespace, _preload_content=False).read().decode('utf-8')
            print(result)
            result = yaml.safe_dump(json.loads(result))
        except ApiException as e:
            code = 1
            msg = e
    elif resource == 'statefulset':
        try:
            result = apps_api.read_namespaced_stateful_set(name=name, namespace=namespace, _preload_content=False).read().decode('utf-8')
            result = yaml.safe_dump(json.loads(result))
        except ApiException as e:
            code = 1
            msg = e
    elif resource == 'daemonset':
        try:
            result = apps_api.read_namespaced_daemon_set(name=name, namespace=namespace, _preload_content=False).read().decode('utf-8')
            result = yaml.safe_dump(json.loads(result))
        except ApiException as e:
            code = 1
            msg = e

    elif resource == 'pod':
        try:
            result = core_api.read_namespaced_pod(name=name, namespace=namespace, _preload_content=False).read().decode('utf-8')
            result = yaml.safe_dump(json.loads(result))
        except ApiException as e:
            code = 1
            msg = e
    elif resource == 'ingress':
        try:
            result = networking_api.read_namespaced_ingress(name=name, namespace=namespace,
                                                            _preload_content=False).read().decode('utf-8')
            result = yaml.safe_dump(json.loads(result))
        except ApiException as e:
            code = 1
            msg = e
    elif resource == 'service':
        try:
            result = core_api.read_namespaced_service(name=name, namespace=namespace, _preload_content=False).read().decode('utf-8')
            result = yaml.safe_dump(json.loads(result))
        except ApiException as e:
            code = 1
            msg = e

    elif resource == 'pvc':
        try:
            result =core_api.read_namespaced_persistent_volume_claim(name=name, namespace=namespace,
                                                                      _preload_content=False).read().decode('utf-8')
            result = yaml.safe_dump(json.loads(result))
        except ApiException as e:
            code = 1
            msg = e

    elif resource == 'configmap':
        try:
            result = core_api.read_namespaced_config_map(name=name, namespace=namespace, _preload_content=False).read().decode('utf-8')
            result = yaml.safe_dump(json.loads(result))
        except ApiException as e:
            code = 1
            msg = e
    elif resource == 'secret':
        try:
            result = core_api.read_namespaced_secret(name=name, namespace=namespace, pretty=True, _preload_content=False).read()
            result = yaml.safe_dump(json.loads(result))
        except ApiException as e:
            code = 1
            msg = e
    res = {"code": code, "msg": msg, "data": result}
    return JsonResponse(res)