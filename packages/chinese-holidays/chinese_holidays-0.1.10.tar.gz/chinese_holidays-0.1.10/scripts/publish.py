from dotenv import load_dotenv, find_dotenv
import os
import subprocess
import shutil
import sys
import re
from pathlib import Path

load_dotenv(find_dotenv(),verbose=True,override=True)

def check_command_exists(command):
    """检查命令是否存在"""
    try:
        subprocess.run([command.split()[0], '--version'], capture_output=True)
        return True
    except FileNotFoundError:
        return False

def run_command(command):
    try:
        process = subprocess.Popen(command, shell=True)
        process.wait()
        if process.returncode != 0:
            raise Exception(f"命令执行失败: {command}")
    except Exception as e:
        print(f"执行命令时出错: {e}")
        sys.exit(1)

def update_version(version_type='patch'):
    """更新版本号
    version_type: major（主版本）, minor（次版本）, patch（补丁版本）
    """
    pyproject_path = Path('pyproject.toml')
    content = pyproject_path.read_text(encoding='utf-8')
    
    # 查找当前版本号
    version_match = re.search(r'version\s*=\s*"(\d+)\.(\d+)\.(\d+)"', content)
    if not version_match:
        raise Exception("无法在 pyproject.toml 中找到版本号")
    
    major, minor, patch = map(int, version_match.groups())
    
    # 根据版本类型更新版本号
    if version_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif version_type == 'minor':
        minor += 1
        patch = 0
    else:  # patch
        patch += 1
    
    new_version = f'{major}.{minor}.{patch}'
    
    # 更新 pyproject.toml 中的版本号
    new_content = re.sub(
        r'(version\s*=\s*")\d+\.\d+\.\d+(")',
        rf'\g<1>{new_version}\g<2>',
        content
    )
    pyproject_path.write_text(new_content, encoding='utf-8')

    # 更新 server.py 中的版本号
    server_path = Path('src/chinese_holidays/server.py')
    server_content = server_path.read_text(encoding='utf-8')
    new_server_content = re.sub(
        r'(server_version=")[\d\.]+(")',
        rf'\g<1>{new_version}\g<2>',
        server_content
    )
    server_path.write_text(new_server_content, encoding='utf-8')

    return new_version

def main():
    # 检查是否安装了 uv
    if check_command_exists('uv'):
        # 获取版本类型参数
        version_type = 'patch'  # 默认更新补丁版本
        if len(sys.argv) > 1:
            version_type = sys.argv[1]
            if version_type not in ['major', 'minor', 'patch']:
                print("无效的版本类型。请使用 'major', 'minor' 或 'patch'")
                sys.exit(1)
        
        # 更新版本号
        new_version = update_version(version_type)
        print(f"版本已更新至: {new_version}")
        # 清理之前的构建文件
        if os.path.exists("dist"):
            shutil.rmtree("dist")
        # 同步依赖
        run_command("uv sync")

        # 添加所有文件到 git
        run_command("git add .")

        # 检查是否有暂存的更改
        process = subprocess.Popen("git status --porcelain", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, _ = process.communicate()
        if stdout:
            # 提交到 git
            run_command("git commit -m 'publish'")
        else:
            print("没有暂存的更改，跳过 git commit 步骤")

        # 构建包
        run_command("uv build")

        # 上传到 PyPI
        run_command(f"uv publish --username {os.getenv('username')} --password {os.getenv('password')}")
    else:
        print("未检测到 uv，请先安装 uv")
        sys.exit(1)

if __name__ == "__main__":
    """
    python scripts/publish.py          # 升级补丁版本 (0.1.9 -> 0.1.10)
    python scripts/publish.py minor    # 升级次版本 (0.1.9 -> 0.2.0)
    python scripts/publish.py major    # 升级主版本 (0.1.9 -> 1.0.0)
    """
    main()
