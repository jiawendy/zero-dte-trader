import os

def save_analysis_to_disk(data):
    """Saves the analysis data to a local text file in the 'reports' directory."""
    if not data or not data.get("text"):
        return None, "No analysis available to save"
        
    try:
        # Create 'reports' directory if not exists
        # Use absolute path relative to the backend directory
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        reports_dir = os.path.join(base_dir, "reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        # Generate filename based on date only (YYYY-MM-DD)
        date_str = data.get("timestamp", "").split("T")[0]
        if not date_str:
            import datetime
            date_str = datetime.date.today().strftime("%Y-%m-%d")
            
        filename = f"analysis_{date_str}.txt"
        filepath = os.path.join(reports_dir, filename)
        
        # Open in append mode
        with open(filepath, "a") as f:
            # Format timestamp
            timestamp_str = data.get('timestamp')
            formatted_time = timestamp_str
            try:
                import datetime
                from zoneinfo import ZoneInfo
                if timestamp_str:
                    dt = datetime.datetime.fromisoformat(timestamp_str)
                    et_dt = dt.astimezone(ZoneInfo("America/New_York"))
                    formatted_time = et_dt.strftime("%b %d, %Y at %I:%M %p ET")
            except Exception as e:
                print(f"Error formatting time for local save: {e}")

            f.write(f"\n{'='*40}\n")
            f.write(f"TIME: {formatted_time}\n")
            f.write(f"{'='*40}\n\n")
            f.write(data.get("text"))
            
            # Append data summary if available
            if data.get("data"):
                f.write("\n\n--- Data Summary ---\n")
                for k, v in data["data"].items():
                    f.write(f"{k}: {v}\n")
            f.write("\n\n") # Extra spacing between entries
            
        return filepath, None
    except Exception as e:
        return None, str(e)
