import os
import requests
import time
from dagster import AssetExecutionContext, asset, file_relative_path, Config
from dagster_dbt import DbtCliResource, dbt_assets, DbtProject

# ==============================================================================
# 1. Configuration
# ==============================================================================
class RunConfig(Config):
    dry_run: bool = False  # If True, skip actual execution/side-effects (simulate)
    simulate_failure: bool = False  # If True, raise an exception to simulate failure

# ==============================================================================
# 2. dbt Setup
# ==============================================================================
# Set up the dbt project directory by resolving relative path from this file
DBT_PROJECT_DIR = file_relative_path(__file__, "../../..")
dbt_project = DbtProject(project_dir=DBT_PROJECT_DIR)

# ==============================================================================
# 3. Airbyte Cloud Ingestion (READY ✅)
# ==============================================================================
@asset(
    group_name="ingestion", 
    compute_kind="airbyte",
    key_prefix=["raw_data"] 
)
def US_ACCIDENTS_RAW(context: AssetExecutionContext, config: RunConfig):
    """
    Triggers Airbyte Cloud Sync to ingest raw US accidents data.
    """
    if config.simulate_failure:
        # Raise exception intentionally to test alerting/notification mechanisms
        raise Exception("🧨 TEST FAILURE: Manual trigger for Gmail Alert testing.")

    if config.dry_run:
        # Do not trigger actual sync in dry-run mode
        context.log.warning("⚠️ DRY RUN MODE: Skipping actual Airbyte Sync.")
        return

    # Airbyte Cloud Connection ID for the pipeline
    AIRBYTE_CONNECTION_ID = "d3dad26b-7700-4489-95b6-5f1c4815c7c9"
    
    # Airbyte Cloud API Key (do not share this key publicly)
    AIRBYTE_API_KEY = (
        "********************************************"
    )
    
    # Airbyte Cloud jobs endpoint
    url = "https://api.airbyte.com/v1/jobs"
    
    headers = {
        "Authorization": f"Bearer {AIRBYTE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "connectionId": AIRBYTE_CONNECTION_ID,
        "jobType": "sync"
    }

    context.log.info("🔌 Triggering Airbyte Cloud Sync...")

    try:
        # Trigger Airbyte sync using the API
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            # Log Job ID if sync started successfully
            job_id = response.json().get("jobId")
            context.log.info(f"✅ Sync Started Successfully! Job ID: {job_id}")
        else:
            # Log Airbyte API error if request failed
            context.log.warning(f"⚠️ Airbyte API Error: {response.status_code} - {response.text}")
            # Allow execution to continue (e.g., for demo or manual sync)
            context.log.warning("👉 Continuing assuming manual sync for Demo.")
            
    except Exception as e:
        # Log connection error and re-raise exception
        context.log.error(f"❌ Connection Failed: {str(e)}")
        raise e

# ==============================================================================
# 4. dbt Analytics (READY ✅)
# ==============================================================================
@dbt_assets(
    manifest=dbt_project.manifest_path,
    dagster_dbt_translator=None,
    exclude="source:*",  # Exclude dbt sources, only build models/tests/snapshots/etc.
)
def dbt_analytics(context: AssetExecutionContext, dbt: DbtCliResource):
    # Run dbt "build" command and stream logs/results to Dagster
    yield from dbt.cli(["build"], context=context).stream()

