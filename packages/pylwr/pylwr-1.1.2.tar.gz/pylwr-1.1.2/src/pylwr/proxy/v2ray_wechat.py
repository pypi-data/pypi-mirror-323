import subprocess
import os

def start_v2ray(config_file):
    v2ray_path = 'src/pylwr/proxy/v2ray/v2ray'  # 相对路径，假设在同一目录下
    v2ray_path = os.path.abspath(v2ray_path)  # 获取绝对路径
    config_file = os.path.abspath(config_file)
    command = [v2ray_path, 'run', '-config=' + config_file]

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    config_file = 'src/pylwr/proxy/wechat.json'  # 相对路径，假设在同一目录下
    start_v2ray(config_file)