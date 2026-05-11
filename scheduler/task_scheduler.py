"""
智能任务调度系统 - 自动化运营调度
"""
import asyncio
import json
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import random


class TaskPriority(Enum):
    """任务优先级"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ScheduledTask:
    """计划任务"""
    task_id: str
    task_type: str
    priority: TaskPriority
    scheduled_time: datetime
    parameters: Dict
    status: TaskStatus = TaskStatus.PENDING
    created_at: str = None
    completed_at: Optional[str] = None
    result: Optional[Dict] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


class IntelligentScheduler:
    """
    智能任务调度器
    
    功能：
    - 智能任务调度
    - 优先级管理
    - 自动重试机制
    - 依赖管理
    - 资源优化
    """
    
    def __init__(self, data_dir: str = "data/scheduler"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 任务队列
        self.task_queue: List[ScheduledTask] = []
        
        # 任务历史
        self.task_history: List[ScheduledTask] = []
        
        # 任务处理器映射
        self.task_handlers: Dict[str, Callable] = {}
        
        # 运行状态
        self.is_running = False
        self.current_task: Optional[ScheduledTask] = None
        
        # 调度配置
        self.config = {
            "max_concurrent_tasks": 1,  # 小红书操作需要串行
            "default_retry_delay": 300,  # 5分钟
            "max_daily_tasks": 50,
            "peak_hours": [7, 8, 12, 13, 18, 19, 20, 21, 22],
        }
        
        # 加载历史任务
        self._load_tasks()
    
    def register_handler(self, task_type: str, handler: Callable):
        """注册任务处理器"""
        self.task_handlers[task_type] = handler
        print(f"✅ 注册任务处理器: {task_type}")
    
    def schedule_task(
        self,
        task_type: str,
        parameters: Dict,
        priority: TaskPriority = TaskPriority.MEDIUM,
        scheduled_time: Optional[datetime] = None,
        max_retries: int = 3
    ) -> ScheduledTask:
        """
        调度任务
        
        Args:
            task_type: 任务类型
            parameters: 任务参数
            priority: 优先级
            scheduled_time: 计划执行时间
            max_retries: 最大重试次数
        """
        task_id = f"{task_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if scheduled_time is None:
            scheduled_time = datetime.now()
        
        task = ScheduledTask(
            task_id=task_id,
            task_type=task_type,
            priority=priority,
            scheduled_time=scheduled_time,
            parameters=parameters,
            max_retries=max_retries
        )
        
        self.task_queue.append(task)
        self._sort_queue()
        
        print(f"📅 任务已调度: {task_id} (优先级: {priority.name})")
        
        return task
    
    def schedule_daily_routine(
        self,
        routine_config: Dict
    ) -> List[ScheduledTask]:
        """
        调度每日例行任务
        
        Args:
            routine_config: 例行任务配置
                {
                    "content_publish": {"count": 2, "themes": [...]},
                    "interaction": {"keywords": [...], "count_per_keyword": 5},
                    "analytics": {"enabled": True},
                    "feed_browsing": {"duration_minutes": 30}
                }
        """
        tasks = []
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 1. 内容发布任务
        if "content_publish" in routine_config:
            pub_config = routine_config["content_publish"]
            count = pub_config.get("count", 1)
            themes = pub_config.get("themes", ["lifestyle"])
            
            for i in range(count):
                # 分散在一天中的最佳时段
                hour = random.choice(self.config["peak_hours"])
                scheduled_time = today + timedelta(hours=hour, minutes=random.randint(0, 59))
                
                task = self.schedule_task(
                    task_type="publish_content",
                    parameters={
                        "theme": random.choice(themes),
                        "auto_generate": True
                    },
                    priority=TaskPriority.HIGH,
                    scheduled_time=scheduled_time
                )
                tasks.append(task)
        
        # 2. 互动任务
        if "interaction" in routine_config:
            int_config = routine_config["interaction"]
            keywords = int_config.get("keywords", [])
            count_per = int_config.get("count_per_keyword", 5)
            
            for keyword in keywords:
                scheduled_time = today + timedelta(
                    hours=random.randint(9, 21),
                    minutes=random.randint(0, 59)
                )
                
                task = self.schedule_task(
                    task_type="interact_by_keyword",
                    parameters={
                        "keyword": keyword,
                        "max_notes": count_per
                    },
                    priority=TaskPriority.MEDIUM,
                    scheduled_time=scheduled_time
                )
                tasks.append(task)
        
        # 3. 数据分析任务
        if routine_config.get("analytics", {}).get("enabled", False):
            task = self.schedule_task(
                task_type="collect_analytics",
                parameters={},
                priority=TaskPriority.LOW,
                scheduled_time=today + timedelta(hours=23, minutes=30)
            )
            tasks.append(task)
        
        # 4. 推荐流浏览
        if "feed_browsing" in routine_config:
            fb_config = routine_config["feed_browsing"]
            duration = fb_config.get("duration_minutes", 30)
            
            task = self.schedule_task(
                task_type="feed_browsing",
                parameters={"duration_minutes": duration},
                priority=TaskPriority.BACKGROUND,
                scheduled_time=today + timedelta(hours=15, minutes=0)
            )
            tasks.append(task)
        
        print(f"📅 已调度 {len(tasks)} 个每日例行任务")
        return tasks
    
    async def start(self):
        """启动调度器"""
        if self.is_running:
            print("⚠️ 调度器已在运行")
            return
        
        self.is_running = True
        print("🚀 智能调度器已启动")
        
        while self.is_running:
            try:
                await self._process_next_task()
                await asyncio.sleep(1)  # 检查间隔
            except Exception as e:
                print(f"❌ 调度器错误: {e}")
                await asyncio.sleep(5)
    
    def stop(self):
        """停止调度器"""
        self.is_running = False
        print("🛑 智能调度器已停止")
    
    async def _process_next_task(self):
        """处理下一个任务"""
        if not self.task_queue:
            return
        
        # 获取当前时间
        now = datetime.now()
        
        # 找到可以执行的任务
        executable_task = None
        for task in self.task_queue:
            if task.status == TaskStatus.PENDING and task.scheduled_time <= now:
                executable_task = task
                break
        
        if not executable_task:
            return
        
        # 从队列中移除
        self.task_queue.remove(executable_task)
        self.current_task = executable_task
        
        # 执行任务
        await self._execute_task(executable_task)
        
        self.current_task = None
    
    async def _execute_task(self, task: ScheduledTask):
        """执行单个任务"""
        print(f"▶️ 执行任务: {task.task_id}")
        
        task.status = TaskStatus.RUNNING
        
        # 获取任务处理器
        handler = self.task_handlers.get(task.task_type)
        
        if not handler:
            print(f"❌ 未找到任务处理器: {task.task_type}")
            task.status = TaskStatus.FAILED
            task.result = {"error": "Handler not found"}
            self.task_history.append(task)
            return
        
        try:
            # 执行任务
            result = await handler(task.parameters)
            
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now().isoformat()
            task.result = result
            
            print(f"✅ 任务完成: {task.task_id}")
            
        except Exception as e:
            print(f"❌ 任务失败: {task.task_id} - {e}")
            
            task.retry_count += 1
            
            if task.retry_count < task.max_retries:
                # 重新调度
                task.status = TaskStatus.PENDING
                task.scheduled_time = datetime.now() + timedelta(
                    seconds=self.config["default_retry_delay"]
                )
                self.task_queue.append(task)
                self._sort_queue()
                print(f"🔄 任务重试: {task.task_id} (第{task.retry_count}次)")
            else:
                task.status = TaskStatus.FAILED
                task.result = {"error": str(e)}
        
        # 保存到历史
        if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            self.task_history.append(task)
            self._save_tasks()
    
    def _sort_queue(self):
        """对任务队列排序"""
        self.task_queue.sort(key=lambda t: (
            t.priority.value,
            t.scheduled_time
        ))
    
    def get_queue_status(self) -> Dict:
        """获取队列状态"""
        return {
            "pending": len([t for t in self.task_queue if t.status == TaskStatus.PENDING]),
            "running": 1 if self.current_task else 0,
            "completed_today": len([
                t for t in self.task_history
                if t.status == TaskStatus.COMPLETED
                and datetime.fromisoformat(t.completed_at).date() == datetime.now().date()
            ]),
            "failed_today": len([
                t for t in self.task_history
                if t.status == TaskStatus.FAILED
                and datetime.fromisoformat(t.created_at).date() == datetime.now().date()
            ])
        }
    
    def generate_schedule_report(self) -> str:
        """生成调度报告"""
        status = self.get_queue_status()
        
        # 统计任务类型分布
        task_type_counts = {}
        for task in self.task_history:
            task_type_counts[task.task_type] = task_type_counts.get(task.task_type, 0) + 1
        
        report = f"""
