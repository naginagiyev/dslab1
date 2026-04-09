## 1. Dataset Overview
- File name: `ibmchurn.csv`
- File size: 954.59 KB
- Rows: 7043
- Columns: 21
- Memory usage: 7.79 MB
- Missing values: 0 (0.00%)
- Duplicate rows: 0 (0.00%)
- First duplicate row indices (up to 3): None
- Column type breakdown: 12 categorical, 6 boolean, 1 id_like, 1 numeric_discrete, 1 numeric_continuous

### Column Summary
| Column           | Inferred Type      | Pandas Dtype   |   Missing Count | Missing %   |
|:-----------------|:-------------------|:---------------|----------------:|:------------|
| customerID       | id_like            | object         |               0 | 0.00%       |
| gender           | categorical        | object         |               0 | 0.00%       |
| SeniorCitizen    | boolean            | int64          |               0 | 0.00%       |
| Partner          | boolean            | object         |               0 | 0.00%       |
| Dependents       | boolean            | object         |               0 | 0.00%       |
| tenure           | numeric_discrete   | int64          |               0 | 0.00%       |
| PhoneService     | boolean            | object         |               0 | 0.00%       |
| MultipleLines    | categorical        | object         |               0 | 0.00%       |
| InternetService  | categorical        | object         |               0 | 0.00%       |
| OnlineSecurity   | categorical        | object         |               0 | 0.00%       |
| OnlineBackup     | categorical        | object         |               0 | 0.00%       |
| DeviceProtection | categorical        | object         |               0 | 0.00%       |
| TechSupport      | categorical        | object         |               0 | 0.00%       |
| StreamingTV      | categorical        | object         |               0 | 0.00%       |
| StreamingMovies  | categorical        | object         |               0 | 0.00%       |
| Contract         | categorical        | object         |               0 | 0.00%       |
| PaperlessBilling | boolean            | object         |               0 | 0.00%       |
| PaymentMethod    | categorical        | object         |               0 | 0.00%       |
| MonthlyCharges   | numeric_continuous | float64        |               0 | 0.00%       |
| TotalCharges     | categorical        | object         |               0 | 0.00%       |
| Churn            | boolean            | object         |               0 | 0.00%       |


## 2. Target Column Analysis
- Target column: `Churn`
- Task type: `binary-classification`
- Class imbalance level: moderate imbalance
- Minority class share: 26.54%
- Imbalance ratio (majority/minority): 2.77

### Class Distribution
| Class   |   Count | Percentage   |
|:--------|--------:|:-------------|
| No      |    5174 | 73.46%       |
| Yes     |    1869 | 26.54%       |
- Missing values in target: 0 (0.00%)


## 3. Per-Column Analysis

### customerID
- Flag: Likely an identifier column - deep analysis skipped.
- Unique count: 7043
- Unique ratio: 100.00%
- Sample values (up to 3): ['7590-VHVEG', '5575-GNVDE', '3668-QPYBK']

### gender
- Inferred type: `categorical`
- Pandas dtype: `object`
- Non-null count: 7043
- Missing: 0 (0.00%)
- Cardinality (unique): 2
- Mode: `Male`
- Least frequent value: `Female` (3488)

#### Top 10 Value Counts
| Value   |   Count | Percentage   |
|:--------|--------:|:-------------|
| Male    |    3555 | 50.48%       |
| Female  |    3488 | 49.52%       |

### SeniorCitizen
- Inferred type: `boolean`
- Detected boolean-like values: ['0', '1']
- Missing: 0 (0.00%)

#### Value Counts
|   Value |   Count | Percentage   |
|--------:|--------:|:-------------|
|       0 |    5901 | 83.79%       |
|       1 |    1142 | 16.21%       |
- True ratio: 0.1621

### Partner
- Inferred type: `boolean`
- Detected boolean-like values: ['No', 'Yes']
- Missing: 0 (0.00%)

#### Value Counts
| Value   |   Count | Percentage   |
|:--------|--------:|:-------------|
| No      |    3641 | 51.70%       |
| Yes     |    3402 | 48.30%       |
- True ratio: 0.4830

### Dependents
- Inferred type: `boolean`
- Detected boolean-like values: ['No', 'Yes']
- Missing: 0 (0.00%)

