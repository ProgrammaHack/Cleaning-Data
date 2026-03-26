# Data Cleaning and User Analytics Pipeline

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Processing-green)
![Status](https://img.shields.io/badge/Status-Completed-brightgreen)

---

## 📌 Overview

This project implements a complete data cleaning and preprocessing pipeline starting from a raw dataset (`dirty_dataset.csv`).

The objective is to transform inconsistent and noisy data into a clean, structured dataset suitable for analysis and machine learning.

---

## 🧭 Pipeline Overview



The pipeline performs:

* Data validation
* Text cleaning
* Type conversion
* Deduplication
* Feature engineering
* User scoring

---

## 📂 Project Structure

```bash
.
├── dirty_dataset.csv
├── clean_dataset_final.csv
├── pulizia_csv.py
└── README.md
```

---

## 🧼 Data Cleaning Process

The dataset contains multiple data quality issues such as invalid identifiers, noisy text, inconsistent formats, and missing values.

### Identifier Validation

The `user_id` column is validated using a UUID pattern.
Invalid, null, or malformed identifiers are removed to ensure data integrity.

---

### Text Normalization

Text fields are cleaned by:

* Removing noise (`NULL`, `n/a`, `xxx`)
* Removing special characters
* Normalizing whitespace
* Converting empty values to `NaN`

---

### 🌍 Data Standardization

Categorical values are standardized:

* Country values → `IT`
* Categories → `Tech`, `Home`, `Fashion`

This ensures consistency in grouping and analysis.

---

### 🔢 Type Conversion

Columns are converted to appropriate types:

* Numeric: `age`, `rating`, `reviews_count`
* Boolean: `returned`
* Invalid values are handled (e.g., negative age → removed)

---

### 💰 Purchase Amount Handling

The `purchase_amount` column is reconstructed to handle:

* Decimal commas (`"12,50"` → `12.50`)
* Special values (`"free"` → `0`)

A new column `is_free` is added to explicitly mark free transactions.

---

### 📅 Date Parsing and Validation

Dates are parsed from multiple formats into a unified datetime format.

Logical consistency is enforced by removing records where:

* `last_login < signup_date`

---

### 🔁 Deduplication

Duplicates are handled in two steps:

1. Exact duplicates removal
2. Fuzzy matching (via `rapidfuzz`)

A blocking strategy improves performance by grouping similar records before comparison.
The most complete record is retained.

---

## 🧠 Feature Engineering

New features are derived:

| Feature               | Description                |
| --------------------- | -------------------------- |
| days_since_signup     | Days since registration    |
| days_since_last_login | Days since last login      |
| is_active_user        | Active within last 30 days |

---

## ⚠️ Data Quality Analysis

Users with anomalous data are identified:

* Invalid or missing age
* Invalid email format
* Missing or non-numeric rating

These issues are stored in the `error_type` column.

---

## ⭐ User Scoring Model

A score (0–100) is computed based on:

* Purchase amount (40%)
* Login recency (30%)
* Number of reviews (20%)
* Rating (10%)

All variables are normalized before weighting.

---

## 📊 Bias Analysis

Missing values are analyzed across:

* Country
* Category


This helps detect non-random missing patterns and potential bias in the dataset.

---

## 📤 Output

```bash
clean_dataset_final.csv
```

The dataset is:

* Cleaned
* Standardized
* Deduplicated
* Enriched with features and scores

---

## ▶️ Execution

```bash
pip install pandas numpy rapidfuzz
python pulizia_csv.py
```

---

## 📈 Future Improvements

* Visualization of missing values (heatmaps)
* Machine learning models
* Automated ETL pipeline
* API-based validation

---

## 🧾 Conclusion

This project demonstrates a full data preprocessing workflow, transforming raw data into a reliable dataset ready for advanced analysis.

---

## 👨‍💻 Author

Developed as part of a Data Cleaning and Data Analysis exercise.
