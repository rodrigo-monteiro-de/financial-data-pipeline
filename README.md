# financial-data-pipeline
##Current Scope

This project currently supports brokerage notes following the SINACOR layout, which is widely adopted by Brazilian brokers such as Rico, XP, and Clear.

The parser was intentionally designed around this standard to ensure maintainability and consistent business rules. Support for additional proprietary 
layouts (e.g., alternative broker-specific formats) can be added through dedicated parsers in future iterations.

Financial data pipeline implementing a Medallion Architecture (Bronze/Silver/Gold) to ingest B3 brokerage notes, process data via Python,
 and deliver a dimensional model for portfolio analytics. 
 
 Local Data Lake implementation.
 
 Financial Data Pipeline Architecture:
 
 financial-data-pipeline/
│
├── Bronze
│   ├── PDF extraction
│   └── Raw text
│
├── Silver
│   ├── Transaction normalization
│   ├── Fee allocation
│   ├── Business rules
│   └── Data validation
│
├── Gold
│   ├── Fact trades
│   ├── Dim asset
│   ├── Dim broker
│   ├── Dim date
│   └── Portfolio metrics
│
├── Spark implementation (future)
│
├── dbt models (future)
│
└── LLM assistant over brokerage notes (future)
 
 
