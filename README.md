## 📄 README.md

```bash
cat > ~/recruitment-pipeline/README.md << 'EOF'
# Recruitment Pipeline

ETL pipeline xử lý logs tuyển dụng từ MongoDB (Data Lake) vào MySQL (Data Warehouse) bằng PySpark, tính toán các chỉ số `click`, `conversion`, `qualified`, `unqualified` theo giờ và ngày. Hỗ trợ near real‑time, visualization bằng Grafana.

## Sơ đồ kiến trúc

```
[MongoDB] --(Spark read)--> [PySpark ETL] --(JDBC)--> [MySQL] --> [Grafana]
   ^                              |                          ^
   |                       (aggregate by date, hour)        |
   |                                                        |
   +-- [Fake data generator (cron 1')]                      +-- (dashboard query)
```

## Thành phần

| Service    | Công nghệ           | Cổng     |
|------------|---------------------|----------|
| Data Lake  | MongoDB 7.0         | 27017    |
| Data Warehouse | MySQL 8.0        | 3306     |
| ETL Engine | PySpark 3.5.4 (container) | 8080 |
| Visualization | Grafana          | 3000     |

## Yêu cầu

- Docker & Docker Compose
- Git

## Cài đặt nhanh

```bash
git clone https://github.com/thnguyendinh/recruitment-pipeline.git
cd recruitment-pipeline
docker-compose up -d
```

Tạo bảng `events` trong MySQL:

```bash
docker exec mysql mysql -uroot -pexample warehouse -e "
CREATE TABLE IF NOT EXISTS events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE,
    hour INT,
    job_id INT,
    campaign_id INT,
    publisher_id INT,
    group_id INT,
    clicks INT DEFAULT 0,
    conversions INT DEFAULT 0,
    qualified INT DEFAULT 0,
    disqualified INT DEFAULT 0,
    bid_set DOUBLE,
    spend_hour DOUBLE,
    sources VARCHAR(50),
    load_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"
```

Tải JAR connector:

```bash
docker exec spark bash -c "
mkdir -p /opt/spark/extra-jars && cd /opt/spark/extra-jars
curl -O https://repo1.maven.org/maven2/org/mongodb/spark/mongo-spark-connector_2.12/10.4.0/mongo-spark-connector_2.12-10.4.0.jar
curl -O https://repo1.maven.org/maven2/com/mysql/mysql-connector-j/8.0.30/mysql-connector-j-8.0.30.jar
"
```

## Chạy ETL thủ công

```bash
docker exec spark bash -c "export JAVA_HOME=/opt/java/openjdk && export SPARK_HOME=/opt/spark && cd /opt/spark && python3 /opt/spark/scripts/etl.py"
```

## Near real‑time (cron)

- Fake data mỗi 1 phút: `* * * * * /home/ubuntu/recruitment-pipeline/fake_data_batch.sh`
- ETL mỗi 2 phút: `*/2 * * * * /home/ubuntu/recruitment-pipeline/scripts/run_etl.sh`

Xem log: `tail -f /var/log/etl.log`

## Grafana

1. Truy cập `http://<EC2_IP>:3000` (admin/admin)
2. Add data source MySQL: host `mysql:3306`, DB `warehouse`, user `root`, pass `example`
3. Tạo dashboard với query:

```sql
SELECT date, SUM(clicks) as clicks, SUM(spend_hour) as spend
FROM events GROUP BY date ORDER BY date;

cd ~/recruitment-pipeline
git add README.md
git commit -m "Add concise professional README with architecture diagram"
git push origin main
```
