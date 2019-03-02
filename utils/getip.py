import requests;
import json
from db.redis_db import search_url_redis

apiUrl = "https://proxy.horocn.com/api/proxies?order_id=CHAK1623100837746825&num=10&format=text&line_separator=win";


def getIP(param):
    return {
        'http': '',
        'https': '',
    }


def getIPWithoutLogin(param):
    return get_proxies()
    return {
        'http': '',
        'https': '',
    }

def get_proxies():
    ip = get_the_ip()
    proxies = {
        "http": 'http://' + ip,
        "https": 'https://' + ip,
    }
    return proxies

def get_the_ip():
    ips = search_url_redis.get("proxies_ips")
    try:
        ips = json.loads(ips)
    except:
        ips = []

    ip_proxies_clock = search_url_redis.get("ip_proxies_clock")
    if not ip_proxies_clock:
        new_ips = requests.get(apiUrl).content.decode()
        new_ips = str(new_ips).split("\n")
        assert len(new_ips) > 2, "error"
        ips = new_ips
        search_url_redis.set("ip_proxies_clock", 1, 10)
    ip = ips.pop(0)
    ips.append(ip)
    search_url_redis.setex("proxies_ips", json.dumps(ips), 10)
    ip = ip.replace('\r', '')
    return ip
