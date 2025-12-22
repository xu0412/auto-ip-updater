import requests
import os

# --- 配置 ---
# IP来源URL (它返回的是纯文本)
SOURCE_URL = "https://ip.164746.xyz/ipTop10.html"
# 输出文件名
OUTPUT_FILE = "ip_list.txt"
# 默认端口
DEFAULT_PORT = "443"

def get_ips_from_url(url):
    """从返回纯文本的URL中直接抓取IP列表"""
    try:
        # 添加一个Headers，模拟浏览器访问，更稳定
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # ！！！这里是关键改动！！！
        # 直接对返回的文本进行分割和处理
        raw_text = response.text
        
        # 增加一个简单的检查，防止网站未来又变回HTML
        if '<html' in raw_text.lower():
             print("⚠️ 警告：网站似乎返回了HTML而不是纯文本，可能需要再次检查脚本。")
             return []
        
        # 按逗号分割，并去除每个IP前后的空白
        ip_list = [ip.strip() for ip in raw_text.split(',') if ip.strip()]
        
        print(f"✅ 成功从 {url} 获取到 {len(ip_list)} 个IP。")
        return ip_list
    except requests.RequestException as e:
        print(f"❌ 获取IP源失败: {e}")
        return []
    except Exception as e:
        print(f"❌ 处理文本时出错: {e}")
        return []

# get_country_code 和 main 函数保持不变，无需修改
def get_country_code(ip):
    """查询单个IP的国家代码"""
    try:
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
    
    raw_ips = get_ips_from_url(SOURCE_URL)
    if not raw_ips:
        print("❌ 未获取到任何IP，任务终止。")
        return

    enriched_ips = []
    for ip in raw_ips:
        country = get_country_code(ip)
        if country:
            enriched_ips.append(f"{ip}:{DEFAULT_PORT}#{country}")
    
    if not enriched_ips:
        print("❌ 没有成功的查询结果，任务终止。")
        return

    enriched_ips.sort()
    file_path = os.path.join(os.getcwd(), OUTPUT_FILE)
    with open(file_path, 'w', encoding='utf-8') as f:
        for ip_line in enriched_ips:
            f.write(ip_line + '\n')
            
    print(f"✅ 成功更新文件 {OUTPUT_FILE}，共写入 {len(enriched_ips)} 条记录。")
    print("--- 每日IP更新任务完成 ---")

if __name__ == "__main__":
    main()