#### Value Counts
| Value   |   Count | Percentage   |
|:--------|--------:|:-------------|
| No      |    4933 | 70.04%       |
| Yes     |    2110 | 29.96%       |
- True ratio: 0.2996

### tenure
- Inferred type: `numeric_discrete`
- Pandas dtype: `int64`
- Non-null count: 7043
- Missing: 0 (0.00%)
- Unique values: 73
- Min: 0.0000
- Max: 72.0000
- Mean: 32.3711
- Median: 29.0000
- Mode: 1.0000
- Standard deviation: 24.5595
- Variance: 603.1681
- Skewness: 0.2395
- Kurtosis: -1.3872

#### Percentiles
| Percentile   |   Value |
|:-------------|--------:|
| 1th          |  1.0000 |
| 5th          |  1.0000 |
| 25th         |  9.0000 |
| 75th         | 55.0000 |
| 95th         | 72.0000 |
| 99th         | 72.0000 |
- IQR outliers: 0 (0.00%)
- Z-score outliers (|z| > 3): 0 (0.00%)
- Zero count: 11 (0.16%)

#### Value Counts
|   Value |   Count | %     |
|--------:|--------:|:------|
|  0.0000 |      11 | 0.16% |
|  1.0000 |     613 | 8.70% |
|  2.0000 |     238 | 3.38% |
|  3.0000 |     200 | 2.84% |
|  4.0000 |     176 | 2.50% |
|  5.0000 |     133 | 1.89% |
|  6.0000 |     110 | 1.56% |
|  7.0000 |     131 | 1.86% |
|  8.0000 |     123 | 1.75% |
|  9.0000 |     119 | 1.69% |
| 10.0000 |     116 | 1.65% |
| 11.0000 |      99 | 1.41% |
| 12.0000 |     117 | 1.66% |
| 13.0000 |     109 | 1.55% |
| 14.0000 |      76 | 1.08% |
| 15.0000 |      99 | 1.41% |
| 16.0000 |      80 | 1.14% |
| 17.0000 |      87 | 1.24% |
| 18.0000 |      97 | 1.38% |
| 19.0000 |      73 | 1.04% |
| 20.0000 |      71 | 1.01% |
| 21.0000 |      63 | 0.89% |
| 22.0000 |      90 | 1.28% |
| 23.0000 |      85 | 1.21% |
| 24.0000 |      94 | 1.33% |
| 25.0000 |      79 | 1.12% |
| 26.0000 |      79 | 1.12% |
| 27.0000 |      72 | 1.02% |
| 28.0000 |      57 | 0.81% |
| 29.0000 |      72 | 1.02% |
| 30.0000 |      72 | 1.02% |
| 31.0000 |      65 | 0.92% |
| 32.0000 |      69 | 0.98% |
| 33.0000 |      64 | 0.91% |
| 34.0000 |      65 | 0.92% |
| 35.0000 |      88 | 1.25% |
| 36.0000 |      50 | 0.71% |
| 37.0000 |      65 | 0.92% |
| 38.0000 |      59 | 0.84% |
| 39.0000 |      56 | 0.80% |
| 40.0000 |      64 | 0.91% |
| 41.0000 |      70 | 0.99% |
| 42.0000 |      65 | 0.92% |
| 43.0000 |      65 | 0.92% |
| 44.0000 |      51 | 0.72% |
| 45.0000 |      61 | 0.87% |
| 46.0000 |      74 | 1.05% |
| 47.0000 |      68 | 0.97% |
| 48.0000 |      64 | 0.91% |
| 49.0000 |      66 | 0.94% |
| 50.0000 |      68 | 0.97% |
| 51.0000 |      68 | 0.97% |
| 52.0000 |      80 | 1.14% |
| 53.0000 |      70 | 0.99% |
| 54.0000 |      68 | 0.97% |
| 55.0000 |      64 | 0.91% |
| 56.0000 |      80 | 1.14% |
| 57.0000 |      65 | 0.92% |
| 58.0000 |      67 | 0.95% |
| 59.0000 |      60 | 0.85% |
| 60.0000 |      76 | 1.08% |
| 61.0000 |      76 | 1.08% |
| 62.0000 |      70 | 0.99% |
| 63.0000 |      72 | 1.02% |
| 64.0000 |      80 | 1.14% |
| 65.0000 |      76 | 1.08% |
| 66.0000 |      89 | 1.26% |
| 67.0000 |      98 | 1.39% |
| 68.0000 |     100 | 1.42% |
| 69.0000 |      95 | 1.35% |
| 70.0000 |     119 | 1.69% |
| 71.0000 |     170 | 2.41% |
| 72.0000 |     362 | 5.14% |

