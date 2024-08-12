from datetime import date, datetime, timedelta

import pandas as pd
import csv
import os, subprocess, platform
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path

PREDEFINED_CATEGORIES = [
    "Food",
    "Transport",
    "Utilities",
    "Entertainment",
    "Healthcare",
    "Education",
    "Rent",
    "Others"
]

# The function below prompts user to enter expense details
def expense_details():
    expense_array = []
    today = date.today()
    expense_type = category_list()
    while True:
        try: 
            amount = float(input("Please Enter Amount: "))
            break
        except ValueError:
            print("Invalid Input, Please try again: ")
    description = input("Please Enter details of expenses: ")
    expense_array.append((today, expense_type, amount, description))
    return expense_array

# The function belows allow user to select a category from predefined list
def category_list():
    while True:
        print("Please select one of the category: ")
        for index, category in enumerate(PREDEFINED_CATEGORIES, start=1):
            print(f"{index}. {category}")
        try:    #make sure that user enters correct values i.e. Intergers
            ask_user = int(input("Enter the number of your choice: "))
            if ask_user in range(1, len(PREDEFINED_CATEGORIES) + 1):
                return PREDEFINED_CATEGORIES[ask_user-1]
            else:
                print("Invalid option, Please try again. ")
        except ValueError:
            print("Invalid option, Please try again ")
    
    

   
# The function below aggregates the total amount spend by the user in a day. This function is than called in the amend data function
def aggregate_amount(filename):
    total_amount_by_date = {}
    with open (filename, mode='r', newline='') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            str_date, category, amount, description = row
            if str_date in total_amount_by_date:
                total_amount_by_date[str_date] +=float(amount)
            else:
                total_amount_by_date[str_date]=float(amount)
    return total_amount_by_date

def month_names():
    return {1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"}

# This function aggregates the total amount spend by the user in a month.
def aggregate_amount_by_month(filename):
    month_names_dict = month_names()

    month_total_expense = {}
    with open(filename, mode='r',newline='') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            str_date, category, amount, description = row
            date_obj = datetime.strptime(str_date, '%Y-%m-%d')
            month = date_obj.month
            year = date_obj.year
            month_name = month_names_dict[month]
            key = f"{month_name} {year}"
            if key in month_total_expense:
                month_total_expense[key]+= float(amount)
            else:
                month_total_expense[key]= float(amount)
    return month_total_expense

# This function lets the user the view the total expense in a month in a bar graph
def category_based_monthly_expense(filename, target_month):
    target_month = target_month.capitalize()
    category_expense = {}
    month_names_dict = month_names()
    month_changed = False
    with open(filename, mode='r', newline='') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            str_date, category, amount, description = row
            date_obj = datetime.strptime(str_date, '%Y-%m-%d')
            month = date_obj.month
            month_name = month_names_dict[month]
            category = category.lower()
            
            if (month_name == target_month):
                month_changed = True
                if category in category_expense:
                    category_expense[category]+=float(amount)
                else:
                    category_expense[category]=float(amount)
                    
    if not month_changed:
        print(f"No expenses found for month {target_month}.")

    return category_expense
                
# This function ensures that the graph touches zero in case if there is no expense in a day           
def fill_missing_dates(aggregated_data):
    if not aggregated_data:
        return aggregated_data
    
    start_date = min(datetime.strptime(date, '%Y-%m-%d') for date in aggregated_data)
    end_date = max(datetime.strptime(date, '%Y-%m-%d') for date in aggregated_data)
    current_date = start_date

    complete_data = {}
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        complete_data[date_str] = aggregated_data.get(date_str, 0.0)
        current_date += timedelta(days=1)
    
    return complete_data

# This function plots the line chart of spendings

def draw_chart(aggregated_data):
    aggregated_data = fill_missing_dates(aggregated_data)
    dates = []
    spendings = []
    for date_str, spend in sorted(aggregated_data.items()):
        date = datetime.strptime(date_str, '%Y-%m-%d')
        dates.append(date)
        spendings.append(spend)
    plt.style.use('grayscale')
    fig, ax = plt.subplots()
    ax.plot(dates, spendings, marker='o', linewidth=2)
    ax.set_title("Spending per day")
    ax.set_xlabel("", fontsize=14)
    ax.set_ylabel("Amount", fontsize=14)
    ax.tick_params(labelsize=14)
    
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()
    plt.show()

#This function draws a bar chart based on the month expenses of the user.
def draw_month_chart(aggregated_monthly_data):
    months = []
    spendings = []
    for month, spend in sorted(aggregated_monthly_data.items()):
        months.append(month)
        spendings.append(spend)
    fig, ax = plt.subplots(1, 1)
    bars = ax.bar(months, spendings, width=0.2, align='center')

    # Adjust x-axis limits to ensure bars are positioned well
    num_bars = len(months)
    ax.set_xlim(-0.5, num_bars - 0.5)
    
    # Optionally, adjust x-ticks to match your bars
    ax.set_xticks(range(num_bars))
    ax.set_xticklabels(months)
    plt.xlabel("Months")
    plt.ylabel("Spendings")
    plt.title("Spendings per Month")
    plt.show()


# This function display the category based expense with a month in a donut graph
def category_monthly_chart(aggregated_monthly_data):
    categories = list(aggregated_monthly_data.keys())
    spendings = list(aggregated_monthly_data.values())

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(aspect="equal"))
    wedges, texts, autotexts = ax.pie(
        spendings,  # Values (sizes) for the pie chart
        labels=categories,  # Labels for the categories
        autopct='%1.1f%%',  # Format of percentage labels
        startangle=140,  # Start angle of the pie chart
        wedgeprops=dict(width=0.4)  # Width for the donut effect
    )
    
    # Beautify the plot
    ax.set_title("Expenses by Category")
    plt.setp(autotexts, size=10, weight="bold")
    plt.setp(texts, size=12)
    
    plt.show()

