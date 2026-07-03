import urllib.request
import json
import base64
import os
import sys

# 配置
REPO_OWNER = "yuzhaopeng-up"
REPO_NAME = "openclaw-workspace"
BRANCH = "main"  # 假设默认分支是main
BASE_PATH = "02-telecom-ai/2026-07-jiangxi-training/skills/Root-Cause-Mapper"
COMMIT_MESSAGE = "Add Root-Cause-Mapper skill for Level 5 (fault topology analysis)"

# 文件列表
files_to_upload = [
    ("SKILL.md", r"C:\Users\于兆鹏\.config\TeleAgent\skills\Root-Cause-Mapper\SKILL.md"),
    ("references/pipeline-phases.md", r"C:\Users\于兆鹏\.config\TeleAgent\skills\Root-Cause-Mapper\references\pipeline-phases.md"),
    ("references/demo-data.md", r"C:\Users\于兆鹏\.config\TeleAgent\skills\Root-Cause-Mapper\references\demo-data.md"),
    ("references/classroom-script.md", r"C:\Users\于兆鹏\.config\TeleAgent\skills\Root-Cause-Mapper\references\classroom-script.md")
]

def get_github_token():
    """尝试获取GitHub token"""
    # 尝试环境变量
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        return token
    
    # 尝试从配置文件读取
    config_paths = [
        os.path.expanduser("~/.config/gh/hosts.yml"),
        os.path.expanduser("~/.config/gh/config.yml"),
    ]
    
    for path in config_paths:
        if os.path.exists(path):
            print(f"找到配置文件: {path}")
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 简单查找token
                if 'token' in content.lower():
                    print("配置文件包含token信息，但无法自动解析")
    
    return None

def check_repo_exists(token=None):
    """检查仓库是否存在"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"
    req = urllib.request.Request(url)
    req.add_header('Accept', 'application/vnd.github.v3+json')
    req.add_header('User-Agent', 'Python')
    
    if token:
        req.add_header('Authorization', f'token {token}')
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return True, data.get('default_branch', 'main'), data.get('private', True)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False, None, None
        elif e.code == 401:
            return None, None, None  # 需要认证
        else:
            raise

def get_file_sha(path, token):
    """获取文件SHA（如果文件存在）"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{path}"
    req = urllib.request.Request(url)
    req.add_header('Accept', 'application/vnd.github.v3+json')
    req.add_header('Authorization', f'token {token}')
    req.add_header('User-Agent', 'Python')
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return data.get('sha')
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise

def upload_file(repo_path, local_path, token, branch='main'):
    """上传或更新文件到GitHub"""
    # 读取文件内容
    with open(local_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 编码为base64
    content_bytes = content.encode('utf-8')
    content_base64 = base64.b64encode(content_bytes).decode('utf-8')
    
    # 检查文件是否已存在
    sha = get_file_sha(repo_path, token)
    
    # 构建请求数据
    data = {
        'message': COMMIT_MESSAGE,
        'content': content_base64,
        'branch': branch
    }
    
    if sha:
        data['sha'] = sha
        print(f"  文件已存在，将更新 (SHA: {sha[:8]}...)")
    else:
        print(f"  文件不存在，将创建")
    
    # 发送请求
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{repo_path}"
    req = urllib.request.Request(url, method='PUT')
    req.add_header('Accept', 'application/vnd.github.v3+json')
    req.add_header('Authorization', f'token {token}')
    req.add_header('Content-Type', 'application/json')
    req.add_header('User-Agent', 'Python')
    
    req.data = json.dumps(data).encode('utf-8')
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            return True, result
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        return False, f"HTTP {e.code}: {error_body}"

def main():
    print("=" * 60)
    print("Root-Cause-Mapper Skill 同步到 GitHub")
    print("=" * 60)
    
    # 获取token
    token = get_github_token()
    
    if not token:
        print("\n未找到GitHub token。请提供以下之一：")
        print("1. 设置环境变量 GITHUB_TOKEN")
        print("2. 使用GitHub CLI登录: gh auth login")
        print("\n或者手动在GitHub网站上创建token：")
        print("https://github.com/settings/tokens")
        print("\n需要权限: repo (访问私有仓库)")
        
        # 尝试无认证访问
        print("\n尝试无认证访问仓库...")
        result = check_repo_exists()
        
        if result[0] is False:
            print("仓库不存在或无法访问")
        elif result[0] is None:
            print("仓库需要认证才能访问（私有仓库）")
        
        return 1
    
    print(f"\n找到GitHub token: {token[:10]}...")
    
    # 检查仓库
    print("\n检查仓库访问权限...")
    repo_exists, default_branch, is_private = check_repo_exists(token)
    
    if not repo_exists:
        print(f"错误: 仓库 {REPO_OWNER}/{REPO_NAME} 不存在或无法访问")
        return 1
    
    print(f"仓库存在 (私有: {is_private})")
    print(f"默认分支: {default_branch}")
    
    # 上传文件
    print(f"\n开始上传文件到路径: {BASE_PATH}")
    print("-" * 60)
    
    success_count = 0
    for repo_file, local_file in files_to_upload:
        repo_path = f"{BASE_PATH}/{repo_file}"
        print(f"\n上传: {repo_file}")
        print(f"  本地: {local_file}")
        print(f"  远程: {repo_path}")
        
        success, result = upload_file(repo_path, local_file, token, default_branch)
        
        if success:
            print(f"  状态: 成功")
            success_count += 1
        else:
            print(f"  状态: 失败")
            print(f"  错误: {result}")
    
    print("\n" + "=" * 60)
    print(f"上传完成: {success_count}/{len(files_to_upload)} 个文件成功")
    print("=" * 60)
    
    return 0 if success_count == len(files_to_upload) else 1

if __name__ == '__main__':
    sys.exit(main())
