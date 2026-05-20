### *RECRUITMENT PIPELINE*

![Architecture](recu-realtime.png)

> *Near-realtime pipeline xử lý dữ liệu tuyển dụng
```markdown
# Real-time Data Engineering Pipeline - Recruitment Platform

##  Mô tả dự án
Hệ thống pipeline xử lý dữ liệu **Near Real-time** cho nền tảng tuyển dụng. Thu thập dữ liệu tracking từ Data Lake, xử lý aggregation (clicks, conversions, qualified, unqualified), sau đó load vào Data Warehouse để phân tích và visualize.

## 🏗 Kiến trúc hệ thống

- **Data Lake**: MongoDB (NoSQL)
- **Processing Engine**: PySpark (Local Mode)
- **Data Warehouse**: MySQL
- **Visualization**: Grafana
- **Orchestration**: Docker Compose
- **Scheduling**: Cron job (chạy mỗi 4-5 phút)

##  Công nghệ sử dụng

| Layer              | Technology                  |
|--------------------|-----------------------------|
| Data Lake          | MongoDB 7.0                 |
| ETL Engine         | PySpark 3.5.4 (Local Mode)  |
| Data Warehouse     | MySQL 8.0                   |
| Visualization      | Grafana                     |
| Container          | Docker Compose              |
| Scheduling         | Linux Cron                  |

##  Cấu trúc thư mục

## 🛠 Cách chạy dự án

### 1. Khởi động hệ thống

```bash
docker compose up -d
```

### 2. Chạy Fake Data (Near Realtime)

```bash
docker exec spark bash -c "cd /opt/spark/scripts && nohup python3 fake_data.py > /var/log/fake_data.log 2>&1 &"
```

### 3. Chạy ETL thủ công

```bash
docker exec spark bash -c "
cd /opt/spark && 
export JAVA_HOME=/opt/java/openjdk && 
python3 scripts/etl.py
"
```

### 4. Thiết lập Cron Job

```bash
crontab -l
```

##  Dashboard Grafana

Truy cập: `http://<EC2_IP>:3000`  
- User/Pass: `admin` / `admin`
- Data Source: MySQL (`mysql:3306`, database `warehouse`)

##  Các Metrics chính

- Số clicks, conversions, qualified, disqualified theo ngày/giờ
- Top Job ID có tương tác cao
- Chi phí (bid/spend) theo campaign

##  Tính năng Near Real-time

- Fake data generator tạo records mới **mỗi 60 giây**
- ETL job chạy **mỗi 4 phút**
- Dữ liệu được aggregate và load liên tục vào MySQL

---
