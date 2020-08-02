import redis

# 普通连接
conn = redis.Redis(host="airke.top", port=6379)
with open("rid","r") as ips:
    for ip in ips.readlines():
        print(ip.strip()[0:]+"---")
        conn.sadd("rid",ip.strip()[0:])
print(conn.smembers("rid"))
# print(type(int(conn.spop("rid"))))