### PhoneService
- Inferred type: `boolean`
- Detected boolean-like values: ['No', 'Yes']
- Missing: 0 (0.00%)

#### Value Counts
| Value   |   Count | Percentage   |
|:--------|--------:|:-------------|
| Yes     |    6361 | 90.32%       |
| No      |     682 | 9.68%        |
- True ratio: 0.9032

### MultipleLines
- Inferred type: `categorical`
- Pandas dtype: `object`
- Non-null count: 7043
- Missing: 0 (0.00%)
- Cardinality (unique): 3
- Mode: `No`
- Least frequent value: `No phone service` (682)

#### Top 10 Value Counts
| Value            |   Count | Percentage   |
|:-----------------|--------:|:-------------|
| No               |    3390 | 48.13%       |
| Yes              |    2971 | 42.18%       |
| No phone service |     682 | 9.68%        |

### InternetService
- Inferred type: `categorical`
- Pandas dtype: `object`
- Non-null count: 7043
- Missing: 0 (0.00%)
- Cardinality (unique): 3
- Mode: `Fiber optic`
- Least frequent value: `No` (1526)

#### Top 10 Value Counts
| Value       |   Count | Percentage   |
|:------------|--------:|:-------------|
| Fiber optic |    3096 | 43.96%       |
| DSL         |    2421 | 34.37%       |
| No          |    1526 | 21.67%       |

### OnlineSecurity
- Inferred type: `categorical`
- Pandas dtype: `object`
- Non-null count: 7043
- Missing: 0 (0.00%)
- Cardinality (unique): 3
- Mode: `No`
- Least frequent value: `No internet service` (1526)

#### Top 10 Value Counts
| Value               |   Count | Percentage   |
|:--------------------|--------:|:-------------|
| No                  |    3498 | 49.67%       |
| Yes                 |    2019 | 28.67%       |
| No internet service |    1526 | 21.67%       |

### OnlineBackup
- Inferred type: `categorical`
- Pandas dtype: `object`
- Non-null count: 7043
- Missing: 0 (0.00%)
- Cardinality (unique): 3
- Mode: `No`
- Least frequent value: `No internet service` (1526)

#### Top 10 Value Counts
| Value               |   Count | Percentage   |
|:--------------------|--------:|:-------------|
| No                  |    3088 | 43.84%       |
| Yes                 |    2429 | 34.49%       |
| No internet service |    1526 | 21.67%       |

### DeviceProtection
- Inferred type: `categorical`
- Pandas dtype: `object`
- Non-null count: 7043
- Missing: 0 (0.00%)
- Cardinality (unique): 3
- Mode: `No`
- Least frequent value: `No internet service` (1526)

#### Top 10 Value Counts
| Value               |   Count | Percentage   |
|:--------------------|--------:|:-------------|
| No                  |    3095 | 43.94%       |
| Yes                 |    2422 | 34.39%       |
| No internet service |    1526 | 21.67%       |

### TechSupport
- Inferred type: `categorical`
- Pandas dtype: `object`
- Non-null count: 7043
- Missing: 0 (0.00%)
- Cardinality (unique): 3
- Mode: `No`
- Least frequent value: `No internet service` (1526)

#### Top 10 Value Counts
| Value               |   Count | Percentage   |
|:--------------------|--------:|:-------------|
| No                  |    3473 | 49.31%       |
| Yes                 |    2044 | 29.02%       |
| No internet service |    1526 | 21.67%       |

### StreamingTV
- Inferred type: `categorical`
- Pandas dtype: `object`
- Non-null count: 7043
- Missing: 0 (0.00%)
- Cardinality (unique): 3
- Mode: `No`
- Least frequent value: `No internet service` (1526)

#### Top 10 Value Counts
| Value               |   Count | Percentage   |
|:--------------------|--------:|:-------------|
| No                  |    2810 | 39.90%       |
| Yes                 |    2707 | 38.44%       |
| No internet service |    1526 | 21.67%       |