# ==============================================================================
# 5. Power BI Reporting (Waiting for IDs) ⏳
# ==============================================================================
@asset(
    group_name="bi_reporting",
    compute_kind="powerbi",
    deps=[dbt_analytics]
)
def trigger_powerbi_refresh(context: AssetExecutionContext, config: RunConfig):
    """
    Triggers a refresh for a Power BI dataset after dbt pipeline completes.
    Configure the GROUP_ID and DATASET_ID with your Power BI Workspace and Dataset.
    """
    if config.dry_run:
        # Skip actual refresh when in dry-run mode
        context.log.warning("⚠️ DRY RUN MODE: Skipping Power BI Refresh.")
        return

    # Replace with your actual Power BI Workspace ID and Dataset ID below
    GROUP_ID = "3ee15055-7c74-4004-8668-666d78f4e8df"   # (Workspace ID)
    DATASET_ID = "69748f3b-4d47-48a3-9751-8433b4b1cc1c" # (Dataset ID)
    ACCESS_TOKEN = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6InJ0c0ZULWItN0x1WTdEVlllU05LY0lKN1ZuYyIsImtpZCI6InJ0c0ZULWItN0x1WTdEVlllU05LY0lKN1ZuYyJ9.eyJhdWQiOiJodHRwczovL2FuYWx5c2lzLndpbmRvd3MubmV0L3Bvd2VyYmkvYXBpIiwiaXNzIjoiaHR0cHM6Ly9zdHMud2luZG93cy5uZXQvODYzOGZmYjQtNGM4Mi00NmI5LTk3YjEtNWRiOGVkN2M1MzhiLyIsImlhdCI6MTc2NDI1NzIzNiwibmJmIjoxNzY0MjU3MjM2LCJleHAiOjE3NjQyNjI3MjksImFjY3QiOjAsImFjciI6IjEiLCJhaW8iOiJBVVFBdS84YUFBQUFqRGhJbnF5MTROeERFTDBvOVhzRURYWlN4Yk5PdkVKNVZTeXJLMmlTMW9Yb3ZaUU1KWUdBZE5LK0kyRThiejlYUFhyYUdTZlo2d1g2KytwUFF4bXN3QT09IiwiYW1yIjpbInB3ZCJdLCJhcHBpZCI6IjE4ZmJjYTE2LTIyMjQtNDVmNi04NWIwLWY3YmYyYjM5YjNmMyIsImFwcGlkYWNyIjoiMCIsImZhbWlseV9uYW1lIjoiU2hhbGFuIiwiZ2l2ZW5fbmFtZSI6IlNoYWltYSIsImlkdHlwIjoidXNlciIsImlwYWRkciI6IjEwNS4xOTYuMTcwLjI4IiwibmFtZSI6IlNoYWltYSBTaGFsYW4iLCJvaWQiOiJjZTRlYzFmYi01YTIwLTRhM2QtOWZhYi0zMWQ5MTVkY2E0YWQiLCJwdWlkIjoiMTAwMzIwMDBERDJCMjYyRiIsInJoIjoiMS5BVjhBdFA4NGhvSk11VWFYc1YyNDdYeFRpd2tBQUFBQUFBQUF3QUFBQUFBQUFBQVBBVnhmQUEuIiwic2NwIjoiQXBwLlJlYWQuQWxsIENhcGFjaXR5LlJlYWQuQWxsIENhcGFjaXR5LlJlYWRXcml0ZS5BbGwgQ29ubmVjdGlvbi5SZWFkLkFsbCBDb25uZWN0aW9uLlJlYWRXcml0ZS5BbGwgQ29udGVudC5DcmVhdGUgRGFzaGJvYXJkLlJlYWQuQWxsIERhc2hib2FyZC5SZWFkV3JpdGUuQWxsIERhdGFmbG93LlJlYWQuQWxsIERhdGFmbG93LlJlYWRXcml0ZS5BbGwgRGF0YXNldC5SZWFkLkFsbCBEYXRhc2V0LlJlYWRXcml0ZS5BbGwgR2F0ZXdheS5SZWFkLkFsbCBHYXRld2F5LlJlYWRXcml0ZS5BbGwgSXRlbS5FeGVjdXRlLkFsbCBJdGVtLkV4dGVybmFsRGF0YVNoYXJlLkFsbCBJdGVtLlJlYWRXcml0ZS5BbGwgSXRlbS5SZXNoYXJlLkFsbCBPbmVMYWtlLlJlYWQuQWxsIE9uZUxha2UuUmVhZFdyaXRlLkFsbCBQaXBlbGluZS5EZXBsb3kgUGlwZWxpbmUuUmVhZC5BbGwgUGlwZWxpbmUuUmVhZFdyaXRlLkFsbCBSZXBvcnQuUmVhZFdyaXRlLkFsbCBSZXBydC5SZWFkLkFsbCBTdG9yYWdlQWNjb3VudC5SZWFkLkFsbCBTdG9yYWdlQWNjb3VudC5SZWFkV3JpdGUuQWxsIFRhZy5SZWFkLkFsbCBUZW5hbnQuUmVhZC5BbGwgVGVuYW50LlJlYWRXcml0ZS5BbGwgVXNlclN0YXRlLlJlYWRXcml0ZS5BbGwgV29ya3NwYWNlLkdpdENvbW1pdC5BbGwgV29ya3NwYWNlLkdpdFVwZGF0ZS5BbGwgV29ya3NwYWNlLlJlYWQuQWxsIFdvcmtzcGFjZS5SZWFkV3JpdGUuQWxsIiwic2lkIjoiMDBhYmZmNTktZjY1Ny03NWUzLTE5NDctOTA2MTlhNjI5MWE0Iiwic3ViIjoiaElvZ0JRTUQ5VUVWTl82WHhtQWs2SHQ2Nm9JckRCR3ZGY0F1elVVSGZydyIsInRpZCI6Ijg2MzhmZmI0LTRjODItNDZiOS05N2IxLTVkYjhlZDdjNTM4YiIsInVuaXF1ZV9uYW1lIjoicy5zaGFsYW5AdHBzLmVkdS5zYSIsInVwbiI6InMuc2hhbGFuQHRwcy5lZHUuc2EiLCJ1dGkiOiIySW1GOUhxcTJFZTM0Ql9tVkZ0TkFBIiwidmVyIjoiMS4wIiwid2lkcyI6WyJiNzlmYmY0ZC0zZWY5LTQ2ODktODE0My03NmIxOTRlODU1MDkiXSwieG1zX2FjdF9mY3QiOiI1IDMiLCJ4bXNfZnRkIjoiMjJaZi1qNWlnbGJYRDZwXzBUQjBJVTdQOTN2MjBXQXkyM21IeWNFX1E4b0JjM2RsWkdWdVl5MWtjMjF6IiwieG1zX2lkcmVsIjoiMSAzMiIsInhtc19zdWJfZmN0IjoiMTYgMyJ9.ruHFpM0iNs73hshTX12Q5nEfe2AuD8KKpefOuDHVYLwPAcq9z-wMira_Gc9ZAU0jLDw-KL1BoXi1E8S4-qE1xBBuaPrprKtZhqCQBqXyWdtzmQlSE49bTPCbKNiUX1hUq20-ZtaC_ZtlB0d8yzCp8D2_VyaBQBwLnKfqTachpK---Cg8DBQInmfOfKV9xqI_B5ZvtDcZYZ8ny5IpjGXrwl-mR3i3F0gKvcd4MAPcDMPSIddSdG4UozTxEo22KFR76KcyRCPfFKn89ETB1yCbUXlXCIYjXA4_UwxHmteLIBrdLqBHG9PQrsgbhkv-ze3PFn6DTYQB8QJFVLggjQdGOg"            # Your Power BI Service Principal or token

    url = f"https://api.powerbi.com/v1.0/myorg/groups/{GROUP_ID}/datasets/{DATASET_ID}/refreshes"
    
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    context.log.info("🚀 Triggering refresh for Power BI Dataset...")

    try:
        # Simulate the refresh since an access token is required
        # Remove the below lines and uncomment the POST request lines to enable live refresh
        import time
        time.sleep(1)
        context.log.info("✅ Power BI Refresh Triggered Successfully (Simulated)!")
        
        # To actually trigger Power BI refresh, remove the comments below and ensure you have a valid token:
        # response = requests.post(url, headers=headers)
        # context.log.info(f"API Response: {response.status_code}")

    except Exception as e:
        # Log any connection errors
        context.log.error(f"❌ Connection Error: {str(e)}")
        raise e