import os
import json
from trailing.chua_ok_all import MultiAssetTradingBot

def main():
    # os.environ["ENV"] = env
    # os.environ["DEBUG"] = str(debug)
    with open('config.json', 'r') as f:
        config_data = json.load(f)
        
    platform_config = config_data['okx']
    feishu_webhook_url = config_data['feishu_webhook']
    monitor_interval = config_data.get("monitor_interval", 4)  # 默认值为4秒

    bot = MultiAssetTradingBot(platform_config, feishu_webhook=feishu_webhook_url, monitor_interval=monitor_interval)
    bot.monitor_total_profit()

if __name__ == "__main__":
    main()
