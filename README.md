# 🚦 SafeRoute: US Traffic Accidents Data Pipeline

![Snowflake](https://img.shields.io/badge/Snowflake-Computed-blue?style=for-the-badge&logo=snowflake)
![dbt](https://img.shields.io/badge/dbt-Transformation-orange?style=for-the-badge&logo=dbt)
![Dagster](https://img.shields.io/badge/Dagster-Orchestration-gray?style=for-the-badge&logo=dagster)
![Airbyte](https://img.shields.io/badge/Airbyte-Ingestion-purple?style=for-the-badge&logo=airbyte)
![Power BI](https://img.shields.io/badge/PowerBI-Visualization-F2C811?style=for-the-badge&logo=powerbi)

> **A comprehensive, automated data engineering solution to analyze 7.7 million US traffic accidents (2016–2023), transforming unstructured raw logs into actionable intelligence.**

---

## 📌 Table of Contents
1. [Business Problem & Context](#-business-problem--context)
2. [Project Objectives](#-project-objectives)
3. [Dataset Overview](#-dataset-overview)
4. [Solution Architecture](#-solution-architecture)
5. [Tech Stack](#-tech-stack)
6. [Engineering & Data Modeling](#-engineering--data-modeling)
7. [Optimization, Quality & Testing](#-optimization-quality--testing-highlights)
8. [Orchestration & Monitoring](#-orchestration--monitoring)
9. [Dashboards](#-power-bi-dashboards)
10. [Quickstart](#-quickstart)
11. [Team](#-team)

---

## 🔥 Business Problem & Context

The United States reports over **7.7 million accidents** in a span of just 7 years. While this data is publicly available, it remains an untapped resource due to its complexity. The core issues we are addressing include:

### 1️⃣ Human Impact
Accidents are not just statistics; they represent lives affected. Understanding the patterns behind these incidents is crucial for safety improvements.

### 2️⃣ Economic Loss
Traffic delays, damaged infrastructure, and emergency response operations cost the economy billions of dollars annually. Efficient analysis can help mitigate these costs.

### 3️⃣ Unstructured & Messy Data
The raw dataset is "Data Rich, Information Poor." It suffers from significant engineering challenges:
* **Missing Values:** Large gaps in critical columns.
* **Inconsistent Data Types:** Mixed formats across years.
* **Data Silos:** 13 scattered boolean fields making querying difficult.
* **Lack of Schema:** No clear modeling; weather, time, and location data are mixed without structure.

> **Bottom Line:** We have plenty of data, but no clear story behind it. This project bridges that gap.

---

## 🎯 Project Objectives

To solve the problems above, this pipeline delivers:

1.  **Centralize:** Ingest all raw accident data into a **Snowflake Bronze Layer** (Raw) in a unified structure.
2.  **Automate:** Build a fully automated ELT pipeline using **Airbyte** (Ingestion), **dbt** (Transformation), and **Dagster** (Orchestration).
3.  **Transform:** Clean, standardize, and model the data into a **Star Schema** optimized for high-performance analytics (Gold Layer).
4.  **Visualize:** Produce interactive dashboards to visualize accident patterns, infrastructure risks, and weather impacts.
5.  **Monitor:** Implement "Data Observability" to detect failures instantly and trigger **Email Alerts** for immediate response.

---

## 📊 Dataset Overview

We are working with a massive open dataset covering the contiguous United States.

* **Volume:** 7.7 Million+ Records.
* **Coverage:** 49 States.
* **Timeline:** Feb 2016 – Mar 2023.

### 📌 Key Attributes
| Category | Details |
| :--- | :--- |
| **Location** | Latitude, Longitude, City, County, State, Zipcode. |
| **Time** | Start/End timestamps, Duration, Timezone. |
| **Weather** | Visibility (miles), Wind Speed, Precipitation, Weather Condition. |
| **Road Features** | Traffic Signals, Junctions, Crossings, Roundabouts (Boolean flags). |
| **Severity** | Scale from 1 (Least impact) to 4 (Significant impact). |

---

## 🏗 Solution Architecture

The system follows a modern **Medallion Architecture** (Bronze $\rightarrow$ Silver $\rightarrow$ Gold).

```mermaid
graph LR
    subgraph "Ingestion (EL)"
        S3[(AWS S3 - Raw CSV)] -->|Sync| Airbyte[Airbyte]
        Airbyte --> Bronze[(Snowflake Bronze)]
    end

    subgraph "Transformation (T)"
        Bronze -->|Clean & Cast| Silver[(Snowflake Silver)]
        Silver -->|Star Schema| Gold[(Snowflake Gold)]
    end

    subgraph "Orchestration & Control"
        Dagster[Dagster] -->|Trigger| Airbyte
        Dagster -->|Run Models| dbtCore(dbt Core)
        Dagster -->|Refresh| PowerBI[Power BI]
        Dagster -.->|Alert| Email[(Email System)]
    end

    PowerBI --> DecisionMakers((Stakeholders))
````

-----

## 🧰 Tech Stack

| Component | Technology | Role in Pipeline |
| :--- | :--- | :--- |
| **Storage** | **AWS S3** | Object storage for raw CSV files. |
| **Ingestion** | **Airbyte Cloud** | Managed connector to sync S3 data to Snowflake. |
| **Warehouse** | **Snowflake** | Cloud Data Warehouse (Separation of Storage & Compute). |
| **Transformation** | **dbt Core** | SQL-based transformation, testing, and documentation. |
| **Orchestration** | **Dagster** | Workflow automation, asset management, and alerting. |
| **Analytics** | **Power BI** | Business Intelligence and Visualization. |
| **Alerting** | **SMTP** | Automated email notifications for pipeline failures. |

-----

## 🧠 Engineering & Data Modeling

### ⭐ Star Schema Implementation

To ensure fast analytical queries, the Gold layer is modeled using a **Star Schema**:

  * **Fact Table:** `FACT_ACCIDENTS` (Contains metrics like Duration, Distance, Severity).
  * **Dimensions:**
      * `DIM_LOCATION` (Hierarchical: City $\rightarrow$ County $\rightarrow$ State).
      * `DIM_WEATHER` (Conditions, Temperature, Visibility).
      * `DIM_TIME` (Date parts, Day/Night).
      * `DIM_ROAD_CONFIG` (Infrastructure flags).

-----

## 🔧 Optimization, Quality & Testing (Highlights)

This section details the engineering decisions made to ensure **Performance** and **Trust**.

### 1️⃣ Optimization: MD5 Fingerprint Keys

To guarantee **Idempotency** and avoid relying on unstable source IDs:

  * I generated a surrogate key using an **MD5 Hash** of critical fields:
    `MD5(Start_Time + Latitude + Longitude + Description)`
  * **Benefit:** Prevents duplicates during incremental loads and ensures a consistent Primary Key across all layers.

### 2️⃣ Optimization: Snowflake Clustering

Querying 7.7M records by specific geographies was initially slow.

  * **Solution:** Applied Snowflake **Automatic Clustering** on `FACT_ACCIDENTS`.
  * **Cluster Keys:** `Start_Date`, `State`, `GeoPoint`.
  * **Result:** Enabled **Partition Pruning**, drastically reducing the number of micro-partitions scanned for geospatial queries.

### 3️⃣ Data Quality: dbt Testing

We don't just load data; we test it.

  * **Generic Tests:** `unique`, `not_null` on all Primary Keys.
  * **Logic Tests:** Enforcing business logic, e.g., checking that `End_Time > Start_Time`.
  * **Staging Logic:** Robust type casting (`TRY_TO_DOUBLE`) and Null handling (`COALESCE`).

-----

## ⚙ Orchestration & Monitoring

**Dagster** acts as the central brain of the operation, managing dependencies between Airbyte, dbt, and Power BI.

### 🚨 Email Alerting System

We implemented a robust failure detection system. If *any* step in the pipeline fails (Ingestion or Transformation):

1.  Dagster Sensor detects the failure event.
2.  SMTP server triggers an immediate **Email Alert** to the engineering team.
3.  Ensures high availability and quick MTTR (Mean Time To Recovery).

> **[Insert Screenshot of Email Alert Here]**

-----

## 📈 Power BI Dashboards

The final output empowers stakeholders with:

1.  **General Overview:** High-level KPIs (Total Accidents, Avg Severity).
2.  **Weather Impact:** Visualizing how rain/snow affects accident frequency.
3.  **Road Infrastructure:** Identifying dangerous junctions and crossings.

-----

## 🚀 Quickstart

```bash
# 1. Clone the repository
git clone [https://github.com/amramgad8/SafeRoute-Data-Pipeline.git](https://github.com/amramgad8/SafeRoute-Data-Pipeline.git)
cd SafeRoute-Data-Pipeline

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup dbt
cd dbt_project
dbt deps
dbt build

# 4. Launch Dagster
cd ../orchestration
dagster dev
```

-----

## 👥 Team

  * **Amr Amgad** – Data Engineering & Cloud Architecture
  * **Mark Ayman** – Data Modeling
  * **Abdelrahman Khaled** – Analytics & Visualization

-----

**SafeRoute** delivers a production-grade modern data pipeline—fully automated, tested, and optimized for performance.
*If you find this project useful, feel free to ⭐ the repo\!*

```
