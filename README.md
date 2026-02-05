# screen-capture-uploader

一个用于**Mac 自动截图并上传到 Windows** 的小工具，适合在同一局域网内做跨设备截图同步。

- `client/`：运行在 **Mac**，定时截图并上传。
- `server/`：运行在 **Windows**，接收图片并保存到本地。

---

## 1. 使用场景（Mac -> Windows）

典型流程如下：

1. 在 Windows 电脑上启动接收服务（Flask Server）。
2. 在 Mac 电脑上运行截图上传脚本。
3. Mac 每隔一段时间抓取全屏并上传到 Windows。
4. Windows 把图片保存到 `server/uploads/` 目录。

---

## 2. 目录结构

```text
screen-capture-uploader/
├─ client/
│  ├─ capture_upload.py
│  └─ requirements.txt
├─ server/
│  ├─ upload_server.py
│  └─ requirements.txt
└─ README.md
```

---

## 3. 环境要求

- Python 3.9+（推荐 3.10/3.11）
- Mac 与 Windows 在同一个局域网
- Windows 防火墙允许服务端端口（默认 `5000`）

---

## 4. Windows 端（Server）启动步骤

> 以下以 PowerShell 为例。

### 4.1 进入项目目录

```powershell
cd path\to\screen-capture-uploader\server
```

### 4.2 创建并激活虚拟环境

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

如果你的 PowerShell 禁止执行脚本，可先临时放开：

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 4.3 安装依赖

```powershell
pip install -r requirements.txt
```

### 4.4 启动服务

```powershell
python upload_server.py
```

服务默认监听：`0.0.0.0:5000`。

启动后，图片会保存到：

```text
server/uploads/
```

---

## 5. Mac 端（Client）启动步骤

> 以下以 macOS 终端（zsh/bash）为例。

### 5.1 进入项目目录

```bash
cd /path/to/screen-capture-uploader/client
```

### 5.2 创建并激活虚拟环境

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 5.3 安装依赖

```bash
pip install -r requirements.txt
```

### 5.4 修改上传地址（非常重要）

编辑 `client/capture_upload.py`，把 `UPLOAD_URL` 改成 Windows 电脑的局域网 IP：

```python
UPLOAD_URL = "http://192.168.1.22:5000/upload"
```

其中 `192.168.1.22` 需要替换为你自己的 Windows 局域网地址。

### 5.5 启动截图上传程序

```bash
python capture_upload.py
```

首次运行时，macOS 可能会提示授权“屏幕录制（Screen Recording）”，请允许对应终端/解释器。

### 5.6 在 Mac 后台运行 Client（nohup + `&`）

如果你希望关闭终端窗口后脚本仍继续运行，可以使用 `nohup`：

```bash
nohup python capture_upload.py > client.log 2>&1 &
```

说明：

- `nohup`：终端关闭后进程也不会退出。
- `> client.log 2>&1`：把标准输出和错误输出都写入日志文件 `client.log`。
- `&`：让程序在后台运行并立即返回 shell。

启动后可用下面命令查看后台进程：

```bash
ps -ef | grep capture_upload.py | grep -v grep
```

也可以直接查看日志确认脚本在工作：

```bash
tail -f client.log
```

### 5.7 运行后检查并杀死后台 Client 进程

先查出进程 PID：

```bash
ps -ef | grep capture_upload.py | grep -v grep
```

输出中第二列通常是 PID，例如 `12345`。

优雅停止（推荐先尝试）：

```bash
kill 12345
```

如果进程仍未退出，再强制结束：

```bash
kill -9 12345
```

可再次执行以下命令确认进程已结束（无输出即已停止）：

```bash
ps -ef | grep capture_upload.py | grep -v grep
```

---

## 6. Server IP 说明（为什么要固定 IP）

客户端代码中写死了服务端地址（`UPLOAD_URL`）。

如果 Windows 的局域网 IP 变化了（例如从 `192.168.1.22` 变成 `192.168.1.35`），Mac 就会上传失败。因此建议：

- 给 Windows 电脑配置**固定内网 IP**（静态 IP），或者
- 在路由器中做 DHCP 地址保留（推荐）

这样 Mac 端配置一次后可长期稳定运行。

---

## 7. 如何查看并固定 Windows 内网 IP（简易教程）

### 7.1 先查看当前 IP

在 Windows PowerShell：

```powershell
ipconfig
```

找到当前网络适配器（Wi-Fi/以太网）的 IPv4 地址，例如：`192.168.1.22`。

### 7.2 方法 A：在路由器里做 DHCP 保留（推荐）

不同路由器界面叫法可能不同：

- DHCP Reservation
- Address Reservation
- Static Lease

基本步骤：

1. 在 Windows 上执行 `ipconfig /all`，记下网卡 `Physical Address (MAC)`。
2. 登录路由器管理后台（常见地址如 `192.168.1.1`）。
3. 在 DHCP 保留页面新增一条记录：
   - 设备 MAC 地址：Windows 网卡 MAC
   - 分配 IP：例如 `192.168.1.22`
4. 保存并重连网络（或重启网卡/电脑）。

这样路由器会始终给该设备分配同一 IP。

### 7.3 方法 B：Windows 手动设置静态 IP

路径（Windows 11）：

1. `设置 -> 网络和 Internet -> 高级网络设置 -> 更多网络适配器选项`
2. 右键当前网卡 -> `属性`
3. 双击 `Internet 协议版本 4 (TCP/IPv4)`
4. 选择“使用下面的 IP 地址”，填写：
   - IP 地址：如 `192.168.1.22`
   - 子网掩码：通常 `255.255.255.0`
   - 默认网关：路由器地址（如 `192.168.1.1`）
   - DNS：可填路由器地址或公共 DNS（例如 `8.8.8.8`）

> 注意：静态 IP 必须在同网段且不能与其他设备冲突。

---

## 8. 常见问题排查

### 8.1 Mac 端报连接失败 / 超时

- 确认 Windows 服务已启动。
- 确认 `UPLOAD_URL` 中 IP 正确，且端口是 `5000`。
- 确认两台机器在同一局域网。
- 确认 Windows 防火墙允许 Python/5000 入站。

### 8.2 没有截图权限

在 macOS 里给终端（或你使用的 Python IDE）授予“屏幕录制”权限，然后重启程序。

### 8.3 上传频率调整

编辑 `client/capture_upload.py`：

- `CAPTURE_INTERVAL`：截图间隔秒数
- `RETRY_INTERVAL`：失败重试间隔
- `MAX_RETRY`：最大重试次数

---

## 9. 停止运行

在运行窗口按 `Ctrl + C` 停止服务端或客户端。

---

## 10. 安全建议

当前服务无鉴权，建议仅在可信局域网中使用。若需在更大网络环境使用，请增加认证、HTTPS、访问控制等安全机制。
