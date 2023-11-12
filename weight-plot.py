from datetime import datetime
import json
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import os
import pandas as pd
import sys
import zipfile

def read_json_file(zip_file_path,file_path):
    with zipfile.ZipFile(zip_file_path, 'r') as zip:
        with zip.open(file_path) as file:
            return json.load(file)

def extract_weight_data(json_data, dateString):
    weights = []
    dates = []
    for entry in json_data.get("physicalInformations", []):
        if "weight, kg" in entry and "dateTime" in entry:
            weight = entry["weight, kg"]
            date = pd.to_datetime(entry["dateTime"].split('T')[0])
            if date >= pd.to_datetime(dateString):
                weights.append(weight)
                dates.append(date)
    return pd.DataFrame({'Date': dates, 'Weight': weights})

def plot_weight_data(weight_data):
    min_weight = weight_data['Weight'].min()
    max_weight = weight_data['Weight'].max()
    print(f"Minimum weight: {min_weight}, Maximum weight: {max_weight}")

    fig, ax = plt.subplots(figsize=(10, 5))

    weight_data.sort_values(by='Date', inplace=True)
    ax.set_ylim(max_weight, min_weight)
    ax.invert_yaxis() # works now, as above sets the limits

    
    # Annotating every 10th measurement
    for i, (date, weight) in enumerate(weight_data.itertuples(index=False)):
        if i % 10 == 0:  # Change '10' to any other number if needed
            plt.annotate(f'{weight} kg', (date, weight), textcoords="offset points", 
                xytext=(0, 10), ha='left', rotation=45)  # Positive x-offset, zero y-offset
    # Annotating the last measurement
    last_date, last_weight = weight_data.iloc[-1]['Date'], weight_data.iloc[-1]['Weight']
    plt.annotate(f'{last_weight} kg', (last_date, last_weight), textcoords="offset points", 
               xytext=(10, 0), ha='left', rotation=22.5)
                  
    ax.yaxis.set_major_locator(ticker.MultipleLocator(2))
    
    ax.plot(weight_data['Date'], weight_data['Weight'], marker='o', linestyle='-')

    plt.title('Weight Trend')
    plt.xlabel('Date')
    plt.ylabel('Weight (kg)')
    plt.grid(True)
    plt.xticks(rotation=22.5)
    

    plt.show()

def main():
    # Default date string
    default_date_string = "2023-07-31"

    # Check if a date string is provided as a command-line argument
    if len(sys.argv) > 1:
        zip_file_path = sys.argv[1]
    else:
        print ("Usage:\n\n python weight-plot.py zipfile <start date in format YYYY-MM-DD>\n\n")
        exit()
        
    if len(sys.argv) > 2:
        date_string = sys.argv[2]
        try:
            # Validate the date format
            datetime.strptime(date_string, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Using default date:", default_date_string)
            date_string = default_date_string
    else:
        print("No date provided. Using default date:", default_date_string)
        date_string = default_date_string

    import zipfile

    # Path to the zip file
    # zip_file_path = '..\polar-user-data-export_ec8060df-e364-47b5-abb2-ee7779f63041.zip'

    json_file_path = ''
    with zipfile.ZipFile(zip_file_path, 'r') as zip:
        # List the names of the files in the zip
        file_names = zip.namelist()
        print("Files in the zip archive:")
        for file in file_names:
            if 'calendar-items' in file:
                json_file_path = file
                # Open the file and read the lines
                print ("open file: " + file)
    
    json_data = read_json_file(zip_file_path, json_file_path)
    weight_data = extract_weight_data(json_data, date_string)
    
    date_object = datetime.strptime(date_string, "%Y-%m-%d")
    max_date_timestamp = weight_data['Date'].max()

    # Compare the dates
    if pd.isna(max_date_timestamp):
        print("The start date given is in future compared to dates in Polar data.")
        exit()

    plot_weight_data(weight_data)


if __name__ == "__main__":
    main()
