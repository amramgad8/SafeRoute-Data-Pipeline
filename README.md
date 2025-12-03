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
