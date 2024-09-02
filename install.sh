# 帮我优化和完善以下这个 SHELL, 生产目录和项目文件不是同一个用户,用户和目录都是需要输入的.帮我检查文件是否被修改,我要保证文件没有被串改
```bash
#!/bin/bash

# 创建生产目录
mkdir -p /home/baichuan/production/llmserver

# 复制项目文件
cp -R /home/baichuan/projects/llmserver/* /home/baichuan/production/llmserver/

# 创建并激活虚拟环境
cd /home/baichuan/production/llmserver
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 创建 systemd 服务文件
echo "[Unit]
Description=LLM Server
After=network.target

[Service]
User=baichuan
Group=baichuan
WorkingDirectory=/home/baichuan/production/llmserver
ExecStart=/home/baichuan/production/llmserver/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target" | sudo tee /etc/systemd/system/llmserver.service

# 启动和启用服务
sudo systemctl start llmserver.service
sudo systemctl enable llmserver.service
```

pip download -r requirements.txt -d /path/to/downloaded_packages

pip install --no-index --find-links /path/to/downloaded_packages -r requirements.txt

pip install --no-index --find-links http://your-internal-server/path/to/downloaded_packages -r requirements.txt


#!/bin/bash

# 获取用户输入
read -p "Enter the username: " username
read -p "Enter the URL of the compressed project file: " project_url
read -p "Enter the production directory: " production_dir
read -p "Enter the internal HTTP server URL for pip packages: " pip_server_url

# 下载项目文件
wget "${project_url}" -O project_archive.tar.gz

# 创建生产目录并解压项目文件
mkdir -p "${production_dir}"
tar -xzf project_archive.tar.gz -C "${production_dir}"

# 创建并激活虚拟环境
cd "${production_dir}"
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install --no-index --find-links "${pip_server_url}" -r requirements.txt

# 创建 systemd 服务文件
service_file="/etc/systemd/system/llmserver.service"
echo "[Unit]
Description=LLM Server
After=network.target

[Service]
User=${username}
Group=${username}
WorkingDirectory=${production_dir}
ExecStart=${production_dir}/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target" | sudo tee "${service_file}"

# 启动和启用服务
sudo systemctl start llmserver.service
sudo systemctl enable llmserver.service

# 文件完整性检查
# 使用 md5sum 或其他哈希函数检查文件完整性
find "${production_dir}" -type f -exec md5sum {} \; > checksums.md5
# 使用上述生成的 checksums.md5 文件来检查文件是否被修改
echo "Checking for file modifications..."
md5sum -c checksums.md5

#!/bin/bash

# 设置项目目录、服务器上传路径和版本号
read -p "Enter the project directory: " project_dir
read -p "Enter the HTTP server upload path: " upload_path
read -p "Enter the version number: " version

# 定义文件名，包括版本号
file_name="project_v${version}.tar.gz"

# 打包项目文件
tar -czf "${file_name}" -C "${project_dir}" .

# 生成校验码
md5sum "${file_name}" > "${file_name}.md5"

# 上传项目文件和校验码
# 注意：以下命令依赖于您的服务器配置和可用的上传工具
# 这里使用 scp 作为示例；请根据实际情况替换为合适的上传命令
scp "${file_name}" "${file_name}.md5" "${upload_path}"


#!/bin/bash

# 设置服务器信息和本地文件路径
server_username="[USERNAME]"
server_address="[SERVER_ADDRESS]"
remote_base_path="[REMOTE_BASE_PATH]" # 例如 /var/www/html/your_project
local_file_path="[LOCAL_FILE_PATH]"
version="[VERSION]"

# 定义远程版本目录
remote_version_path="${remote_base_path}/v${version}"

# 检查远程版本目录是否存在
if ssh ${server_username}@${server_address} "[ -d '${remote_version_path}' ]"
then
    echo "Error: The version directory already exists on the server."
    exit 1
else
    echo "Version directory does not exist. Proceeding with upload."
    # 创建远程版本目录
    ssh ${server_username}@${server_address} "mkdir -p '${remote_version_path}'"
    # 上传文件到远程版本目录
    scp ${local_file_path} ${server_username}@${server_address}:${remote_version_path}/
    echo "File uploaded successfully."
fi



#!/bin/bash

# 默认用户名
default_username="default_user"

# 设置项目目录、服务器上传路径、版本号
read -p "Enter the project directory: " project_dir
read -p "Enter the server username (default: ${default_username}): " server_username
server_username=${server_username:-$default_username}  # 如果未输入，使用默认用户名
read -p "Enter the server address: " server_address
read -p "Enter the remote base path: " remote_base_path
read -p "Enter the version number: " version

# 其余脚本内容...

#!/bin/bash

# 设置项目目录、服务器上传路径、版本号
read -p "Enter the project directory: " project_dir
read -p "Enter the server username: " server_username
read -p "Enter the server address: " server_address
read -p "Enter the remote base path: " remote_base_path
read -p "Enter the version number: " version

# 定义文件名，包括版本号
file_name="project_v${version}.tar.gz"
checksum_file_name="project_v${version}.md5"

# 打包项目文件
tar -czf "${file_name}" -C "${project_dir}" .

# 生成校验码
md5sum "${file_name}" > "${checksum_file_name}"

# 检查远程版本目录是否存在
remote_version_path="${remote_base_path}/v${version}"
if ssh ${server_username}@${server_address} "[ -d '${remote_version_path}' ]"
then
    echo "Error: Version directory already exists on the server."
    exit 1
else
    echo "Version directory does not exist. Proceeding with upload."
    # 创建远程版本目录并上传文件
    ssh ${server_username}@${server_address} "mkdir -p '${remote_version_path}'"
    scp "${file_name}" "${checksum_file_name}" ${server_username}@${server_address}:${remote_version_path}/
    echo "Files uploaded successfully."
fi


curl -X POST http://172.16.1.120:9002/v1/chat/llmchat/stream \
   -H "Content-Type: application/json"   \
   -d '{
        "messages": [
          {
            "role": "user",
            "content": "世界第一高峰是?"
          }
        ],
        "stream": true
      }'