### StreamingMovies
- Inferred type: `categorical`
- Pandas dtype: `object`
- Non-null count: 7043
- Missing: 0 (0.00%)
- Cardinality (unique): 3
- Mode: `No`
- Least frequent value: `No internet service` (1526)

#### Top 10 Value Counts
| Value               |   Count | Percentage   |
|:--------------------|--------:|:-------------|
| No                  |    2785 | 39.54%       |
| Yes                 |    2732 | 38.79%       |
| No internet service |    1526 | 21.67%       |

### Contract
- Inferred type: `categorical`
- Pandas dtype: `object`
- Non-null count: 7043
- Missing: 0 (0.00%)
- Cardinality (unique): 3
- Mode: `Month-to-month`
- Least frequent value: `One year` (1473)

#### Top 10 Value Counts
| Value          |   Count | Percentage   |
|:---------------|--------:|:-------------|
| Month-to-month |    3875 | 55.02%       |
| Two year       |    1695 | 24.07%       |
| One year       |    1473 | 20.91%       |

### PaperlessBilling
- Inferred type: `boolean`
- Detected boolean-like values: ['No', 'Yes']
- Missing: 0 (0.00%)

#### Value Counts
| Value   |   Count | Percentage   |
|:--------|--------:|:-------------|
| Yes     |    4171 | 59.22%       |
| No      |    2872 | 40.78%       |
- True ratio: 0.5922

### PaymentMethod
- Inferred type: `categorical`
- Pandas dtype: `object`
- Non-null count: 7043
- Missing: 0 (0.00%)
- Cardinality (unique): 4
- Mode: `Electronic check`
- Least frequent value: `Credit card (automatic)` (1522)

#### Top 10 Value Counts
| Value                     |   Count | Percentage   |
|:--------------------------|--------:|:-------------|
| Electronic check          |    2365 | 33.58%       |
| Mailed check              |    1612 | 22.89%       |
| Bank transfer (automatic) |    1544 | 21.92%       |
| Credit card (automatic)   |    1522 | 21.61%       |

### MonthlyCharges
- Inferred type: `numeric_continuous`
- Pandas dtype: `float64`
- Non-null count: 7043
- Missing: 0 (0.00%)
- Unique values: 1585
- Min: 18.2500
- Max: 118.7500
- Mean: 64.7617
- Median: 70.3500
- Mode: 20.0500
- Standard deviation: 30.0900
- Variance: 905.4109
- Skewness: -0.2205
- Kurtosis: -1.2572

#### Percentiles
| Percentile   |    Value |
|:-------------|---------:|
| 1th          |  19.2000 |
| 5th          |  19.6500 |
| 25th         |  35.5000 |
| 75th         |  89.8500 |
| 95th         | 107.4000 |
| 99th         | 114.7290 |
- IQR outliers: 0 (0.00%)
- Z-score outliers (|z| > 3): 0 (0.00%)
- Zero count: 0 (0.00%)

### TotalCharges
- Inferred type: `categorical`
- Pandas dtype: `object`
- Non-null count: 7043
- Missing: 0 (0.00%)
- Cardinality (unique): 6531
- Mode: ` `
- Least frequent value: `29.85` (1)

#### Top 10 Value Counts
| Value   |   Count | Percentage   |
|:--------|--------:|:-------------|
|         |      11 | 0.16%        |
| 20.2    |      11 | 0.16%        |
| 19.75   |       9 | 0.13%        |
| 20.05   |       8 | 0.11%        |
| 19.9    |       8 | 0.11%        |
| 19.65   |       8 | 0.11%        |
| 45.3    |       7 | 0.10%        |
| 19.55   |       7 | 0.10%        |
| 20.15   |       6 | 0.09%        |
| 20.25   |       6 | 0.09%        |
- Showing top 10 of 6531 unique values.

### Churn
- Inferred type: `boolean`
- Detected boolean-like values: ['No', 'Yes']
- Missing: 0 (0.00%)

#### Value Counts
| Value   |   Count | Percentage   |
|:--------|--------:|:-------------|
| No      |    5174 | 73.46%       |
| Yes     |    1869 | 26.54%       |
- True ratio: 0.2654

## 4. Missing Values
- Total missing cells: 0
- No missing values detected in any column.
- Columns with 0% missing: customerID, gender, SeniorCitizen, Partner, Dependents, tenure, PhoneService, MultipleLines, InternetService, OnlineSecurity, OnlineBackup, DeviceProtection, TechSupport, StreamingTV, StreamingMovies, Contract, PaperlessBilling, PaymentMethod, MonthlyCharges, TotalCharges, Churn
- No high co-missing pairs (>50%) found.


