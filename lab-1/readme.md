# Lab 1

將 Promtail、Loki、Tempo 串連至 Lab 0 的架構中。

## Quick Start

1. 啟動所有服務

    ```bash
    docker-compose up -d
    ```

2. 檢視服務
   1. App A: [http://localhost:8000](http://localhost:8000)
      1. Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
      2. Metrics: [http://localhost:8000/metrics](http://localhost:8000/metrics)
   2. App B: [http://localhost:8001](http://localhost:8001)
      1. Swagger UI: [http://localhost:8001/docs](http://localhost:8001/docs)
      2. Metrics: [http://localhost:8001/metrics](http://localhost:8001/metrics)
   3. App C: [http://localhost:8080](http://localhost:8082)
      1. Swagger UI: [http://localhost:8080/swagger-ui/index.html](http://localhost:8080/swagger-ui/index.html)
      2. Metrics: [http://localhost:8080/actuator/prometheus](http://localhost:8080/actuator/prometheus)
   4. cAdvisor: [http://localhost:8081](http://localhost:8081)
   5. Prometheus: [http://localhost:9090](http://localhost:9090)
   6. Grafana: [http://localhost:3000](http://localhost:3000)，登入帳號密碼為 `admin/admin`
      1. 點擊左上 Menu > Dashboards > Cadvisor exporter、FastAPI Observability、Spring Boot Observability，即可查看透過 Provisioning 建立的 Dashboard
3. 關閉所有服務

    ```bash
    docker-compose down
    ```

## Goals

![Lab Architecture](./img/lab-1-arch.png)

1. 建立 FastAPI App（app-a、app-b）
   1. 透過 Prometheus Client 產生 OpenMetrics，揭露於 `/metrics` endpoint
   2. 透過 OpenTelemetry Manual Instrumentation 產生 Trace，發送至 Tempo
   3. 透過 OpenTelemetry Manual Instrumentation 與調整 Log Pattern 將 Trace ID 與 Span ID 寫入 Log
2. 建立 Spring Boot App（app-c）
   1. 透過 Spring Boot Actuator 與 Micrometer 產生 OpenMetrics，揭露於 `/actuator/prometheus` endpoint
   2. 透過 OpenTelemetry Automatic Instrumentation 產生 Trace，發送至 Tempo
   3. 透過 OpenTelemetry Automatic Instrumentation 與調整 Log Pattern 將 Trace ID 與 Span ID 寫入 Log
3. 建立 cAdvisor，監控 Docker Container，Prometheus Metrics 揭露於 `/metrics` endpoint
4. 建立 Prometheus，收集 app-a、app-b、app-c、cAdvisor 的 Metrics
5. 建立 Promtail，收集 Container Log，發送至 Loki
6. 建立 Loki，接收 Promtail 收集的 Log
7. 建立 Tempo，接收 App A、App B、App C 發送的 Trace
8. 建立 Grafana，查詢 Prometheus、Loki、Tempo 資料

## Tasks

<details><summary>Task 1: 開啟 <a href="http://localhost:8000" target="_blank">http://localhost:8000</a> 後，查詢 App A 的 Log</summary>

1. 開啟 Grafana UI，點擊左上選單後進入 `Explore` 頁籤
2. 左上下拉選單選擇 `Loki`，Label 選擇 `container=app-a` 後點擊 `Run Query`

<img src="./img/task-1.png" />

</details>

<details><summary>Task 2: 開啟 <a href="http://localhost:8080/chain" target="_blank">http://localhost:8080/chain</a> 後，查詢 App C 該筆 Request 的 Trace</summary>

1. 開啟 Grafana UI，點擊左上選單後進入 `Explore` 頁籤
2. 左上下拉選單選擇 `Tempo`，Query Type 選擇 `Search`，`Resource Service Name` 選擇 `app-c`，`Span Name` 選擇 `GET /chain` 後點擊 `Run Query`

<img src="./img/task-2-query.png" />

<img src="./img/task-2-trace.png" />

</details>

<details><summary>Task 3: 透過 App C 的 Swagger UI <a href="http://localhost:8080/swagger-ui/index.html" target="_blank">http://localhost:8080/swagger-ui/index.html</a> 執行 POST `/peanuts` 一次建立角色，再執行 GET `/peanuts/0` 兩次，查詢 App C 這三筆 Request 的 Trace</summary>

1. 開啟 Grafana UI，點擊左上選單後進入 `Explore` 頁籤
2. 左上下拉選單選擇 `Tempo`，Query Type 選擇 `Search`，`Resource Service Name` 選擇 `app-c`，`Span Name` 選擇 `POST /peanuts` 與 `GET /peanuts/` 後點擊 `Run Query`

<img src="./img/task-3-query.png" />

<img src="./img/task-3-trace-post.png" />

<img src="./img/task-3-trace-get-select.png" />

<img src="./img/task-3-trace-get-cache.png" />

</details>
