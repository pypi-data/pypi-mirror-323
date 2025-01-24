import os
import requests
from typing import Optional
from pathlib import Path
from .utils import get_cache_dir, validate_model_id
import ssl
from requests.adapters import HTTPAdapter
import urllib3

class DownloadError(Exception):
    """下载过程中的自定义异常"""
    pass

class CustomHTTPAdapter(HTTPAdapter):
    """自定义HTTP适配器，支持SSL上下文"""
    def __init__(self, ssl_context=None, *args, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(*args, **kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = urllib3.poolmanager.PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_context=self.ssl_context
        )

def get_project_id(user_name: str, project_name: str) -> int:
    """根据用户名和项目名获取项目ID"""
    base_url = "https://shangshan.mwr.cn/hub/api/v4"
    url = f"{base_url}/users/{user_name}/projects?search={project_name}"
    response = requests.get(url)
    return response.json()['id']

def snapshot_download(
    model_id: str,
    cache_dir: Optional[str] = None,
    token: Optional[str] = None,
) -> str:
    """
    从GitLab下载模型快照
    
    Args:
        model_id: 模型ID，格式为 'username/model-name'
        cache_dir: 可选，指定下载目录
        token: 可选，GitLab API token
    
    Returns:
        str: 模型文件保存的本地目录路径
    
    Raises:
        DownloadError: 当下载失败时抛出
    """
    # 验证模型ID格式
    if not validate_model_id(model_id):
        raise ValueError(f"无效的模型ID格式: {model_id}")
    
    # 设置下载目录
    if cache_dir is None:
        cache_dir = get_cache_dir()
    
    model_dir = os.path.join(cache_dir, model_id.replace('/', '_'))
    os.makedirs(model_dir, exist_ok=True)
    
    # API配置 设置成全局的配置
    api_base = "https://shangshan.mwr.cn/hub/api/v4"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        # 创建Session对象以复用连接
        session = requests.Session()
        
        # 创建并配置SSL上下文
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.load_default_certs()
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        ssl_context.options |= ssl.OP_NO_SSLv2
        ssl_context.options |= ssl.OP_NO_SSLv3
        ssl_context.options |= getattr(ssl, '_OP_LEGACY_SERVER_CONNECT', 0x00000004)
        ssl_context.set_ciphers('DEFAULT@SECLEVEL=1')
        
        # 配置session的SSL设置
        session.verify = True
        adapter = CustomHTTPAdapter(ssl_context=ssl_context, max_retries=3)
        session.mount('https://', adapter)
        session.mount('http://', adapter)
        
        # 获取项目ID
        user_name, project_name = model_id.split('/')
        # 使用session发送请求
        response = session.get(
            f"{api_base}/users/{user_name}/projects",
            params={"search": project_name},
            headers=headers
        )
        response.raise_for_status()
        project_id = response.json()[0]['id']
        
        # 获取仓库文件列表
        tree_response = session.get(
            f"{api_base}/projects/{project_id}/repository/tree",
            params={"recursive": True},
            headers=headers
        )
        tree_response.raise_for_status()
        
        # 下载所有非git文件
        for item in tree_response.json():
            if item["type"] == "blob" and not item["path"].startswith(".git"):
                file_path = os.path.join(model_dir, item["path"])
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                # 下载文件内容
                file_response = session.get(
                    f"{api_base}/projects/{project_id}/repository/files/{item['path']}/raw",
                    headers=headers
                )
                file_response.raise_for_status()
                
                with open(file_path, "wb") as f:
                    f.write(file_response.content)
        
        return model_dir
        
    except requests.exceptions.RequestException as e:
        raise DownloadError(f"下载失败: {str(e)}") 