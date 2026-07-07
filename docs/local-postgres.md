# Local PostgreSQL With Docker

## English Version

### Purpose

Use a local PostgreSQL container for MVP validation and development. This database is only a local sandbox. Production data should live in a managed server or cloud database.

### Start

Run from the project root:

```powershell
docker compose up -d
```

### Check Status

```powershell
docker ps
docker logs gongkao-postgres
```

### Connection Info

```text
Host: localhost
Port: 5432
Database: gongkao_dev
User: gongkao
Password: gongkao_dev_password
```

Database URL:

```text
postgresql://gongkao:gongkao_dev_password@localhost:5432/gongkao_dev
```

### Open psql

```powershell
docker exec -it gongkao-postgres psql -U gongkao -d gongkao_dev
```

Then verify:

```sql
SELECT version();
```

### Stop Or Remove

Stop the container:

```powershell
docker compose stop
```

Remove the container while keeping the database volume:

```powershell
docker compose down
```

Remove the container and local database data:

```powershell
docker compose down -v
```

Use `down -v` carefully because it deletes the local PostgreSQL volume.

### Schema Management Rule

Do not treat local database tables as the source of truth. Schema changes should be represented by migration files in Git. The local database, staging database, and production database should all be created or upgraded by the same migrations.

## 中文版本

### 目的

使用本地 PostgreSQL 容器进行 MVP 验证和开发。这个数据库只是本地沙盘，正式业务数据应该放在服务器或云托管数据库中。

### 启动

在项目根目录运行：

```powershell
docker compose up -d
```

### 查看状态

```powershell
docker ps
docker logs gongkao-postgres
```

### 连接信息

```text
Host: localhost
Port: 5432
Database: gongkao_dev
User: gongkao
Password: gongkao_dev_password
```

数据库连接字符串：

```text
postgresql://gongkao:gongkao_dev_password@localhost:5432/gongkao_dev
```

### 打开 psql

```powershell
docker exec -it gongkao-postgres psql -U gongkao -d gongkao_dev
```

进入后验证：

```sql
SELECT version();
```

### 停止或删除

停止容器：

```powershell
docker compose stop
```

删除容器但保留数据库 volume：

```powershell
docker compose down
```

删除容器和本地数据库数据：

```powershell
docker compose down -v
```

谨慎使用 `down -v`，因为它会删除本地 PostgreSQL 数据卷。

### Schema 管理规则

不要把本地数据库里的表当作事实来源。表结构变更应该以 migration 文件的形式进入 Git。本地数据库、测试数据库和生产数据库都应该通过同一套 migration 创建或升级。
