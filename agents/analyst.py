# from scipy.stats import pearsonr
# from scipy.stats import spearmanr
# from scipy.stats import ttest_ind
# from scipy.stats import f_oneway

# import statsmodels.api as sm

# def analyze_hypotheses(df, hypotheses):

#     if hypotheses.get("status") != "success":
#         return {
#             "agent": "Analyst Agent",
#             "status": "skipped",
#             "reason": "Hypothesis Agent failed.",
#             "analysis": []
#         }

#     results = []

#     for hypothesis in hypotheses.get("hypotheses", []):

#         result = {
#             "id": hypothesis.get("id"),
#             "statement": hypothesis.get("statement"),
#             "test": hypothesis.get("recommended_test"),
#             "status": "Not Executed"
#         }

#         try:

#             test = hypothesis.get("recommended_test")

#             # Pearson Correlation

#             if test == "pearson_correlation":

#                 columns = hypothesis.get("columns", [])

#                 if len(columns) != 2:
#                     raise ValueError("Pearson requires exactly 2 columns.")

#                 col1, col2 = columns

#                 if col1 not in df.columns or col2 not in df.columns:
#                     raise ValueError("Column not found in dataset.")

#                 corr, p = pearsonr(df[col1], df[col2])

#                 result.update({
#                     "columns": columns,
#                     "correlation": round(float(corr), 4),
#                     "p_value": float(p),
#                     "significant": bool(p < 0.05),
#                     "direction": "Positive" if corr > 0 else "Negative",
#                     "effect_strength": (
#                         "Very Strong" if abs(corr) >= 0.8 else
#                         "Strong" if abs(corr) >= 0.6 else
#                         "Moderate" if abs(corr) >= 0.4 else
#                         "Weak"
#                     ),
#                     "status": "Completed"
#                 })

#             # Spearman Correlation

#             elif test == "spearman_correlation":

#                 columns = hypothesis.get("columns", [])

#                 if len(columns) != 2:
#                     raise ValueError("Spearman requires exactly 2 columns.")

#                 col1, col2 = columns

#                 if col1 not in df.columns or col2 not in df.columns:
#                     raise ValueError("Column not found in dataset.")

#                 corr, p = spearmanr(df[col1], df[col2])

#                 result.update({
#                     "columns": columns,
#                     "correlation": round(float(corr), 4),
#                     "p_value": float(p),
#                     "significant": bool(p < 0.05),
#                     "direction": "Positive" if corr > 0 else "Negative",
#                     "effect_strength": (
#                         "Very Strong" if abs(corr) >= 0.8 else
#                         "Strong" if abs(corr) >= 0.6 else
#                         "Moderate" if abs(corr) >= 0.4 else
#                         "Weak"
#                     ),
#                     "status": "Completed"
#                 })

#             # Linear Regression

#             elif test == "linear_regression":

#                 dependent = hypothesis.get("dependent")
#                 independent = hypothesis.get("independent", [])

#                 if dependent not in df.columns:
#                     raise ValueError("Dependent column not found.")

#                 for col in independent:
#                     if col not in df.columns:
#                         raise ValueError(f"{col} not found.")

#                 X = sm.add_constant(df[independent])
#                 y = df[dependent]

#                 model = sm.OLS(y, X).fit()

#                 predictor = independent[0]

#                 coef = model.params[predictor]
#                 stderr = model.bse[predictor]
#                 pvalue = model.pvalues[predictor]
#                 ci = model.conf_int().loc[predictor]

#                 result.update({
#                     "dependent": dependent,
#                     "independent": independent,
#                     "coefficient": round(float(coef), 10),
#                     "intercept": round(float(model.params["const"]), 10),
#                     "r2_score": round(float(model.rsquared), 10),
#                     "adjusted_r2": round(float(model.rsquared_adj), 10),
#                     "f_statistic": round(float(model.fvalue), 10),
#                     "p_value": float(pvalue),
#                     "standard_error": round(float(stderr), 10),
#                     "confidence_interval": [
#                         round(float(ci[0]), 10),
#                         round(float(ci[1]), 10)
#                     ],
#                     "significant": bool(pvalue < 0.05),
#                     "status": "Completed"
#                 })


#              # T-Test

#             elif test == "t_test":

#                 group_col = hypothesis.get("group_column")
#                 target_col = hypothesis.get("target_column")

#                 if group_col not in df.columns:
#                     raise ValueError("Group column not found.")

#                 if target_col not in df.columns:
#                     raise ValueError("Target column not found.")

#                 groups = df[group_col].dropna().unique()

#                 if len(groups) != 2:

#                     result.update({
#                         "status": "Skipped",
#                         "reason": "T-Test requires exactly two groups."
#                     })

#                 else:

