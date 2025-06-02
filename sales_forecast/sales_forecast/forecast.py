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
        print("Starting sales forecast...")
        
        # 1) Fetch & aggregate sales data
        print("Fetching sales invoice data...")
        sales_data = []
        invoices = frappe.get_list("Sales Invoice", 
                                  filters={"docstatus": 1},
                                  fields=["name", "posting_date", "grand_total"])
        
        print(f"Found {len(invoices)} sales invoices")
        
        if not invoices:
            frappe.log_error("No sales invoices found for forecasting", "Sales Forecast")
            print("No sales invoices found")
            return
            
        # Convert to simple Python types
        for inv in invoices:
            sales_data.append({
                "posting_date": str(inv.posting_date),  # Convert date to string
                "grand_total": float(inv.grand_total)   # Convert decimal to float
            })
            
        print("Creating DataFrame...")
        df = pd.DataFrame(sales_data)
        df["posting_date"] = pd.to_datetime(df["posting_date"])
        
        print("Aggregating monthly sales...")
        # Aggregate monthly sales
        monthly = (df.set_index("posting_date")
                     .resample("M")["grand_total"]
                     .sum()
                     .reset_index()
                     .rename(columns={"posting_date": "ds", "grand_total": "y"}))

        print(f"Have {len(monthly)} months of data")
        
        if len(monthly) < 12:
            frappe.log_error("Insufficient data for forecasting (need at least 12 months)", "Sales Forecast")
            print("Insufficient data - need at least 12 months")
            return

        # 2) Create features
        print("Creating features...")
        monthly["lag1"] = monthly["y"].shift(1)
        monthly["lag12"] = monthly["y"].shift(12)
        monthly["ma3"] = monthly["y"].rolling(3).mean()
        monthly.dropna(inplace=True)

        if len(monthly) == 0:
            frappe.log_error("No data available after feature engineering", "Sales Forecast")
            print("No data available after feature engineering")
            return

        X = monthly[["lag1", "lag12", "ma3"]].assign(
              month=monthly.ds.dt.month,
              quarter=monthly.ds.dt.quarter
            )
        y = monthly.y

        # 3) Train model & predict next month
        print("Training model...")
        model = lgb.LGBMRegressor(verbose=-1)  # Suppress warnings
        model.fit(X, y)

        last = monthly.ds.max()
        nxt = last + MonthEnd(1)
        
        print(f"Generating forecast for {nxt.date()}")
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
        print(f"Predicted value: {pred}")

        # 4) Upsert forecast record
        print("Saving forecast...")
        filters = {"forecast_date": nxt.date()}
        exists = frappe.db.exists("Sales Forecast", filters)

        if exists:
            doc = frappe.get_doc("Sales Forecast", exists)
            doc.value = pred
            doc.save(ignore_permissions=True)
            print(f"Updated forecast for {nxt.date()}: {pred}")
        else:
            frappe.get_doc({
                "doctype": "Sales Forecast",
                "forecast_date": nxt.date(),
                "period": "Monthly",
                "value": pred
            }).insert(ignore_permissions=True)
            print(f"Created new forecast for {nxt.date()}: {pred}")
        
        frappe.db.commit()
        print("Forecast completed successfully!")
        
    except Exception as e:
        frappe.log_error(f"Error in sales forecasting: {str(e)}", "Sales Forecast")
        print(f"Error occurred: {str(e)}")
        raise e 