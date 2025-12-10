# 在 Docker 上构建项目

在项目根目录下运行以下命令来构建镜像：

```bash
docker-compose build
```

如果在构建过程中出现类似下图的错误（无法从 Docker Hub 拉取镜像）：

![Docker build 问题](./image/docker_bulid_problem1.png)

原因：网络无法访问 Docker Hub，导致无法拉取 `python:3.11-slim` 和 `node:18-alpine` 这两个基础镜像。

解决办法：

1. 手动拉取缺失的镜像：

```bash
docker pull python:3.11-slim
docker pull node:18-alpine
```

2. 确保网络通畅后，重新执行构建命令：

```bash
docker-compose build
```

构建完成后，请确认本地是否安装并运行了 MySQL：

- 如果尚未安装，请先安装 MySQL。
- 在 MySQL 中创建一个名为 `notecraft_db` 的数据库（或根据项目配置使用相应的数据库名）。

准备就绪后，在项目目录运行：

```bash
docker-compose up
```

启动成功后，可以在 Docker 面板中查看运行的服务或直接在浏览器中打开前端暴露的端口（例如 `http://localhost:3000`，具体端口以项目配置为准）来访问页面。

附加提示：

- 如果从 Docker Hub 拉取镜像速度慢或失败，可以考虑配置国内镜像加速器或使用 VPN。 
- 请注意文件名大小写问题（在某些部署环境中区分大小写）。
- 若遇到其它错误，请把控制台或日志信息贴出来，我可以继续帮你排查。