#                     sample1 = df[df[group_col] == groups[0]][target_col]
#                     sample2 = df[df[group_col] == groups[1]][target_col]

#                     t_stat, p_value = ttest_ind(sample1, sample2, equal_var=False)

#                     result.update({
#                         "group_column": group_col,
#                         "target_column": target_col,
#                         "t_statistic": round(float(t_stat), 4),
#                         "p_value": float(p_value),
#                         "significant": bool(p_value < 0.05),
#                         "status": "Completed"
#                     })

#             # ANOVA

#             elif test == "anova":

#                 group_col = hypothesis.get("group_column")
#                 target_col = hypothesis.get("target_column")

#                 if group_col not in df.columns:
#                     raise ValueError("Group column not found.")

#                 if target_col not in df.columns:
#                     raise ValueError("Target column not found.")

#                 grouped = [group[target_col].values for _, group in df.groupby(group_col)]

#                 if len(grouped) < 2:
#                     raise ValueError("ANOVA requires at least two groups.")

#                 f_stat, p_value = f_oneway(*grouped)

#                 result.update({
#                     "group_column": group_col,
#                     "target_column": target_col,
#                     "f_statistic": round(float(f_stat), 4),
#                     "p_value": float(p_value),
#                     "significant": bool(p_value < 0.05),
#                     "status": "Completed"
#                 })

#             # Unknown Test

#             else:

#                 result.update({
#                     "status": "Unsupported Test",
#                     "error": f"Unsupported statistical test: {test}"
#                 })

#         except Exception as e:

#             result.update({"status": "Failed", "error": str(e)})

#         results.append(result)

#     return {
#         "agent": "Analyst Agent",
#         "status": "success",
#         "analysis": results
#     }


# if __name__ == "__main__":
#     print("Analyst Agent Ready")


from scipy.stats import pearsonr
from scipy.stats import spearmanr
from scipy.stats import ttest_ind
from scipy.stats import f_oneway

import statsmodels.api as sm

import pandas as pd


