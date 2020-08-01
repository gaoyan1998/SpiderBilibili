import redis

# 普通连接
conn = redis.Redis(host="airke.top", port=6379)
with open("goodip.txt","r") as ips:
    for ip in ips.readlines():
        print(ip.strip()[0:]+"---")
        conn.sadd("ips",ip.strip()[0:])
print(conn.smembers("ips"))
