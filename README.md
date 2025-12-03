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

The pipeline follows the **Medallion Architecture** (Bronze, Silver, Gold) to ensure data quality and scalability.

![Pipeline Architecture](Data_flow_3.png)

### 🔄 Data Flow (Interactive Map)

```mermaid
graph LR
    subgraph "Source & Ingestion"
        S3[(AWS S3 Data Lake)] -->|Raw CSV| Airbyte[Airbyte Cloud]
        Airbyte -->|Trigger| SnowBronze[(Snowflake Bronze)]
    end

    subgraph "Transformation (dbt)"
        SnowBronze -->|Clean & Cast| SnowSilver[(Snowflake Silver)]
        SnowSilver -->|Star Schema| SnowGold[(Snowflake Gold)]
    end

    subgraph "Orchestration & BI"
        Dagster{Dagster} -->|Manage| Airbyte
        Dagster -->|Run| dbt(dbt Core)
        Dagster -->|Refresh| PBI[Power BI Dashboard]
        Dagster -->|Alert| Email((Gmail Alert))
    end

    classDef tool fill:#f9f,stroke:#333,stroke-width:2px;
    class Airbyte,dbt,Dagster,PBI tool;
````

-----

## 🛠️ Tech Stack & Implementation Details

| Component | Tool | Description |
| :--- | :--- | :--- |
| **Data Lake** | **AWS S3** | Stores raw CSV data (partitioned/stored securely). |
| **Ingestion** | **Airbyte Cloud** | Automates data loading from S3 to Snowflake (Bronze Layer). |
| **Warehouse** | **Snowflake** | Cloud DWH hosting the Medallion Architecture layers. |
| **Transformation** | **dbt Core** | Performs data cleaning, testing, and modeling (Junk Dimensions, Surrogate Keys). |
| **Orchestration** | **Dagster** | Manages dependencies, assets, and creates a sensor-based trigger for pipeline failure (Gmail SMTP). |
| **Visualization** | **Power BI** | Interactive dashboard for geospatial and trend analysis. |

-----

## 📊 Data Modeling (Star Schema)

We designed a highly optimized **Star Schema** to facilitate high-performance analytics on the 7M+ records.

**Key Design Decisions:**

  * **Junk Dimension (`DIM_ROAD_CONFIG`):** Combined 13 boolean flags (bump, crossing, signal, etc.) into unique configuration keys to reduce Fact Table width.
  * **Geospatial Data:** Utilized Snowflake's `GEOGRAPHY` data type for precise location analytics.
  * **Surrogate Keys:** Generated MD5 hashes for dimension integrity.

-----

## 🚨 Orchestration & Monitoring

We implemented **Dagster Sensors** to monitor pipeline health in real-time. If any asset fails (e.g., dbt test failure or Airbyte sync error), an automated email alert is triggered immediately via SMTP.

*\> Proof of the automated failure alert system delivering real-time notifications.*

-----

## 📈 Analytics & Dashboard

The final output is a suite of Power BI dashboards used to identify accident hotspots, weather correlations, and road infrastructure impacts.

### 1\. General Overview

*High-level metrics covering total accidents, severity distribution, and temporal trends.*

### 2\. Weather Impact Analysis

*Correlating visibility, wind speed, and precipitation with accident frequency.*

### 3\. Road Infrastructure Statistics

*Analyzing the impact of road features (junctions, signals) on accident rates.*

-----

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

-----

## 👥 Team (SIC 7 - Group 11)

  * **Amr Amgad** - Data Engineering & Cloud Infrastructure
  * **Mark Ayman** - Data Modeling & Transformation
  * **Abdelrahman Khaled** - Analysis & Visualization

-----

*Project developed as part of the Samsung Innovation Campus (SIC) Graduation Program.*

````
````

وبعدها ادخل على الرابط وشوف العظمة\! 🥳
