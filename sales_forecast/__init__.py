# -*- coding: utf-8 -*-
from __future__ import unicode_literals

__version__ = '0.0.1'

import frappe
import pandas as pd
import lightgbm as lgb
from pandas.tseries.offsets import MonthEnd

def run_and_store():
    """
    Main function to run sales forecasting and store results.
    This function will be called by the cron job.
    """
    try:
        # 1) Fetch & aggregate sales data
        inv = frappe.get_all("Sales Invoice",
                             filters={"docstatus": 1},
                             fields=["posting_date", "grand_total"])
        
        if not inv:
            frappe.log_error("No sales invoices found for forecasting", "Sales Forecast")
            return
        
        df = pd.DataFrame(inv)
        df["posting_date"] = pd.to_datetime(df["posting_date"])
        
        # Aggregate monthly sales
        monthly = (df.set_index("posting_date")
                     .resample("M")["grand_total"]
                     .sum()
                     .reset_index()
                     .rename(columns={"posting_date": "ds", "grand_total": "y"}))

        if len(monthly) < 12:
            frappe.log_error("Insufficient data for forecasting (need at least 12 months)", "Sales Forecast")
            return

        # 2) Create features
        monthly["lag1"] = monthly["y"].shift(1)
        monthly["lag12"] = monthly["y"].shift(12)
        monthly["ma3"] = monthly["y"].rolling(3).mean()
        monthly.dropna(inplace=True)

        if len(monthly) == 0:
            frappe.log_error("No data available after feature engineering", "Sales Forecast")
            return

        X = monthly[["lag1", "lag12", "ma3"]].assign(
              month=monthly.ds.dt.month,
              quarter=monthly.ds.dt.quarter
            )
        y = monthly.y

        # 3) Train model & predict next month
        model = lgb.LGBMRegressor(verbose=-1)  # Suppress warnings
        model.fit(X, y)

        last = monthly.ds.max()
        nxt = last + MonthEnd(1)
        
        # Create features for next month
        feat = {
            "lag1": monthly.y.iloc[-1],
            "lag12": monthly.set_index("ds")
                          .reindex([nxt - pd.DateOffset(months=12)])
                          .y.fillna(monthly.y.mean())
                          .iloc[0],
            "ma3": monthly.y.iloc[-3:].mean(),
            "month": nxt.month,
            "quarter": nxt.quarter
        }
        
        pred = float(model.predict(pd.DataFrame([feat]))[0])

        # 4) Upsert forecast record
        filters = {"forecast_date": nxt.date()}
        exists = frappe.db.exists("Sales Forecast", filters)

        if exists:
            doc = frappe.get_doc("Sales Forecast", exists)
            doc.value = pred
            doc.save(ignore_permissions=True)
            frappe.logger().info(f"Updated forecast for {nxt.date()}: {pred}")
        else:
            frappe.get_doc({
                "doctype": "Sales Forecast",
                "forecast_date": nxt.date(),
                "period": "Monthly",
                "value": pred
            }).insert(ignore_permissions=True)
            frappe.logger().info(f"Created new forecast for {nxt.date()}: {pred}")
        
        frappe.db.commit()
        
    except Exception as e:
        frappe.log_error(f"Error in sales forecasting: {str(e)}", "Sales Forecast")
        raise 