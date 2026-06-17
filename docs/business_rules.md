# Business Rules

## Overview

This document describes the business rules applied during the transformation of brokerage notes from the Bronze layer into the Silver layer.

The objective is to ensure consistency, traceability, and reproducibility of all financial calculations and data transformations performed by the pipeline.

---

# BR001 - Brokerage Note Granularity

A brokerage note may contain one or multiple asset transactions.

Each transaction extracted from a brokerage note is represented as a separate record in the Silver layer.

Example:

| Brokerage Note | Asset         |
| -------------- | ------------- |
| Note A         | KLABIN S/A PN |
| Note A         | RECR11        |
| Note A         | PETR4         |

Result:

Three transaction records are generated from a single brokerage note.

---

# BR002 - Source File Traceability

Every transaction must preserve the source brokerage note from which it was extracted.

Field:

```text
source_file
```

Purpose:

* Data lineage
* Auditability
* Cost allocation calculations
* Validation against original documents

---

# BR003 - Asset Name Preservation

Asset descriptions are preserved as provided by the brokerage note.

Normalization rules:

* Leading spaces are removed
* Trailing spaces are removed
* Multiple consecutive spaces are reduced to a single space

Examples:

| Original                                 |
| ---------------------------------------- |
| KLABIN S/A          PN                   |
| FII REC RECE          RECR11          CI |

Becomes:

| Normalized             |
| ---------------------- |
| KLABIN S/A PN          |
| FII REC RECE RECR11 CI |

No ticker inference or asset classification is performed in the Silver layer.

---

# BR004 - Gross Transaction Value

The gross transaction value represents the financial value of the transaction before fees and taxes.

Formula:

```text
gross_value = quantity × unit_price
```

Example:

```text
Quantity = 10
Unit Price = 3.73

Gross Value = 37.30
```

---

# BR005 - Transaction Direction

Transaction direction is determined using the brokerage note indicators.

Values:

| Indicator | Operation |
| --------- | --------- |
| D         | Buy       |
| C         | Sell      |

Stored values:

```text
B = Buy
S = Sell
```

---

# BR006 - Transaction Weight

When a brokerage note contains multiple assets, costs must be allocated proportionally.

The transaction weight represents the participation of each asset in the total value of the note.

Formula:

```text
weight = gross_value / total_note_gross_value
```

Example:

```text
Asset A = 100
Asset B = 900

Total = 1000

Weight A = 0.10
Weight B = 0.90
```

---

# BR007 - Settlement Fee Allocation

Settlement fees are allocated proportionally according to transaction weight.

Formula:

```text
allocated_settlement_fee =
settlement_fee × weight
```

---

# BR008 - Emoluments Allocation

Exchange emoluments are allocated proportionally according to transaction weight.

Formula:

```text
allocated_emoluments =
emoluments × weight
```

---

# BR009 - Brokerage Fee Allocation

Brokerage fees are allocated proportionally according to transaction weight.

Formula:

```text
allocated_brokerage_fee =
brokerage_fee × weight
```

---

# BR010 - Asset Transfer Fee Allocation

Asset transfer fees are allocated proportionally according to transaction weight.

Formula:

```text
allocated_asset_transfer_fee =
asset_transfer_fee × weight
```

---

# BR011 - Total Fee Allocation

The total allocated fee for a transaction is calculated as the sum of all allocated costs.

Formula:

```text
allocated_total_fees =
allocated_settlement_fee
+ allocated_emoluments
+ allocated_brokerage_fee
+ allocated_asset_transfer_fee
```

---

# BR012 - Silver Layer Scope

The Silver layer is responsible for:

* Parsing brokerage notes
* Standardizing fields
* Normalizing asset descriptions
* Allocating transaction costs
* Preserving source traceability

The Silver layer is NOT responsible for:

* Ticker standardization
* Asset classification
* Star schema modeling
* Financial analytics
* Portfolio calculations

These responsibilities belong to the Gold layer.

---

# Future Gold Layer Rules

The following rules will be implemented in future project phases:

* BR101 - Asset Dimension
* BR102 - Brokerage Dimension
* BR103 - Date Dimension
* BR104 - Fact Transactions
* BR105 - Portfolio Analytics
* BR106 - Investment Performance Metrics
