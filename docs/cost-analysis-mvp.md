# AWS Cost Analysis - Financial Data Pipeline MVP

# Cost Analysis – MVP

## Objective

Estimate the monthly infrastructure cost for the **Financial Data Pipeline MVP** before deployment on AWS. The estimates below are based on expected usage for a small production-ready environment with room for moderate growth.

## Assumptions

- AWS Region: **US East (N. Virginia)**
- Daily batch processing
- Bronze layer stores raw TXT files
- Silver layer stores optimized Parquet files
- Gold layer is generated with dbt
- Athena is used for analytical queries
- Costs are estimates and may vary according to actual usage

## Estimated Monthly Costs

| Service | Configuration | Monthly Cost |
|----------|---------------|-------------:|
| Amazon S3 | 10 GB storage, 1,000 PUT requests, 5,000 GET requests | **US$ 0.24** |
| Amazon Athena | 100 queries/month, 1 GB scanned per query | **US$ 0.49** |
| AWS Glue | 2 DPUs, ~150 minutes/month (Spark ETL) | **US$ 2.20** |
| **Total Estimated Cost** | | **US$ 2.93/month** |

## Key Assumptions

### Amazon S3
- 10 GB of Standard Storage
- 1,000 monthly PUT/COPY/POST/LIST requests
- 5,000 monthly GET requests
- No S3 Select usage
- No significant data transfer outside the AWS Region

### Amazon Athena
- 100 SQL queries per month
- Average of 1 GB scanned per query
- Serverless pricing model (pay per data scanned)

### AWS Glue
- Spark ETL jobs only
- 2 DPUs allocated
- Approximately 150 minutes of execution per month
- No Python Shell jobs
- No Interactive Sessions

## Estimated Architecture

```text
TXT Files
    │
    ▼
Amazon S3 (Bronze)
    │
    ▼
AWS Glue (PySpark ETL)
    │
    ▼
Amazon S3 (Silver - Parquet)
    │
    ▼
dbt (Gold)
    │
    ▼
Amazon Athena
```

## Notes

These estimates represent the initial MVP and were intentionally sized with reasonable growth in mind rather than current usage. The architecture can scale by increasing storage, query volume, and ETL processing time as the project evolves.