#The function below amends the data entered by the user in a CSV file. It also checks if the file exists or not. If the file exits it appends the data as a new row otherwise creates a header in the file
def amend_data(filename, headers = ["Date", "Category", "Amount", "Description"] ):
    df = pd.DataFrame(expense_details(), columns=headers)

    file_exist = os.path.isfile(filename)

    with open(filename, mode = 'a', newline='') as file:
        writer = csv.writer(file)
        if not file_exist:
            writer.writerow(headers)
        writer.writerows(df.values.tolist())
    print(f"Data {df} has been written to {filename}")
    display_file(filename)


# This function displays data for in the prompt for data management including sorting and filtering
def display_file(filename):
    try:
        df = pd.read_csv(filename)
    except FileNotFoundError:
        print("File not found.")
        return None
    except pd.errors.EmptyDataError:
        print("File is empty.")
        return None
    print("Current Data:")
    df.index += 1
    print(df.to_string(index=True))
    return df


# This function sorts the table on the bases of Date, Category, Amount, and Description
def sort_file(filename):
    df = display_file(filename)
    if df is None:
        return
    
    while True:
        option = input("Would you like to sort in ascending or descending order? Please press A for ascending and D for descending:\n").strip().upper()
        if option == "A":
            option_chosen = True
        elif option == "D":
            option_chosen = False
        else:
            print("Invalid input. Please press A for ascending or D for descending.")
            continue
        try:
            ask_user = int(input("How would you like to sort:\nEnter 1 by Date:\nEnter 2 by Category:\nEnter 3 by Amount:\nEnter 4 by Description:"))
        
            if ask_user == 1: 
                rslt_df = df.sort_values( by = 'Date', ascending=option_chosen)
        

            elif ask_user == 2:
                df['Category'] = df['Category'].str.capitalize()
                rslt_df = df.sort_values( by = 'Category', ascending=option_chosen)

            elif ask_user == 3:
                rslt_df = df.sort_values( by = 'Amount', ascending=option_chosen)
   
            elif ask_user == 4:
                rslt_df = df.sort_values( by = 'Description', ascending=option_chosen)

            else:
                print("Wrong Number, Please choose between 1 and 4")
                continue
            rslt_df.reset_index(drop=True, inplace=True)
            rslt_df.index +=1
            
            print (rslt_df.to_string(index=True))
            break

        except ValueError:
            print("Please enter a number between 1 and 4")

# This is the base function for filtering the data
def filter_data(filename):
    df = display_file(filename)
    if df is None or df.empty:
        print("The data file is empty or could not be loaded.")
        return
    
    while True:
        filter_option = input("Enter 'A' to sort by Date\nEnter 'B' to sort by Amount\nEnter 'C' to filter by category").lower()
        
        if filter_option == 'a':
            filter_date(df)
        elif filter_option == 'b':
            filter_amount(df)
        elif filter_option == 'c':
            filter_category(df)
        else:
            print("Invalid option, please choose 'A', 'B' or 'C'.")
            continue
        break

# This function filters data on the basis on the Date
def filter_date(df):
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Convert min_date and max_date to datetime
    min_date = df['Date'].min()
    max_date = df['Date'].max()

    while True:
        start_date = input("Please Enter Start Date in YYYY-MM-DD format: ")
        end_date = input("Please Enter End Date in YYYY-MM-DD format: ")
        try:
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)

            if not (min_date <= start_date <= max_date) or not (min_date <= end_date <= max_date):
                print("Either one or both dates are out of range.")
                continue

            filtered_data = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

            if filtered_data.empty:
                print("No data found during your required timeframe.")
                continue
        except ValueError:
            print("Please enter dates in the correct format.")
            continue
        
        print("Filtered Data:")
        filtered_data.reset_index(drop=True, inplace=True)
        filtered_data.index += 1
        print(filtered_data.to_string(index=True))
        break

