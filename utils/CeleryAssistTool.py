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


#本文件代码废弃，任何情况下均禁止调用

class BaseTask(Task):
    """
    自定义任务基类，用于统一处理错误或日志。
    """
    abstract = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print(f"Task {task_id} failed: {exc}")
        # 这里可以添加发送邮件通知或记录到数据库的逻辑
        super().on_failure(exc, task_id, args, kwargs, einfo)

class ProgressTask(BaseTask):
    """
    支持进度更新的任务基类。
    适用于文档解析、向量化等长耗时操作。
    """
    abstract = True

    def update_progress(self, current, total, status="Processing"):
        """
        更新任务进度状态
        """
        self.update_state(state='PROGRESS', meta={
            'current': current,
            'total': total,
            'status': status,
            'percent': int((current / total) * 100) if total > 0 else 0
        })

class TaskRegistry:
    """
    任务注册表，用于管理和检索系统中的异步任务。
    """
    _tasks = {}

    @classmethod
    def register(cls, task_name, task_func):
        cls._tasks[task_name] = task_func
        return task_func

    @classmethod
    def get_task(cls, task_name):
        return cls._tasks.get(task_name)

def retry_on_exception(max_retries=3, countdown=5):
    """
    生成通用的重试配置参数字典。
    用法: @celery.task(**retry_on_exception())
    """
    return {
        'bind': True,
        'max_retries': max_retries,
        'default_retry_delay': countdown,
        'autoretry_for': (Exception,),
        'retry_backoff': True  # 指数退避
    }

# 创建全局实例
celery_app = make_celery("knowledge_base_worker")

def get_task_info(task_id):
    """
    获取任务的详细信息，包括进度。
    """
    task = celery_app.AsyncResult(task_id)
    response = {
        'id': task_id,
        'state': task.state,
    }
    
    if task.state == 'PENDING':
        response.update({'status': 'Pending...'})
    elif task.state == 'PROGRESS':
        response.update(task.info)
    elif task.state == 'SUCCESS':
        response.update({
            'status': 'Completed',
            'result': task.result
        })
    elif task.state == 'FAILURE':
        response.update({
            'status': 'Failed',
            'error': str(task.info)
        })  
