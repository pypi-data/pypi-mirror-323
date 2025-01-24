from scapy.all import sniff, IP, TCP

def extract_application_info(packet):
    if TCP in packet and IP in packet:
        ip_src = packet[IP].src
        ip_dst = packet[IP].dst
        sport = packet[TCP].sport
        dport = packet[TCP].dport

        # 提取 TCP 数据包的有效载荷
        payload = str(packet[TCP].payload)

        # 在这里可以添加更复杂的逻辑来解析应用信息
        # 以下示例简单地打印有效载荷
        if "192.168" not in ip_dst:
            print(f"[*] Captured TCP packet from {ip_src}:{sport} to {ip_dst}:{dport}")
            print("[*] Payload:")
            print(payload)
            print("=" * 50)

# 监听本地 TCP 流量并提取应用信息
sniff(prn=extract_application_info, store=0)