# This function filters data on the bases of amount
def filter_amount(df):
    min_amount = df['Amount'].min()
    max_amount = df['Amount'].max()

    while True:
        user_amount = input("Enter 'L' to find amounts less than a specific number\nEnter 'G' to find amounts greater than a specific number\n").lower()
        
        if user_amount == "l":
            try:
                entered_amount = float(input("Enter the number: "))
                if entered_amount > min_amount:
                    filtered_data = df[df['Amount'] < entered_amount]
                else:
                    print("No data to show as you entered a value less than the minimum value.")
                    continue
            except ValueError:
                print("Please enter a correct value ")
                continue

        elif user_amount == "g":
            try:
                entered_amount = float(input("Enter the number: "))
                if entered_amount < max_amount:
                    filtered_data = df[df['Amount'] > entered_amount]
                else:
                    print("No data to show as you entered a value greater than the maximum value.")
                    continue
            except ValueError:
                print("Please enter a correct value ")
                continue
        else:
            print("Wrong entry, please choose between 'L' and 'G'.")
            continue
                
        print("Filtered Data:")
        filtered_data.reset_index(drop=True, inplace=True)
        filtered_data.index += 1
        print(filtered_data.to_string(index=True))
        break

# This function filters data on the basis of categories
def filter_category(df):
    categories = list(set(sorted(df['Category'].str.lower())))
    
    for index, value in enumerate(categories, start=1):
        print(f"{index}. {value.capitalize()}")

    while True:
        choose_category = input("Enter the category you want to filter with: ").lower()

        if choose_category in categories:
            filtered_data = df[df['Category'].str.lower() == choose_category]
            print("Filtered Data:")
            filtered_data.reset_index(drop=True, inplace=True)
            filtered_data.index += 1
            print(filtered_data.to_string(index=True))
            break
        else:
            print("Please enter a valid category.")


# This function deletes the data in the file and resets the index        
def delete_row(filename, row_to_del):
    df = display_file(filename)
    if df is None:
        return

    # Check if the row_to_del is within the valid range
    if row_to_del < 1 or row_to_del > len(df):
        print(f"{row_to_del} is out of range")
        return

    # Adjust index to match user's choice
    df.index = range(1, len(df) + 1)

    # Drop the row from DataFrame
    df = df[df.index != row_to_del]

    # Reset index after dropping the row
    df.reset_index(drop=True, inplace=True)
    df.index += 1

    # Write the updated DataFrame back to CSV
    df.to_csv(filename, index=False)

    print(f"Row {row_to_del} has been deleted\n")
    print("Updated Data:")
    display_file(filename)

# This function opens the data in the CSV
def open_csv(filename):
    path = Path(filename)
    print("The record file will open in your default browser: ")
    if path.exists():
        if (platform.system() == 'Darwin'):
            subprocess.call(('open', path))
        elif (platform.system() == 'Windows'):
            os.startfile(path)
        else:
            subprocess.call(['xdg-open', path])
    else:
        print("File Not Found")
        
    


filename = "expenses.csv"
while True:

    ask_user = input("Press 1 to expense data:\nPress 2 to delete a row:\nPress 3 to display a daily chart:\nPress 4 to display monthly spendings:\nPress 5 to display monthly category based spending:\nPress 6 to open your record:\nPress 7 to sort the current data:\nPress 8 to filter current data:")
    
    if (ask_user == "1"):
        amend_data(filename)
        break

    elif ask_user == "2":
        try:
            # Display the current DataFrame before asking for deletion
            df = pd.read_csv(filename)
            df.index = df.index + 1  # Adjust index to start from 1
            print("Current Data:")
            print(df.to_string(index=True))
            
            row_to_del = int(input("Please Enter row to delete: "))
            
            # Call delete_row function with the row number
            delete_row(filename, row_to_del)
            break
        except ValueError:
            print("Invalid Input, please try again.")
        except FileNotFoundError:
            print("File not found.")
        except pd.errors.EmptyDataError:
            print("File is empty.")

    elif ask_user == "3":
        aggregated_data = aggregate_amount(filename)
        draw_chart(aggregated_data)
        break

    elif ask_user == "4":
        monthly_aggregated_data = aggregate_amount_by_month(filename)
        draw_month_chart(monthly_aggregated_data)
        break
    
    elif ask_user == "5":
        target_month = "August"
        aggregated_monthly_data = category_based_monthly_expense(filename, target_month)
        category_monthly_chart(aggregated_monthly_data)
        
    elif ask_user == "6":
        open_csv(filename)
        break
    elif ask_user == "7":
        sort_file(filename)
        break
    elif ask_user == "8":
        filter_data(filename)
        break
        
        

    else:
        print("Invalid Input, Please Enter 1, 2, 3, 4, 5, 6, 7 or 8")






