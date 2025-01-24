import psutil

def get_pid_and_process_name_by_port(port):
    for conn in psutil.net_connections(kind='inet'):
        if conn.laddr.port == port:
            pid = conn.pid
            process = psutil.Process(pid)
            process_name = process.name()
            return pid, process_name

    return None, None

# 指定要查找的端口号
target_port = 52251

# 查找指定端口对应的 PID 和进程名称
pid, process_name = get_pid_and_process_name_by_port(target_port)

if pid is not None:
    print(f"Port {target_port} is being used by process with PID {pid} and name {process_name}")
else:
    print(f"No process found using port {target_port}")