## 5. Correlations
### Numeric vs Numeric (Pearson)
- No strong numeric correlations found.

### Categorical vs Categorical (Cramer's V)
| Feature A        | Feature B        |   Cramer's V | Strength   |
|:-----------------|:-----------------|-------------:|:-----------|
| StreamingTV      | StreamingMovies  |       0.7710 | Strong     |
| DeviceProtection | StreamingMovies  |       0.7360 | Strong     |
| DeviceProtection | StreamingTV      |       0.7336 | Strong     |
| OnlineSecurity   | TechSupport      |       0.7330 | Strong     |
| DeviceProtection | TechSupport      |       0.7264 | Strong     |
| InternetService  | OnlineSecurity   |       0.7244 | Strong     |
| InternetService  | TechSupport      |       0.7228 | Strong     |
| OnlineBackup     | TechSupport      |       0.7197 | Strong     |
| OnlineBackup     | DeviceProtection |       0.7190 | Strong     |
| OnlineSecurity   | OnlineBackup     |       0.7183 | Strong     |
| OnlineSecurity   | DeviceProtection |       0.7172 | Strong     |
| InternetService  | StreamingTV      |       0.7170 | Strong     |
| TechSupport      | StreamingMovies  |       0.7162 | Strong     |
| TechSupport      | StreamingTV      |       0.7162 | Strong     |
| InternetService  | StreamingMovies  |       0.7159 | Strong     |
| OnlineBackup     | StreamingTV      |       0.7146 | Strong     |
| OnlineBackup     | StreamingMovies  |       0.7136 | Strong     |
| OnlineSecurity   | StreamingMovies  |       0.7081 | Strong     |
| OnlineSecurity   | StreamingTV      |       0.7077 | Strong     |
| InternetService  | OnlineBackup     |       0.7071 | Strong     |
| InternetService  | DeviceProtection |       0.7070 | Strong     |
| MultipleLines    | InternetService  |       0.3964 | Weak       |
| TechSupport      | Contract         |       0.3306 | Weak       |
| InternetService  | PaymentMethod    |       0.3125 | Weak       |
| TechSupport      | PaymentMethod    |       0.3062 | Weak       |
| OnlineSecurity   | PaymentMethod    |       0.3043 | Weak       |
| OnlineSecurity   | Contract         |       0.3009 | Weak       |

### Feature vs Target
| Feature          | Metric         |   Value |
|:-----------------|:---------------|--------:|
| Contract         | Cramer's V     |  0.4098 |
| tenure           | Point-Biserial | -0.3522 |
| OnlineSecurity   | Cramer's V     |  0.3470 |
| TechSupport      | Cramer's V     |  0.3425 |
| InternetService  | Cramer's V     |  0.3220 |
| PaymentMethod    | Cramer's V     |  0.3027 |
| OnlineBackup     | Cramer's V     |  0.2919 |
| DeviceProtection | Cramer's V     |  0.2811 |
| StreamingMovies  | Cramer's V     |  0.2304 |
| StreamingTV      | Cramer's V     |  0.2299 |
| MonthlyCharges   | Point-Biserial |  0.1934 |
| SeniorCitizen    | Point-Biserial |  0.1509 |
| MultipleLines    | Cramer's V     |  0.0364 |
| gender           | Cramer's V     |  0.0000 |
| TotalCharges     | Cramer's V     |  0.0000 |


## 6. Outlier Summary
| Column         |   IQR Outlier Count | IQR Outlier %   |   Z-score Outlier Count | Z-score Outlier %   |
|:---------------|--------------------:|:----------------|------------------------:|:--------------------|
| tenure         |                   0 | 0.00%           |                       0 | 0.00%               |
| MonthlyCharges |                   0 | 0.00%           |                       0 | 0.00%               |


## 7. Data Quality Warnings
### Cardinality
1. High cardinality in 'TotalCharges' (6531 unique values).

### Class Imbalance
2. Class imbalance in target 'Churn': moderate imbalance (minority class is 26.54%, ratio=2.77).

### Other
3. Column 'TotalCharges' appears numeric-like in string format (parse success ratio: 99.84%).
