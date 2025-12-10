from celery import Celery, Task
import os



def make_celery(app_name=__name__):
    """
    创建一个配置好的 Celery 实例。
    通常用于 Flask 或其他框架集成。
    """
    # 从环境变量获取 Redis 或 RabbitMQ 地址，默认为本地 Redis
    broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

    celery = Celery(
        app_name,
        broker=broker_url,
        backend=result_backend
    )

    # 默认配置更新
    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='Asia/Shanghai',
        enable_utc=True,
    )

    return celery