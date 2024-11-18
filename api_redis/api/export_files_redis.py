import os
import json
import redis
from redis import Redis
from dotenv import load_dotenv

load_dotenv()
redis_host = os.getenv("REDIS_HOST")
redis_port = os.getenv("REDIS_PORT")
redis_password = os.getenv("REDIS_PASSWORD")


class RedisClient:
    def __init__(self, host: str, port: int, password: str):
        self.client = redis.Redis(host=host, port=port, password=password)

    def get_client(self) -> Redis:
        return self.client

    def check_connection(self) -> bool:
        try:
            return self.client.ping()
        except redis.ConnectionError:
            return False


redis_client = RedisClient(
    host=redis_host, port=int(redis_port), password=redis_password
).get_client()


def export_redis_data_to_file(file_path):
    """Exporta todos os dados do Redis para um arquivo JSON com especificações detalhadas."""
    all_data = {}
    keys = redis_client.keys('*')

    for key in keys:
        key_str = key.decode('utf-8')
        key_type = redis_client.type(key).decode('utf-8')

        if key_type == 'string':
            value = redis_client.get(key).decode('utf-8')
            all_data[key_str] = {"type": key_type, "value": value}
        elif key_type == 'hash':
            value = {
                field.decode('utf-8'): val.decode('utf-8')
                for field, val in redis_client.hgetall(key).items()
            }
            all_data[key_str] = {"type": key_type, "fields": value}
        elif key_type == 'list':
            value = [item.decode('utf-8')
                     for item in redis_client.lrange(key, 0, -1)]
            all_data[key_str] = {"type": key_type, "values": value}
        elif key_type == 'set':
            value = [item.decode('utf-8')
                     for item in redis_client.smembers(key)]
            all_data[key_str] = {"type": key_type, "values": value}
        elif key_type == 'zset':
            value = [
                {"member": item.decode('utf-8'), "score": score}
                for item, score in redis_client.zscan_iter(key)
            ]
            all_data[key_str] = {"type": key_type, "members": value}
        else:
            all_data[key_str] = {"type": key_type, "value": "Unsupported type"}

    with open(file_path, 'w') as file:
        json.dump(all_data, file, indent=4, ensure_ascii=False)

    print(f"Dados exportados para o arquivo: {file_path}")


export_redis_data_to_file(
    '/Users/annakarolinymatias/Documents/repositorios/dataengineer/api_redis/database/redis_export.json')
