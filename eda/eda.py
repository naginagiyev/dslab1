# imports
import os
import re
import csv
import warnings
import numpy as np
import pandas as pd
from typing import Any
from pathlib import Path
from tabulate import tabulate
from datetime import timedelta
from itertools import combinations
from config import readers as externalReaders, allowedTaskTypes
from scipy.stats import chi2_contingency as chi2Contingency, kurtosis, pointbiserialr, skew, zscore

class EDA:
    # initialze the class
    def __init__(self, inputPath: str, targetCol: str, taskType: str):
        self.inputPath = inputPath

        # get the target column
        if targetCol is None or not str(targetCol).strip():
            raise ValueError("targetCol is required and cannot be empty.")
        self.targetCol = str(targetCol).strip()
        if taskType not in allowedTaskTypes:
            raise ValueError(
                "taskType must be one of: "
                "binary-classification, regression, multi-class-classification, "
                "time-series, clustering, anomaly-detection."
            )
        self.taskType = taskType

        # create the output path
        inputObj = Path(inputPath)
        self.outputPath = str(inputObj.with_name(f"{inputObj.stem}eda.md"))

        # initialize the dataframe
        self.df: pd.DataFrame | None = None
        # initialize the column types
        self.colTypes: dict[str, str] = {}
        # initialize the warnings
        self.warnings: list[str] = []
        # initialize the report sections
        self.reportSections: list[str] = []
        # initialize the outlier statistics
        self.outlierStats: dict[str, dict[str, float]] = {}

    # the sections that will be run and written to the report
    def run(self) -> str:
        # load the data and get the types
        self.loadData()
        self.inferTypes()

        # main sections of the report
        self.reportSections.append(self.sectionOverview())
        self.reportSections.append(self.sectionTarget())
        self.reportSections.append(self.sectionColumns())
        self.reportSections.append(self.sectionMissing())
        self.reportSections.append(self.sectionCorrelations())
        self.reportSections.append(self.sectionOutliers())
        self.reportSections.append(self.sectionWarnings())

        # write the report into an .md file
        self.writeReport()
        return self.outputPath

    # read the data and confirm its completeness securely
    def loadData(self) -> None:
        ext = Path(self.inputPath).suffix.lower()
        df: pd.DataFrame | None = None

        if ext in {".csv", ".tsv"}:
            df = self.readDelimited()
        elif ext in externalReaders:
            df = externalReaders[ext](self.inputPath)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")

        if df is None or df.empty:
            raise ValueError("Loaded dataframe is empty.")

        if df.shape[1] == 0:
            raise ValueError("Loaded dataframe has no columns.")

        if all(df[col].isna().all() for col in df.columns):
            raise ValueError("All columns are fully missing.")

        if self.targetCol not in df.columns:
            raise ValueError(f"Target column '{self.targetCol}' was not found in the dataset.")

        self.df = df

    # a function to define what is the seperator in the dataset 
    def readDelimited(self, sampleSize: int = 4096) -> pd.DataFrame:
        delimiter = None
        ext = Path(self.inputPath).suffix.lower()

        if ext == ".tsv":
            delimiter = "\t"
        else:
            try:
                with open(self.inputPath, "r", encoding="utf-8") as file:
                    sample = file.read(sampleSize)
                    delimiter = csv.Sniffer().sniff(sample).delimiter
            except Exception:
                delimiter = None

        readKwargs = {"engine": "python", "sep": delimiter if delimiter is not None else None}
        try:
            return pd.read_csv(self.inputPath, encoding="utf-8", **readKwargs)
        except UnicodeDecodeError:
            return pd.read_csv(self.inputPath, encoding="latin-1", **readKwargs)

    # a function to decide what is the real type of the columns in the dataset
    def inferTypes(self) -> None:
        if self.df is None:
            raise ValueError("Data is not loaded.")

        df = self.df
        nRows = len(df)

        # iterate through the columns and decide the type
        for col in df.columns:
            series = df[col]
            nonNull = series.dropna()
            nonNullCount = len(nonNull)
            uniqueCount = nonNull.nunique(dropna=True)
            uniqueRatio = (uniqueCount / nRows) if nRows else 0.0

            if nonNullCount == 0:
                self.colTypes[col] = "categorical"
                continue

            if nRows >= 200:
                if uniqueRatio >= 0.98:
                    self.colTypes[col] = "id_like"
                    continue
            else:
                if uniqueCount == nonNullCount and nonNullCount >= 10:
                    self.colTypes[col] = "id_like"
                    continue

            convertedNumeric = self.tryConvertStringNumeric(col)
            if convertedNumeric:
                series = self.df[col]
                nonNull = series.dropna()
                nonNullCount = len(nonNull)
                uniqueCount = nonNull.nunique(dropna=True)
                uniqueRatio = (uniqueCount / nRows) if nRows else 0.0

            if self.isBooleanSeries(nonNull):
                self.colTypes[col] = "boolean"
                continue

            if pd.api.types.is_datetime64_any_dtype(series):
                self.colTypes[col] = "datetime"
                continue

            if pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series):
                if self.datetimeParseSuccessRatio(nonNull) > 0.80:
                    self.colTypes[col] = "datetime"
                    continue
                avgWords = self.averageWordCount(nonNull)
                if nRows >= 200:
                    if avgWords > 3 and uniqueRatio >= 0.40:
                        self.colTypes[col] = "text"
                        continue
                else:
                    if avgWords > 3 and uniqueCount >= 20:
                        self.colTypes[col] = "text"
                        continue
                if nonNull.map(type).nunique() > 1:
                    self.addWarning(f"Mixed types detected in column '{col}'. Treated as categorical.")
                self.colTypes[col] = "categorical"
                continue

            if pd.api.types.is_numeric_dtype(series):
                if nRows >= 200:
                    isDiscrete = uniqueRatio <= 0.05
                else:
                    isDiscrete = uniqueCount <= 15
                if isDiscrete:
                    self.colTypes[col] = "numeric_discrete"
                else:
                    self.colTypes[col] = "numeric_continuous"
                continue

            self.colTypes[col] = "categorical"

    # overview section and columns summary table
    def sectionOverview(self) -> str:
        if self.df is None:
            return "## 1. Dataset Overview\n\nNo data loaded.\n"

        df = self.df
        fileSize = os.path.getsize(self.inputPath) if os.path.exists(self.inputPath) else 0
        memoryUsage = int(df.memory_usage(deep=True).sum())
        missingCount = int(df.isna().sum().sum())
        totalCells = int(df.shape[0] * df.shape[1])
        missingPct = self.percent(missingCount, totalCells)

        duplicateMask = df.duplicated()
        duplicateCount = int(duplicateMask.sum())
        duplicatePct = self.percent(duplicateCount, len(df))
        duplicateIndices = df.index[duplicateMask].tolist()[:3]

        typeBreakdown = pd.Series(self.colTypes).value_counts().to_dict()
        typeLine = ", ".join(f"{v} {k}" for k, v in typeBreakdown.items()) if typeBreakdown else "N/A"

        summaryRows: list[list[Any]] = []
        for col in df.columns:
            miss = int(df[col].isna().sum())
            summaryRows.append(
                [
                    col,
                    self.colTypes.get(col, "unknown"),
                    str(df[col].dtype),
                    miss,
                    f"{self.percent(miss, len(df)):.2f}%",
                ]
            )

        section = [
            "## 1. Dataset Overview",
            f"- File name: `{Path(self.inputPath).name}`",
            f"- File size: {self.formatBytes(fileSize)}",
            f"- Rows: {len(df)}",
            f"- Columns: {df.shape[1]}",
            f"- Memory usage: {self.formatBytes(memoryUsage)}",
            f"- Missing values: {missingCount} ({missingPct:.2f}%)",
            f"- Duplicate rows: {duplicateCount} ({duplicatePct:.2f}%)",
            f"- First duplicate row indices (up to 3): {duplicateIndices if duplicateIndices else 'None'}",
            f"- Column type breakdown: {typeLine}",
            "",
            "### Column Summary",
            self.mdTable(
                summaryRows,
                ["Column", "Inferred Type", "Pandas Dtype", "Missing Count", "Missing %"],
            ),
            "",
        ]
        return "\n".join(section)

    # target column analysis
    def sectionTarget(self) -> str:
        # make sure the dataframe is loaded
        if self.df is None:
            return ""

        target = self.df[self.targetCol]
        taskType = self.taskType
        nonNull = target.dropna()
        missingCount = int(target.isna().sum())
        missingPct = self.percent(missingCount, len(target))

        section = ["## 2. Target Column Analysis", f"- Target column: `{self.targetCol}`", f"- Task type: `{taskType}`"]

        # make sure the target column has more than one unique value
        if nonNull.nunique(dropna=True) <= 1:
            self.addWarning("Target column has only one unique non-null value.")

        # check the imbalance of the target column
        if taskType in {"binary-classification", "multi-class-classification", "clustering", "anomaly-detection"}:
            counts = nonNull.value_counts(dropna=True)
            total = int(counts.sum())
            classRows = [[idx, int(val), f"{self.percent(int(val), total):.2f}%"] for idx, val in counts.items()]

            if len(counts) > 0:
                minCount = int(counts.min())
                maxCount = int(counts.max())
                minorityRatio = (minCount / total) if total else 0.0
                imbalanceRatio = (maxCount / minCount) if minCount else np.inf
                imbalanceLevel = self.classImbalanceLevel(imbalanceRatio)

                section.extend(
                    [
                        f"- Class imbalance level: {imbalanceLevel}",
                        f"- Minority class share: {minorityRatio * 100:.2f}%",
                        f"- Imbalance ratio (majority/minority): {imbalanceRatio:.2f}",
                    ]
                )

                if imbalanceLevel in {"moderate imbalance", "strong imbalance", "very strong imbalance"}:
                    self.addWarning(
                        f"Class imbalance in target '{self.targetCol}': {imbalanceLevel} "
                        f"(minority class is {minorityRatio * 100:.2f}%, ratio={imbalanceRatio:.2f})."
                    )

            section.extend(
                [
                    "",
                    "### Class Distribution",
                    self.mdTable(classRows, ["Class", "Count", "Percentage"]),
                    f"- Missing values in target: {missingCount} ({missingPct:.2f}%)",
                ]
            )
        elif taskType in {"regression", "time-series"}:
            numericTarget = pd.to_numeric(nonNull, errors="coerce").dropna()
            q1 = float(numericTarget.quantile(0.25)) if len(numericTarget) else 0.0
            q3 = float(numericTarget.quantile(0.75)) if len(numericTarget) else 0.0
            iqr = q3 - q1
            lower = q1 - (1.5 * iqr)
            upper = q3 + (1.5 * iqr)
            outlierCount = int(((numericTarget < lower) | (numericTarget > upper)).sum())
            statsRows = [
                ["count", float(numericTarget.count())],
                ["mean", float(numericTarget.mean()) if len(numericTarget) else np.nan],
                ["median", float(numericTarget.median()) if len(numericTarget) else np.nan],
                ["std", float(numericTarget.std()) if len(numericTarget) > 1 else np.nan],
                ["min", float(numericTarget.min()) if len(numericTarget) else np.nan],
                ["max", float(numericTarget.max()) if len(numericTarget) else np.nan],
                ["skewness", float(skew(numericTarget, nan_policy="omit")) if len(numericTarget) > 2 else np.nan],
                ["kurtosis", float(kurtosis(numericTarget, nan_policy="omit")) if len(numericTarget) > 3 else np.nan],
            ]
            pctRows = [
                ["5th", float(numericTarget.quantile(0.05)) if len(numericTarget) else np.nan],
                ["25th", q1],
                ["75th", q3],
                ["95th", float(numericTarget.quantile(0.95)) if len(numericTarget) else np.nan],
            ]
            section.extend(
                [
                    "",
                    "### Target Statistics",
                    self.mdTable(statsRows, ["Metric", "Value"]),
                    "",
                    "### Target Percentiles",
                    self.mdTable(pctRows, ["Percentile", "Value"]),
                    f"- IQR outlier count: {outlierCount}",
                    f"- Missing values in target: {missingCount} ({missingPct:.2f}%)",
                ]
            )
        else:
            section.append("- Target analysis summary is limited for this task type.")
            section.append(f"- Missing values in target: {missingCount} ({missingPct:.2f}%)")

        section.append("")
        return "\n".join(section)

    # individual column analysis
    def sectionColumns(self) -> str:
        if self.df is None:
            return "## 3. Per-Column Analysis\n\nNo data loaded.\n"

        # iterate over all columns and analyze them
        sectionParts = ["## 3. Per-Column Analysis"]
        for col in self.df.columns:
            colType = self.colTypes.get(col, "categorical")
            if colType in {"numeric_continuous", "numeric_discrete"}:
                sectionParts.append(self.analyzeNumeric(col))
            elif colType == "categorical":
                sectionParts.append(self.analyzeCategorical(col))
            elif colType == "boolean":
                sectionParts.append(self.analyzeBoolean(col))
            elif colType == "datetime":
                sectionParts.append(self.analyzeDatetime(col))
            elif colType == "text":
                sectionParts.append(self.analyzeText(col))
            elif colType == "id_like":
                sectionParts.append(self.analyzeId(col))
            else:
                sectionParts.append(self.analyzeCategorical(col))

        return "\n\n".join(sectionParts)

    # function to specifically analyze numeric columns
    def analyzeNumeric(self, col: str) -> str:
        # make sure the dataframe is loaded
        if self.df is None:
            return f"### {col}\n\nNo data loaded."

        rawSeries = self.df[col]
        series = pd.to_numeric(rawSeries, errors="coerce")
        nonNull = series.dropna()
        totalRows = len(rawSeries)
        nonNullCount = int(nonNull.count())
        missingCount = int(rawSeries.isna().sum())
        missingPct = self.percent(missingCount, totalRows)
        uniqueCount = int(nonNull.nunique(dropna=True))

        # make sure not all values are missing
        if nonNullCount == 0:
            self.addWarning(f"Column '{col}' is 100% missing and numeric statistics were skipped.")
            return (
                f"### {col}\n"
                f"- Inferred type: `{self.colTypes.get(col, 'unknown')}`\n"
                f"- Pandas dtype: `{rawSeries.dtype}`\n"
                f"- Missing: {missingCount} ({missingPct:.2f}%)\n"
                "- All values are missing.\n"
            )

        # mode of the column
        modeSeries = nonNull.mode(dropna=True)
        modeValue = modeSeries.iloc[0] if not modeSeries.empty else np.nan

        # quantiles of the column
        q1 = float(nonNull.quantile(0.25))
        q3 = float(nonNull.quantile(0.75))
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        # IQR outliers of the column
        iqrMask = (nonNull < lower) | (nonNull > upper)
        iqrOutliers = int(iqrMask.sum())
        iqrPct = self.percent(iqrOutliers, nonNullCount)

        # Z-score outliers of the column
        if nonNullCount > 2:
            zscores = pd.Series(zscore(nonNull, nan_policy="omit"), index=nonNull.index)
            zOutliers = int((zscores.abs() > 3).sum())
        else:
            zOutliers = 0
        zPct = self.percent(zOutliers, nonNullCount)

        # skew and kurtosis of the column
        skewVal = float(skew(nonNull, nan_policy="omit")) if nonNullCount > 2 else np.nan
        kurtVal = float(kurtosis(nonNull, nan_policy="omit")) if nonNullCount > 3 else np.nan

        if not np.isnan(skewVal):
            if abs(skewVal) > 2:
                self.addWarning(f"Severe skew in '{col}' (skew={skewVal:.4f}).")
            elif abs(skewVal) > 1:
                self.addWarning(f"High skew in '{col}' (skew={skewVal:.4f}).")
        if iqrPct > 5:
            self.addWarning(f"Outliers above 5% in '{col}' by IQR method ({iqrPct:.2f}%).")

        self.outlierStats[col] = {
            "iqr_count": float(iqrOutliers),
            "iqrPct": float(iqrPct),
            "z_count": float(zOutliers),
            "zPct": float(zPct),
        }

        percentiles = [0.01, 0.05, 0.25, 0.75, 0.95, 0.99]
        percentileRows = [[f"{int(p * 100)}th", float(nonNull.quantile(p))] for p in percentiles]

        zeroCount = int((nonNull == 0).sum())
        zeroPct = self.percent(zeroCount, nonNullCount)
        negativeCount = int((nonNull < 0).sum())
        negativePct = self.percent(negativeCount, nonNullCount)

        lines = [
            f"### {col}",
            f"- Inferred type: `{self.colTypes.get(col, 'unknown')}`",
            f"- Pandas dtype: `{rawSeries.dtype}`",
            f"- Non-null count: {nonNullCount}",
            f"- Missing: {missingCount} ({missingPct:.2f}%)",
            f"- Unique values: {uniqueCount}",
            f"- Min: {float(nonNull.min()):.4f}",
            f"- Max: {float(nonNull.max()):.4f}",
            f"- Mean: {float(nonNull.mean()):.4f}",
            f"- Median: {float(nonNull.median()):.4f}",
            f"- Mode: {float(modeValue):.4f}" if pd.notna(modeValue) else "- Mode: N/A",
            f"- Standard deviation: {float(nonNull.std()):.4f}" if nonNullCount > 1 else "- Standard deviation: N/A",
            f"- Variance: {float(nonNull.var()):.4f}" if nonNullCount > 1 else "- Variance: N/A",
            f"- Skewness: {skewVal:.4f}" if not np.isnan(skewVal) else "- Skewness: N/A",
            f"- Kurtosis: {kurtVal:.4f}" if not np.isnan(kurtVal) else "- Kurtosis: N/A",
            "",
            "#### Percentiles",
            self.mdTable(percentileRows, ["Percentile", "Value"]),
            f"- IQR outliers: {iqrOutliers} ({iqrPct:.2f}%)",
            f"- Z-score outliers (|z| > 3): {zOutliers} ({zPct:.2f}%)",
            f"- Zero count: {zeroCount} ({zeroPct:.2f}%)",
        ]

        # negative values of the column
        if negativeCount > 0:
            lines.append(f"- Negative count: {negativeCount} ({negativePct:.2f}%)")

        # value counts of the column
        if self.colTypes.get(col) == "numeric_discrete":
            valueCounts = (
                nonNull.value_counts(dropna=True)
                .sort_index()
                .rename_axis("Value")
                .reset_index(name="Count")
            )
            rows = [
                [row["Value"], int(row["Count"]), f"{self.percent(int(row['Count']), nonNullCount):.2f}%"]
                for _, row in valueCounts.iterrows()
            ]
            lines.extend(["", "#### Value Counts", self.mdTable(rows, ["Value", "Count", "%"])])

        return "\n".join(lines)

    # function to specifically analyze categorical columns
    def analyzeCategorical(self, col: str) -> str:
        # make sure the dataframe is loaded
        if self.df is None:
            return f"### {col}\n\nNo data loaded."

        # get some statistics about the categorical column  like 
        # non-null count, missing count, unique count, mode, least frequent value, top rows
        series = self.df[col]
        nonNull = series.dropna().astype(str)
        totalRows = len(series)
        nonNullCount = int(nonNull.count())
        missingCount = int(series.isna().sum())
        missingPct = self.percent(missingCount, totalRows)
        uniqueCount = int(nonNull.nunique(dropna=True))

        # check if the unique count is greater than 50
        if uniqueCount > 50:
            self.addWarning(f"High cardinality in '{col}' ({uniqueCount} unique values).")
        # check if the unique count is equal to the total rows
        if uniqueCount == totalRows and totalRows > 0:
            self.addWarning(f"Column '{col}' appears identifier-like (cardinality equals rows).")

        vcDesc = nonNull.value_counts(dropna=True)
        vcAsc = nonNull.value_counts(dropna=True, ascending=True)
        modeValue = vcDesc.index[0] if not vcDesc.empty else "N/A"
        leastValue = vcAsc.index[0] if not vcAsc.empty else "N/A"
        leastCount = int(vcAsc.iloc[0]) if not vcAsc.empty else 0

        top10 = vcDesc.head(10)
        topRows = [[idx, int(cnt), f"{self.percent(int(cnt), nonNullCount):.2f}%"] for idx, cnt in top10.items()]

        lines = [
            f"### {col}",
            f"- Inferred type: `{self.colTypes.get(col, 'unknown')}`",
            f"- Pandas dtype: `{series.dtype}`",
            f"- Non-null count: {nonNullCount}",
            f"- Missing: {missingCount} ({missingPct:.2f}%)",
            f"- Cardinality (unique): {uniqueCount}",
            f"- Mode: `{modeValue}`",
            f"- Least frequent value: `{leastValue}` ({leastCount})",
            "",
            "#### Top 10 Value Counts",
            self.mdTable(topRows, ["Value", "Count", "Percentage"]) if topRows else "No non-null values.",
        ]

        if uniqueCount > 10:
            lines.append(f"- Showing top 10 of {uniqueCount} unique values.")

        return "\n".join(lines)

    # function to specifically analyze boolean columns
    def analyzeBoolean(self, col: str) -> str:
        # make sure the dataframe is loaded
        if self.df is None:
            return f"### {col}\n\nNo data loaded."

        # get some statistics about the boolean column like
        # non-null count, missing count, value counts, true ratio
        # also normalize the boolean values to 1 and 0
        series = self.df[col]
        nonNull = series.dropna()
        missingCount = int(series.isna().sum())
        missingPct = self.percent(missingCount, len(series))

        normalized = nonNull.map(self.normalizeBoolToken)
        vc = nonNull.astype(str).value_counts(dropna=True)
        total_nonNull = int(nonNull.count())

        trueRatio = self.percent(int((normalized == 1).sum()), total_nonNull) / 100 if total_nonNull else 0.0
        rows = [[idx, int(cnt), f"{self.percent(int(cnt), total_nonNull):.2f}%"] for idx, cnt in vc.items()]

        detectedValues = sorted(nonNull.astype(str).unique().tolist())

        lines = [
            f"### {col}",
            f"- Inferred type: `{self.colTypes.get(col, 'unknown')}`",
            f"- Detected boolean-like values: {detectedValues}",
            f"- Missing: {missingCount} ({missingPct:.2f}%)",
            "",
            "#### Value Counts",
            self.mdTable(rows, ["Value", "Count", "Percentage"]) if rows else "No non-null values.",
            f"- True ratio: {trueRatio:.4f}",
        ]
        return "\n".join(lines)

    # function to specifically analyze datetime columns
    def analyzeDatetime(self, col: str) -> str:
        # make sure the dataframe is loaded
        if self.df is None:
            return f"### {col}\n\nNo data loaded."

        # get some statistics about the datetime column like
        # non-null count, missing count, earliest date, latest date, total range (days),
        # is monotonically increasing, min gap, max gap, mean gap
        series = self.df[col]
        parsed = pd.to_datetime(series, errors="coerce")
        nonNull = parsed.dropna()
        missingCount = int(parsed.isna().sum())
        missingPct = self.percent(missingCount, len(parsed))

        if nonNull.empty:
            return (
                f"### {col}\n"
                f"- Inferred type: `{self.colTypes.get(col, 'unknown')}`\n"
                f"- Missing: {missingCount} ({missingPct:.2f}%)\n"
                "- No parseable datetime values found.\n"
            )

        earliest = nonNull.min()
        latest = nonNull.max()
        dateRangeDays = int((latest - earliest).days)
        monotonic = nonNull.is_monotonic_increasing

        years = nonNull.dt.year.value_counts().head(3)
        months = nonNull.dt.month.value_counts().head(3)
        weekdays = nonNull.dt.day_name().value_counts().head(3)

        sortedVals = nonNull.sort_values()
        gaps = sortedVals.diff().dropna()
        minGap = self.formatTimedelta(gaps.min()) if not gaps.empty else "N/A"
        maxGap = self.formatTimedelta(gaps.max()) if not gaps.empty else "N/A"
        meanGap = self.formatTimedelta(gaps.mean()) if not gaps.empty else "N/A"

        lines = [
            f"### {col}",
            f"- Inferred type: `{self.colTypes.get(col, 'unknown')}`",
            f"- Missing: {missingCount} ({missingPct:.2f}%)",
            f"- Earliest date: {earliest}",
            f"- Latest date: {latest}",
            f"- Total range (days): {dateRangeDays}",
            f"- Is monotonically increasing: {'yes' if monotonic else 'no'}",
            f"- Min gap: {minGap}",
            f"- Max gap: {maxGap}",
            f"- Mean gap: {meanGap}",
            "",
            "#### Most Common Year (Top 3)",
            self.mdTable([[idx, int(cnt)] for idx, cnt in years.items()], ["Year", "Count"]),
            "",
            "#### Most Common Month (Top 3)",
            self.mdTable([[idx, int(cnt)] for idx, cnt in months.items()], ["Month", "Count"]),
            "",
            "#### Most Common Day Of Week (Top 3)",
            self.mdTable([[idx, int(cnt)] for idx, cnt in weekdays.items()], ["Day", "Count"]),
        ]
        return "\n".join(lines)

    # function to specifically analyze text columns
    def analyzeText(self, col: str) -> str:
        # make sure the dataframe is loaded
        if self.df is None:
            return f"### {col}\n\nNo data loaded."

        # get some statistics about the text column like
        # non-null count, missing count, character length, word length, empty string count
        series = self.df[col]
        text = series.dropna().astype(str)
        stripped = text.str.strip()
        missingCount = int(series.isna().sum())
        missingPct = self.percent(missingCount, len(series))

        charLens = stripped.str.len() if not stripped.empty else pd.Series(dtype=float)
        wordLens = stripped.str.split().str.len() if not stripped.empty else pd.Series(dtype=float)
        emptyCount = int((stripped == "").sum()) if not stripped.empty else 0

        lines = [
            f"### {col}",
            "- Flag: text column",
            f"- Non-null count: {int(text.count())}",
            f"- Missing: {missingCount} ({missingPct:.2f}%)",
            f"- Character length (min/max/mean): {self.seriesMinMaxMean(charLens)}",
            f"- Word count (min/max/mean): {self.seriesMinMaxMean(wordLens)}",
            f"- Empty string count: {emptyCount}",
            "- Note: Deep NLP analysis not included.",
        ]
        return "\n".join(lines)

    # function to specifically analyze identifier columns
    def analyzeId(self, col: str) -> str:
        # make sure the dataframe is loaded
        if self.df is None:
            return f"### {col}\n\nNo data loaded."

        # get some statistics about the identifier column like
        # unique count, unique ratio, sample values
        series = self.df[col]
        uniqueCount = int(series.nunique(dropna=True))
        uniqueRatio = self.percent(uniqueCount, len(series))
        sampleValues = series.dropna().astype(str).head(3).tolist()

        lines = [
            f"### {col}",
            "- Flag: Likely an identifier column - deep analysis skipped.",
            f"- Unique count: {uniqueCount}",
            f"- Unique ratio: {uniqueRatio:.2f}%",
            f"- Sample values (up to 3): {sampleValues if sampleValues else 'N/A'}",
        ]
        return "\n".join(lines)

    # SECTION 4 - Missing values
    # here we will analyze the missing values in the dataframe
    # we will check for total missing cells, columns with missing values, columns with 0% missing,
    # columns with >50% missing, columns with 100% missing, and co-missing pairs (>50%)
    # we will also add warnings for columns with high missingness, fully missing columns, and co-missing pairs (>50%)
    def sectionMissing(self) -> str:
        if self.df is None:
            return "## 4. Missing Values\n\nNo data loaded.\n"

        df = self.df
        totalMissing = int(df.isna().sum().sum())
        section = ["## 4. Missing Values", f"- Total missing cells: {totalMissing}"]

        missingCols = []
        no_missingCols = []

        for col in df.columns:
            miss = int(df[col].isna().sum())
            missPct = self.percent(miss, len(df))
            if miss > 0:
                missingCols.append([col, miss, f"{missPct:.2f}%", self.colTypes.get(col, "unknown"), missPct])
            else:
                no_missingCols.append(col)

            if missPct > 50:
                self.addWarning(f"Column '{col}' has high missingness ({missPct:.2f}%).")
            if missPct == 100:
                self.addWarning(f"Column '{col}' is fully missing (100%).")

        if missingCols:
            missingCols_sorted = sorted(missingCols, key=lambda row: row[4], reverse=True)
            displayRows = [row[:4] for row in missingCols_sorted]
            section.extend(
                [
                    "",
                    "### Columns With Missing Values",
                    self.mdTable(displayRows, ["Column", "Missing Count", "Missing %", "Inferred Type"]),
                ]
            )
        else:
            section.append("- No missing values detected in any column.")

        section.append(
            f"- Columns with 0% missing: {', '.join(no_missingCols) if no_missingCols else 'None'}"
        )

        missingColumns = [col for col in df.columns if df[col].isna().sum() > 0]
        coMissingRows: list[list[Any]] = []
        for colA, colB in combinations(missingColumns, 2):
            bothMissing = int((df[colA].isna() & df[colB].isna()).sum())
            pct = self.percent(bothMissing, len(df))
            if pct > 50:
                coMissingRows.append([colA, colB, bothMissing, f"{pct:.2f}%"])

        if coMissingRows:
            section.extend(
                [
                    "",
                    "### Co-missing Pairs (>50%)",
                    self.mdTable(
                        coMissingRows,
                        ["Column A", "Column B", "Co-missing Rows", "Co-missing %"],
                    ),
                ]
            )
        else:
            section.append("- No high co-missing pairs (>50%) found.")

        section.append("")
        return "\n".join(section)

    # SECTION 5 - Correlations
    # here we will analyze the correlations between the columns in the dataframe
    # we will check for numeric vs numeric correlations, categorical vs categorical correlations, and feature vs target correlations
    # we will also add warnings for potential multicollinearity, and no strong numeric correlations found
    def sectionCorrelations(self) -> str:
        if self.df is None:
            return "## 5. Correlations\n\nNo data loaded.\n"

        df = self.df
        section = ["## 5. Correlations", "### Numeric vs Numeric (Pearson)"]

        numericCols = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
        if len(numericCols) < 2:
            section.append("- Not enough numeric columns for Pearson correlation.")
        else:
            corr = df[numericCols].corr(numeric_only=True)
            pairs = []
            for i, colA in enumerate(corr.columns):
                for colB in corr.columns[i + 1 :]:
                    val = corr.loc[colA, colB]
                    if pd.notna(val) and abs(val) > 0.5:
                        strength = self.corrStrength(abs(float(val)))
                        pairs.append([colA, colB, float(val), strength, abs(float(val))])
                        if abs(val) > 0.9:
                            self.addWarning(
                                f"Potential multicollinearity: '{colA}' vs '{colB}' (r={val:.4f})."
                            )
            if pairs:
                pairs = sorted(pairs, key=lambda row: row[4], reverse=True)
                tableRows = [[a, b, r, s] for a, b, r, s, _ in pairs]
                section.append(self.mdTable(tableRows, ["Feature A", "Feature B", "Pearson r", "Strength"]))
            else:
                section.append("- No strong numeric correlations found.")

        section.extend(["", "### Categorical vs Categorical (Cramer's V)"])
        catCols = [col for col in df.columns if self.colTypes.get(col) == "categorical"]
        cramersRows = []
        for colA, colB in combinations(catCols, 2):
            if df[colA].nunique(dropna=True) > 50 or df[colB].nunique(dropna=True) > 50:
                continue
            v = self.cramersV(df[colA], df[colB])
            if v > 0.3:
                strength = self.corrStrength(v, categorical=True)
                cramersRows.append([colA, colB, v, strength, v])

        if cramersRows:
            cramersRows = sorted(cramersRows, key=lambda row: row[4], reverse=True)
            section.append(
                self.mdTable(
                    [[a, b, v, s] for a, b, v, s, _ in cramersRows],
                    ["Feature A", "Feature B", "Cramer's V", "Strength"],
                )
            )
        else:
            section.append("- No categorical pairs exceeded Cramer's V > 0.3.")

        # find correlations between features and target
        # if the target column is a regression or time-series target, we will check for Pearson r correlations
        # if the target column is a classification target, we will check for Cramer's V and point-biserial correlations
        # if the target column is a binary classification target, we will check for point-biserial correlations
        if self.targetCol in df.columns:
            section.extend(["", "### Feature vs Target"])
            targetType = self.taskType
            target = df[self.targetCol]
            featureRows = []

            if targetType in {"regression", "time-series"}:
                targetNum = pd.to_numeric(target, errors="coerce")
                for col in numericCols:
                    if col == self.targetCol:
                        continue
                    pairDf = pd.DataFrame({"x": pd.to_numeric(df[col], errors="coerce"), "y": targetNum}).dropna()
                    if len(pairDf) < 2:
                        continue
                    val = pairDf["x"].corr(pairDf["y"])
                    if pd.notna(val):
                        featureRows.append([col, "Pearson r", float(val), abs(float(val))])
            else:
                target_nonNull = target.dropna()
                targetUnique = target_nonNull.nunique(dropna=True)
                for col in catCols:
                    if col == self.targetCol:
                        continue
                    v = self.cramersV(df[col], target)
                    if pd.notna(v):
                        featureRows.append([col, "Cramer's V", float(v), abs(float(v))])

                if targetUnique == 2:
                    validTarget = target_nonNull.astype("category")
                    mapping = {cat: idx for idx, cat in enumerate(validTarget.cat.categories)}
                    encodedTarget = target.map(mapping)
                    for col in numericCols:
                        if col == self.targetCol:
                            continue
                        pairDf = pd.DataFrame(
                            {"x": pd.to_numeric(df[col], errors="coerce"), "y": encodedTarget}
                        ).dropna()
                        if len(pairDf) < 2:
                            continue
                        stat, _ = pointbiserialr(pairDf["y"], pairDf["x"])
                        if pd.notna(stat):
                            featureRows.append([col, "Point-Biserial", float(stat), abs(float(stat))])
                else:
                    section.append("- Point-biserial is skipped because target is not binary.")

            if featureRows:
                featureRows = sorted(featureRows, key=lambda row: row[3], reverse=True)
                section.append(
                    self.mdTable(
                        [[a, b, c] for a, b, c, _ in featureRows],
                        ["Feature", "Metric", "Value"],
                    )
                )
            else:
                section.append("- No valid feature-target relationships were computed.")

        section.append("")
        return "\n".join(section)

    # SECTION 6 - Outliers
    # here we will analyze the outliers in the dataframe
    # we will check for IQR outliers and Z-score outliers in the numeric columns
    # we will also add warnings for columns with >5% IQR outliers
    def sectionOutliers(self) -> str:
        section = ["## 6. Outlier Summary"]
        if not self.outlierStats:
            section.extend(["- No numeric columns found for outlier analysis.", ""])
            return "\n".join(section)

        rows = []
        for col, stats in self.outlierStats.items():
            rows.append(
                [
                    col,
                    int(stats["iqr_count"]),
                    f"{stats['iqrPct']:.2f}%",
                    int(stats["z_count"]),
                    f"{stats['zPct']:.2f}%",
                    stats["iqr_count"],
                ]
            )
            if stats["iqrPct"] > 5:
                self.addWarning(f"Outlier summary flags '{col}' above 5% IQR outliers.")

        rowsSorted = sorted(rows, key=lambda row: row[5], reverse=True)
        display = [row[:5] for row in rowsSorted]
        section.append(
            self.mdTable(
                display,
                ["Column", "IQR Outlier Count", "IQR Outlier %", "Z-score Outlier Count", "Z-score Outlier %"],
            )
        )
        section.append("")
        return "\n".join(section)

    # SECTION 7 - Warnings
    # here is the section that contains warnings we added along our EDA journey
    # we will group the warnings by category and add them to the section
    def sectionWarnings(self) -> str:
        section = ["## 7. Data Quality Warnings"]
        if not self.warnings:
            section.extend(["No data quality issues detected.", ""])
            return "\n".join(section)

        grouped: dict[str, list[str]] = {
            "Missing Data": [],
            "Outliers": [],
            "Correlations": [],
            "Cardinality": [],
            "Skewness": [],
            "Class Imbalance": [],
            "Other": [],
        }

        for msg in self.warnings:
            lowered = msg.lower()
            if "missing" in lowered:
                grouped["Missing Data"].append(msg)
            elif "outlier" in lowered:
                grouped["Outliers"].append(msg)
            elif "correlation" in lowered or "multicollinearity" in lowered:
                grouped["Correlations"].append(msg)
            elif "cardinality" in lowered or "identifier-like" in lowered:
                grouped["Cardinality"].append(msg)
            elif "skew" in lowered:
                grouped["Skewness"].append(msg)
            elif "imbalance" in lowered or "minority class" in lowered:
                grouped["Class Imbalance"].append(msg)
            else:
                grouped["Other"].append(msg)

        idx = 1
        for groupName, items in grouped.items():
            if not items:
                continue
            section.append(f"### {groupName}")
            for item in items:
                section.append(f"{idx}. {item}")
                idx += 1
            section.append("")

        return "\n".join(section)

    # simple function to add warnings to the warnings list
    def addWarning(self, msg: str) -> None:
        self.warnings.append(msg)

    # function to convert a list of lists to a markdown table
    def mdTable(self, data: list[list[Any]], headers: list[str]) -> str:
        return tabulate(data, headers=headers, tablefmt="pipe", floatfmt=".4f")

    # function to calculate the percentage safely
    @staticmethod
    def percent(part: float, whole: float) -> float:
        if whole == 0:
            return 0.0
        return round((part / whole) * 100, 2)

    # function to calculate the class imbalance level
    @staticmethod
    def classImbalanceLevel(imbalanceRatio: float) -> str:
        if imbalanceRatio <= 1.5:
            return "no imbalance"
        if imbalanceRatio <= 2.0:
            return "weak imbalance"
        if imbalanceRatio <= 3.0:
            return "moderate imbalance"
        if imbalanceRatio <= 6.0:
            return "strong imbalance"
        return "very strong imbalance"

    # function to format the size in bytes to a human readable format
    @staticmethod
    def formatBytes(sizeInBytes: int) -> str:
        if sizeInBytes < 1024:
            return f"{sizeInBytes} B"
        if sizeInBytes < 1024**2:
            return f"{sizeInBytes / 1024:.2f} KB"
        return f"{sizeInBytes / (1024**2):.2f} MB"

    # function to create a markdown anchor from a text
    @staticmethod
    def markdownAnchor(text: str) -> str:
        anchor = text.lower().strip()
        anchor = re.sub(r"[^\w\s-]", "", anchor)
        anchor = re.sub(r"\s+", "-", anchor)
        return anchor

    # function to get the min, max, and mean of a series
    @staticmethod
    def seriesMinMaxMean(series: pd.Series) -> str:
        if series.empty:
            return "N/A"
        return f"{float(series.min()):.4f} / {float(series.max()):.4f} / {float(series.mean()):.4f}"

    # function to format a timedelta to a human readable format
    @staticmethod
    def formatTimedelta(value: timedelta | pd.Timedelta) -> str:
        if pd.isna(value):
            return "N/A"
        totalSeconds = int(value.total_seconds())
        days, remainder = divmod(totalSeconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        parts = []
        if days:
            parts.append(f"{days}d")
        if hours:
            parts.append(f"{hours}h")
        if minutes:
            parts.append(f"{minutes}m")
        if seconds or not parts:
            parts.append(f"{seconds}s")
        return " ".join(parts)

    # function to calculate the average word count of a series
    @staticmethod
    def averageWordCount(series: pd.Series) -> float:
        if series.empty:
            return 0.0
        text = series.astype(str).str.strip()
        words = text.str.split().str.len()
        return float(words.mean()) if len(words) else 0.0

    @staticmethod
    # function to normalize a boolean value to 1 and 0
    def normalizeBoolToken(value: Any) -> int | None:
        if pd.isna(value):
            return None
        normalized = str(value).strip().lower()
        truthy = {"1", "true", "t", "yes", "y"}
        falsy = {"0", "false", "f", "no", "n"}
        if normalized in truthy:
            return 1
        if normalized in falsy:
            return 0
        return None

    # function to check if a series is a boolean series
    def isBooleanSeries(self, series: pd.Series) -> bool:
        if series.empty:
            return False
        if pd.api.types.is_bool_dtype(series):
            return True
        normalized = series.map(self.normalizeBoolToken).dropna()
        if len(normalized) != len(series):
            return False
        return normalized.nunique(dropna=True) == 2

    # function to calculate the datetime parse success ratio
    # checks if a string column is a datetime in reality
    def datetimeParseSuccessRatio(self, series: pd.Series) -> float:
        if series.empty:
            return 0.0
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=UserWarning)
            try:
                parsed = pd.to_datetime(series, errors="coerce", format="mixed")
            except TypeError:
                try:
                    parsed = pd.to_datetime(series, errors="coerce")
                except Exception:
                    return 0.0
            except Exception:
                return 0.0
        success = parsed.notna().sum()
        return float(success / len(series)) if len(series) else 0.0

    # function to try and convert a string column to a numeric column
    # checks if a string column is a numeric column in reality
    def tryConvertStringNumeric(self, col: str) -> bool:
        if self.df is None:
            return False
        series = self.df[col]
        if not (pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series)):
            return False

        nonNull = series.dropna().astype(str)
        if nonNull.empty:
            return False

        cleaned = (
            nonNull.str.replace(",", "", regex=False)
            .str.replace("$", "", regex=False)
            .str.strip()
        )
        converted = pd.to_numeric(cleaned, errors="coerce")
        successRatio = converted.notna().mean() if len(converted) else 0.0
        if successRatio > 0.90:
            self.addWarning(
                f"Column '{col}' appears numeric-like in string format (parse success ratio: {successRatio * 100:.2f}%)."
            )
            return True
        return False

    @staticmethod
    # function to calculate the correlation strength
    def corrStrength(value: float, categorical: bool = False) -> str:
        if value < 0.20:
            return "Very Weak"
        if value < 0.40:
            return "Weak"
        if value < 0.60:
            return "Moderate"
        if value < 0.80:
            return "Strong"
        return "Very Strong"

    @staticmethod
    # function to calculate the Cramer's V
    def cramersV(x: pd.Series, y: pd.Series) -> float:
        data = pd.DataFrame({"x": x, "y": y}).dropna()
        if data.empty:
            return 0.0
        contingency = pd.crosstab(data["x"], data["y"])
        if contingency.empty:
            return 0.0
        chi2 = chi2Contingency(contingency)[0]
        n = contingency.values.sum()
        if n == 0:
            return 0.0
        r, k = contingency.shape
        phi2 = chi2 / n
        phi2corr = max(0, phi2 - ((k - 1) * (r - 1)) / (n - 1)) if n > 1 else 0
        rcorr = r - ((r - 1) ** 2) / (n - 1) if n > 1 else r
        kcorr = k - ((k - 1) ** 2) / (n - 1) if n > 1 else k
        denom = min((kcorr - 1), (rcorr - 1))
        if denom <= 0:
            return 0.0
        return float(np.sqrt(phi2corr / denom))

    # function to write the report to a file
    def writeReport(self) -> None:
        report = "\n\n".join(self.reportSections)
        with open(self.outputPath, "w", encoding="utf-8") as file:
            file.write(report)

# run the code with existing data to test
if __name__ == "__main__":
    eda = EDA(
        inputPath="./data/ibmchurn.csv",
        targetCol="Churn",
        taskType="binary-classification",
    )
    eda.run()