def analyze_hypotheses(df, hypotheses):

    if hypotheses.get("status") != "success":

        return {
            "agent": "Analyst Agent",
            "status": "skipped",
            "reason": "Hypothesis Agent failed.",
            "analysis": []
        }

    results = []

    for hypothesis in hypotheses.get("hypotheses", []):

        result = {

            "id": hypothesis.get("id"),

            "statement": hypothesis.get("statement"),

            "test": hypothesis.get("recommended_test"),

            "status": "Not Executed"

        }

        try:

            test = hypothesis.get("recommended_test")

            # --------------------------------------------------
            # Pearson Correlation
            # --------------------------------------------------

            if test == "pearson_correlation":

                columns = hypothesis.get("columns", [])

                if len(columns) != 2:
                    raise ValueError(
                        "Pearson Correlation requires exactly two columns."
                    )

                col1, col2 = columns

                if col1 not in df.columns or col2 not in df.columns:
                    raise ValueError("Column not found in dataset.")

                corr, p = pearsonr(df[col1], df[col2])

                result.update({

                    "columns": columns,

                    "correlation": round(float(corr), 4),

                    "p_value": round(float(p), 6),

                    "significant": bool(p < 0.05),

                    "direction":
                        "Positive" if corr > 0 else "Negative",

                    "effect_strength":
                        (
                            "Very Strong"
                            if abs(corr) >= 0.80 else

                            "Strong"
                            if abs(corr) >= 0.60 else

                            "Moderate"
                            if abs(corr) >= 0.40 else

                            "Weak"
                        ),

                    "status": "Completed"

                })

            
            # Spearman Correlation
            

            elif test == "spearman_correlation":

                columns = hypothesis.get("columns", [])

                if len(columns) != 2:
                    raise ValueError(
                        "Spearman Correlation requires exactly two columns."
                    )

                col1, col2 = columns

                if col1 not in df.columns or col2 not in df.columns:
                    raise ValueError("Column not found in dataset.")

                corr, p = spearmanr(df[col1], df[col2])

                result.update({

                    "columns": columns,

                    "correlation": round(float(corr), 4),

                    "p_value": round(float(p), 6),

                    "significant": bool(p < 0.05),

                    "direction":
                        "Positive" if corr > 0 else "Negative",

                    "effect_strength":
                        (
                            "Very Strong"
                            if abs(corr) >= 0.80 else

                            "Strong"
                            if abs(corr) >= 0.60 else

                            "Moderate"
                            if abs(corr) >= 0.40 else

                            "Weak"
                        ),

                    "status": "Completed"

                })

            # Multiple Linear Regression
           

            elif test == "linear_regression":

                dependent = hypothesis.get("dependent")

                independent = hypothesis.get("independent", [])

                if dependent not in df.columns:
                    raise ValueError(
                        "Dependent column not found."
                    )

                if len(independent) == 0:
                    raise ValueError(
                        "No independent variables supplied."
                    )

                for column in independent:

                    if column not in df.columns:
                        raise ValueError(
                            f"{column} not found."
                        )

                X = sm.add_constant(df[independent])

                y = df[dependent]

                model = sm.OLS(y, X).fit()

                coefficients = {}

                for predictor in independent:

                    ci = model.conf_int().loc[predictor]

                    coefficients[predictor] = {

                        "coefficient":
                            round(
                                float(model.params[predictor]),
                                8
                            ),

                        "standard_error":
                            round(
                                float(model.bse[predictor]),
                                8
                            ),

                        "p_value":
                            round(
                                float(model.pvalues[predictor]),
                                6
                            ),

                        "confidence_interval": [

                            round(float(ci[0]), 8),
                            round(float(ci[1]), 8)

                        ],

                        "significant":
                            bool(
                                model.pvalues[predictor] < 0.05
                            )

                    }

                result.update({

                    "dependent": dependent,
                    "independent": independent,
                    "intercept":
                        round(
                            float(model.params["const"]),
                            8
                        ),

                    "r2_score":
                        round(
                            float(model.rsquared),
                            6
                        ),

                    "adjusted_r2":
                        round(
                            float(model.rsquared_adj),
                            6
                        ),

                    "f_statistic":
                        round(
                            float(model.fvalue),
                            6
                        ),

                    "model_p_value":
                        round(
                            float(model.f_pvalue),
                            6
                        ),

                    "coefficients":
                        coefficients,

                    "status":
                        "Completed"

                })

                           
            # Independent T-Test
            

            elif test == "t_test":

                group_col = hypothesis.get("group_column")
                target_col = hypothesis.get("target_column")

                if group_col not in df.columns:
                    raise ValueError("Group column not found.")

                if target_col not in df.columns:
                    raise ValueError("Target column not found.")

                groups = df[group_col].dropna().unique()

                if len(groups) != 2:

                    result.update({

                        "status": "Skipped",

                        "reason":
                            "T-Test requires exactly two groups."

                    })

                else:

                    sample1 = df[
                        df[group_col] == groups[0]
                    ][target_col].dropna()

                    sample2 = df[
                        df[group_col] == groups[1]
                    ][target_col].dropna()

                    if len(sample1) < 2 or len(sample2) < 2:

                        result.update({

                            "status": "Skipped",

                            "reason":
                                "Each group must contain at least two observations."

                        })

                    else:

                        t_stat, p_value = ttest_ind(
                            sample1,
                            sample2,
                            equal_var=False
                        )

                        result.update({

                            "group_column": group_col,

                            "target_column": target_col,

                            "group_1": str(groups[0]),

                            "group_2": str(groups[1]),

                            "group_1_size": len(sample1),

                            "group_2_size": len(sample2),

                            "t_statistic":
                                round(float(t_stat), 4),

                            "p_value":
                                round(float(p_value), 6),

                            "significant":
                                bool(p_value < 0.05),

                            "status":
                                "Completed"

                        })


            # --------------------------------------------------
            # One-Way ANOVA
            # --------------------------------------------------

            elif test == "anova":

                group_col = hypothesis.get("group_column")
                target_col = hypothesis.get("target_column")

                if group_col not in df.columns:
                    raise ValueError("Group column not found.")

                if target_col not in df.columns:
                    raise ValueError("Target column not found.")

                grouped = [

                    group[target_col].dropna().values

                    for _, group in df.groupby(group_col)

                    if len(group[target_col].dropna()) >= 2

                ]

                if len(grouped) < 2:

                    result.update({

                        "status": "Skipped",

                        "reason":
                            "ANOVA requires at least two groups with two or more observations."

                    })

                else:

                    f_stat, p_value = f_oneway(*grouped)

                    result.update({

                        "group_column": group_col,

                        "target_column": target_col,

                        "groups_compared": len(grouped),

                        "f_statistic":
                            round(float(f_stat), 4),

                        "p_value":
                            round(float(p_value), 6),

                        "significant":
                            bool(p_value < 0.05),

                        "status":
                            "Completed"

                    })


            # --------------------------------------------------
            # Unsupported Test
            # --------------------------------------------------

            else:

                result.update({

                    "status": "Unsupported",

                    "error":
                        f"{test} is currently not implemented."

                })


        except Exception as e:

            result.update({

                "status": "Failed",

                "error": str(e)

            })

        results.append(result)


    return {

        "agent": "Analyst Agent",

        "status": "success",

        "analysis": results

    }


if __name__ == "__main__":

    print("Analyst Agent Ready") 