# 🚦 SafeRoute: End-to-End US Traffic Accidents Data Pipeline

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python)
![Snowflake](https://img.shields.io/badge/Snowflake-Data_Warehouse-blue?style=for-the-badge&logo=snowflake)
![dbt](https://img.shields.io/badge/dbt-Transformation-orange?style=for-the-badge&logo=dbt)
![Dagster](https://img.shields.io/badge/Dagster-Orchestration-purple?style=for-the-badge&logo=dagster)
![Airbyte](https://img.shields.io/badge/Airbyte-Ingestion-ff69b4?style=for-the-badge&logo=airbyte)
![Power BI](https://img.shields.io/badge/Power_BI-Visualization-F2C811?style=for-the-badge&logo=powerbi)

> **SafeRoute** is a robust data engineering solution designed to process, transform, and analyze over **7.7 million traffic accident records** across the US. The project leverages a Modern Data Stack to provide actionable insights for improving road safety infrastructure.

---

## 🏗️ Architecture Overview

The pipeline follows the **Medallion Architecture** (Bronze, Silver, Gold) to ensure data quality and scalability. Data flows from raw CSVs in AWS S3 to actionable insights in Power BI.

![Pipeline Architecture](Data_flow_3.png)

### 🔄 Data Flow Summary
1.  **Ingestion:** Airbyte extracts raw data from **AWS S3** and loads it into **Snowflake (Bronze Layer)**.
2.  **Transformation:** dbt Core performs data cleaning, type casting, and testing to create the **Silver Layer**.
3.  **Modeling:** dbt models the data into a **Star Schema** (Gold Layer) optimized for analytics.
4.  **Orchestration:** Dagster manages the entire workflow, dependencies, and alerting.
5.  **Visualization:** Power BI connects to the Gold Layer for reporting.

---

## 🚀 Optimization & Data Strategy

Handling 7.7M+ records required strict optimization strategies to ensure performance and reduce costs:

### 1. Data Selection Strategy
[cite_start]We reduced the dataset volume by approximately **20%** by filtering out low-impact columns (e.g., `Wind_Chill`, `Humidity`, `Civil_Twilight`) that added noise without analytical value[cite: 627, 654].

### 2. Junk Dimension Implementation
Instead of keeping 13 separate boolean columns (e.g., `Bump`, `Crossing`, `Traffic_Signal`) in the Fact table—which would increase width and slow down queries—we implemented a **Junk Dimension strategy**. We combined these flags into unique configuration keys in `DIM_ROAD_CONFIG`[cite: 666, 669].

### 3. Snowflake Optimization
* [cite_start]**Geography Data Type:** Utilized Snowflake's native `GEOGRAPHY` type for accurate spatial analysis[cite: 638].
* [cite_start]**Dedicated Warehouses:** Separated compute resources for ingestion (Airbyte) and transformation (dbt) to prevent resource contention[cite: 189].

---

## 📊 Data Modeling (Star Schema)

We designed a Star Schema centered around `FACT_ACCIDENTS` to facilitate fast aggregations and slicing.

![Star Schema](Star_Shcema_model.png)

### Dimensions Breakdown:
* **`DIM_LOCATION`**: Contains hierarchical address data (City, County, State) and geospatial points. [cite_start]It uses MD5 surrogate keys for integrity[cite: 663].
* [cite_start]**`DIM_TIME`**: A derived dimension handling Hour, Part of Day (Morning, Rush Hour), and Day/Night indicators to analyze temporal patterns[cite: 673].
* [cite_start]**`DIM_ROAD_CONFIG`**: Stores the unique combinations of road infrastructure features (Signals, Junctions, etc.)[cite: 666].
* [cite_start]**`DIM_WEATHER`**: Captures weather conditions (Rain, Fog) and wind direction to correlate environmental factors with accidents[cite: 676].
* **`DIM_DATE`**: A standard date spine supporting weekend/weekday analysis[cite: 671].

---

## 🚨 Orchestration & Monitoring

Reliability is key. We implemented **Dagster Sensors** to monitor pipeline health in real-time. If any asset fails (e.g., dbt test failure or Airbyte sync error), an automated email alert is triggered immediately via SMTP.

![Dagster Email Alert](dagster_alert_email.jpg)
*> Screenshot: Real-time critical failure alert sent to the engineering team.*

---

## 📈 Analytics & Dashboard

The final output is a suite of Power BI dashboards used to identify accident hotspots, weather correlations, and road infrastructure impacts.

### 1. General Overview
Provides high-level metrics covering total accidents (7.7M), severity distribution, and yearly trends.
![General Statistics](General_Statistics_dashboard.png)

### 2. Weather Impact Analysis
Correlates visibility, wind speed, and precipitation with accident frequency to identify dangerous conditions.
![Weather Statistics](Weather_Statistics_dashboard.png)

### 3. Road Infrastructure Statistics
Analyzes the impact of specific road features (e.g., Junctions, Traffic Signals) on accident rates and severity.
![Road Statistics](Road_Statistics_dashboard.png)

---

## 💻 How to Run Locally

### Prerequisites
* Python 3.9+
* Snowflake Account
* dbt CLI installed

### Steps

1.  **Clone the Repo**
    ```bash
    git clone [https://github.com/amramgad8/SafeRoute-Data-Pipeline.git](https://github.com/amramgad8/SafeRoute-Data-Pipeline.git)
    cd SafeRoute-Data-Pipeline
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Setup dbt Profile**
    Configure your `profiles.yml` to connect to your Snowflake account.

4.  **Run the Pipeline (Dagster UI)**
    ```bash
    dagster dev
    ```
    Navigate to `localhost:3000` to visualize and launch the pipeline.

---

## 👥 Team (SIC 7 - Group 11)

* **Amr Amgad** - Data Engineering & Cloud Infrastructure
* **Mark Ayman** - Data Modeling & Transformation
* **Abdelrahman Khaled** - Analysis & Visualization

---

*Project developed as part of the Samsung Innovation Campus (SIC) Graduation Program.*
