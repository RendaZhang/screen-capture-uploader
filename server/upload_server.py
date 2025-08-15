import os
from datetime import datetime

from flask import Flask, request

app = Flask(__name__)

# 设置图片保存的文件夹（当前目录下的 uploads 文件夹）
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # 如果不存在则创建


@app.route("/upload", methods=["POST"])
def upload_file():
    # 获取上传的文件对象，字段名为 'file'
    file = request.files.get("file")
    if not file or file.filename == "":
        return "No file provided", 400

    # 生成带时间戳的唯一文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"

    # 拼接保存路径
    save_path = os.path.join(UPLOAD_FOLDER, filename)

    # 保存文件
    file.save(save_path)
    print(f"[{timestamp}] ✅ File received and saved: {save_path}")

    return "OK", 200


if __name__ == "__main__":
    # 启动 Flask 服务，绑定所有 IP（以便局域网访问）
    app.run(host="0.0.0.0", port=5000)