📅 智能调度系统报告
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

当前状态:
  - 待执行: {status['pending']}
  - 运行中: {status['running']}
  - 今日完成: {status['completed_today']}
  - 今日失败: {status['failed_today']}

任务类型分布:
"""
        
        for task_type, count in sorted(task_type_counts.items(), key=lambda x: x[1], reverse=True):
            report += f"  - {task_type}: {count}次\n"
        
        # 待执行任务预览
        if self.task_queue:
            report += "\n即将执行的任务:\n"
            for task in self.task_queue[:5]:
                report += f"  - {task.task_type} @ {task.scheduled_time.strftime('%H:%M')}\n"
        
        report += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        
        return report
    
    def _save_tasks(self):
        """保存任务数据"""
        # 保存队列
        queue_file = self.data_dir / "task_queue.json"
        with open(queue_file, 'w', encoding='utf-8') as f:
            json.dump(
                [asdict(t) for t in self.task_queue],
                f,
                ensure_ascii=False,
                indent=2,
                default=lambda x: x.value if isinstance(x, Enum) else str(x)
            )
        
        # 保存历史
        history_file = self.data_dir / "task_history.json"
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(
                [asdict(t) for t in self.task_history[-200:]],
                f,
                ensure_ascii=False,
                indent=2,
                default=lambda x: x.value if isinstance(x, Enum) else str(x)
            )
    
    def _load_tasks(self):
        """加载任务数据"""
        # 加载队列
        queue_file = self.data_dir / "task_queue.json"
        if queue_file.exists():
            try:
                with open(queue_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.task_queue = [self._dict_to_task(t) for t in data]
            except:
                pass
        
        # 加载历史
        history_file = self.data_dir / "task_history.json"
        if history_file.exists():
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.task_history = [self._dict_to_task(t) for t in data]
            except:
                pass
    
    def _dict_to_task(self, data: Dict) -> ScheduledTask:
        """字典转任务对象"""
        task = ScheduledTask(
            task_id=data["task_id"],
            task_type=data["task_type"],
            priority=TaskPriority[data["priority"]],
            scheduled_time=datetime.fromisoformat(data["scheduled_time"]),
            parameters=data["parameters"],
            status=TaskStatus(data["status"]),
            created_at=data.get("created_at"),
            completed_at=data.get("completed_at"),
            result=data.get("result"),
            retry_count=data.get("retry_count", 0),
            max_retries=data.get("max_retries", 3)
        )
        return task
