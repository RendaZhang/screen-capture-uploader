import io
import queue
import threading
import time
from datetime import datetime

import requests
from PIL import ImageGrab

# =======================
# 配置参数（可自行修改）
# =======================
UPLOAD_URL = "http://192.168.8.102:5000/upload"  # 上传服务器地址
CAPTURE_INTERVAL = 30  # 每隔多少秒截图一次
RETRY_INTERVAL = 10  # 上传失败后重试间隔
MAX_RETRY = 3  # 最大重试次数


# =======================
# 上传任务的数据结构
# =======================
class UploadTask:
    def __init__(self, image_data, filename, retry=0):
        self.image_data = image_data
        self.filename = filename
        self.retry = retry


# =======================
# 截图函数
# =======================
def capture_screen():
    """抓取当前主屏幕的全屏截图，并返回二进制数据和生成的文件名"""
    image = ImageGrab.grab()
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshot_{timestamp}.png"

    return buffer, filename


# =======================
# 上传函数
# =======================
def upload_image(task):
    """将截图数据上传到远程服务器"""
    try:
        response = requests.post(
            UPLOAD_URL,
            files={"file": (task.filename, task.image_data, "image/png")},
            timeout=10,
        )
        print(
            f"[{datetime.now()}] ✅ Uploaded: {task.filename} ({response.status_code})"
        )
        return True
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Upload failed: {task.filename} | Error: {e}")
        return False


# =======================
# 上传线程主逻辑
# =======================
def upload_worker(upload_queue):
    """上传线程：从队列中获取任务，上传，失败则重试"""
    while True:
        task = upload_queue.get()

        if not upload_image(task) and task.retry < MAX_RETRY:
            task.retry += 1
            print(
                f"🔁 Retrying {task.filename} (Attempt {task.retry}) in {RETRY_INTERVAL}s..."
            )
            time.sleep(RETRY_INTERVAL)
            upload_queue.put(task)

        upload_queue.task_done()


# =======================
# 主循环：定时截图并提交任务
# =======================
def main_loop():
    upload_queue = queue.Queue()

    # 启动后台上传线程
    threading.Thread(target=upload_worker, args=(upload_queue,), daemon=True).start()

    while True:
        try:
            image_data, filename = capture_screen()
            task = UploadTask(image_data=image_data, filename=filename)
            upload_queue.put(task)
        except Exception as e:
            print(f"[{datetime.now()}] ❌ Error capturing screen: {e}")
        time.sleep(CAPTURE_INTERVAL)


# =======================
# 程序入口
# =======================
if __name__ == "__main__":
    print("📸 Auto Screen Capture & Upload Script Started...")
    main_loop()
