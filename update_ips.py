import requests
from bs4 import BeautifulSoup
import os

# --- 配置 ---
# IP来源URL
SOURCE_URL = "https://ip.164746.xyz/ipTop10.html" 
# 输出文件名
OUTPUT_FILE = "ip_list.txt" 
# 默认端口
DEFAULT_PORT = "443"

def get_ips_from_url(url):
    """从指定URL抓取IP地址列表"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status() # 如果请求失败则抛出异常
        
        soup = BeautifulSoup(response.text, 'html.parser')
        # 根据页面结构，IP在 class="ip" 的 <td> 标签内
        ip_elements = soup.find_all('td', class_='ip')
        
        ips = [ip.get_text().strip() for ip in ip_elements]
        print(f"✅ 成功从 {url} 抓取到 {len(ips)} 个IP。")
        return ips
    except requests.RequestException as e:
        print(f"❌ 获取IP源失败: {e}")
        return []
    except Exception as e:
        print(f"❌ 解析页面时出错: {e}")
        return []

def get_country_code(ip):
    """查询单个IP的国家代码"""
    try:
        # 使用免费的 ip-api.com 接口
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
        response.raise_for_status()
        data = response.json()
        if data['status'] == 'success':
            return data['countryCode']
        else:
            print(f"⚠️ 查询 {ip} 国家代码失败: {data.get('message', '未知原因')}")
            return None
    except requests.RequestException:
        print(f"⚠️ 网络请求失败，无法查询 {ip} 的国家代码。")
        return None

def main():
    """主函数"""
    print("--- 开始每日IP更新任务 ---")
    
    # 1. 获取原始IP列表
    raw_ips = get_ips_from_url(SOURCE_URL)
    if not raw_ips:
        print("❌ 未获取到任何IP，任务终止。")
        return

    # 2. 为每个IP查询国家代码并格式化
    enriched_ips = []
    for ip in raw_ips:
        country = get_country_code(ip)
        if country:
            # 按要求格式化: IP:端口#国家
            enriched_ips.append(f"{ip}:{DEFAULT_PORT}#{country}")
        # 可以添加一个小的延时以避免API请求过于频繁
        # time.sleep(0.2) 
    
    if not enriched_ips:
        print("❌ 没有任何成功的IP查询结果，任务终止。")
        return

    # 3. 将结果写入文件 (按字母顺序排序，便于后续版本控制)
    enriched_ips.sort()
    file_path = os.path.join(os.getcwd(), OUTPUT_FILE)
    with open(file_path, 'w', encoding='utf-8') as f:
        for ip_line in enriched_ips:
            f.write(ip_line + '\n')
            
    print(f"✅ 成功更新文件 {OUTPUT_FILE}，共写入 {len(enriched_ips)} 条记录。")
    print("--- 每日IP更新任务完成 ---")

if __name__ == "__main__":
    main()

