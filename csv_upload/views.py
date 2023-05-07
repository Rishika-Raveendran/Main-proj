import os
from django.shortcuts import render
from .models import *
from .forms import *
import pandas as pd
from datetime import datetime
from io import StringIO
from pymongo import MongoClient
import csv
# from .settings import MONGO_URI


def clean_csv(csv_file):
    # Read in the CSV file
    df = pd.read_csv(csv_file)

    # delete some columns
    df = df[['Product', 'Quantity Ordered']]

    df['Quantity Ordered'] = pd.to_numeric(
        df['Quantity Ordered'], errors='coerce')

    # Drop any rows with missing data
    df = df.dropna()

    # Remove any leading or trailing whitespace from column names
    df.columns = df.columns.str.strip()

    # Convert any string columns to lowercase
    string_columns = df.select_dtypes(include='object').columns
    df[string_columns] = df[string_columns].apply(lambda x: x.str.lower())

    # Grouping and calculatig total sales
    sum_df = df.groupby('Product')['Quantity Ordered'].sum().reset_index()

    # get today's datetime
    now = datetime.now()

    # Adding month column
    sum_df['MONTH'] = now.strftime('%B')
    sum_df['shop_id']=1

    # If merge required
    result_df = pd.DataFrame()
    # if merge == True:
    #     fetched_df = pd.read_csv(fetched)
    #     result_df = pd.merge(
    #         fetched_df , sum_df, on=['Product', 'Quantity Ordered', 'MONTH'], how='outer')
    # else:
    # result_df = sum_df
    result_df = sum_df

    # Return the cleaned DataFrame
    return result_df.to_csv(index=False)
# Create your views here.


def upload_csv(request, pk=None):
    connection_string = 'mongodb+srv://chainaid:7XKgw7yjs1ZBkkEn@cluster0.1n1dhzf.mongodb.net/?retryWrites=true&w=majority'
    client = MongoClient(connection_string)

    db = client['ChainAid']

    # collection object
    collection = db['shopsales']
    form = CsvFileForm()
    if request.method == 'POST':
        form = CsvFileForm(request.POST, request.FILES)
        if form.is_valid():
            # Extracting information from the submitted form
            csvFile = form.cleaned_data['csv_file']
            branch = form.cleaned_data['branch']

            # csv_queryset = CSVModel.objects.filter(branch=branch)
            # # If record already exists, merge csv with already existing csv
            # if csv_queryset.exists():
            #     csv_obj = csv_queryset.first()
            #     fetched_csv = csv_obj.csv_file
            #     cleaned_csv_str = clean_csv(csvFile, True, fetched_csv)
            #     cleaned_csv = StringIO(cleaned_csv_str)
            #     csv_obj.csv_file.save('updated_csv.csv', cleaned_csv)
            #     csv_obj.save()

            # # Else create a new  record
            # else:
            cleaned_csv_str = clean_csv(csvFile)
            cleaned_csv = StringIO(cleaned_csv_str)
            # csv_entry = CSVModel()
            # csv_entry.branch = branch
            # csv_entry.csv_file.save('updated_csv.csv', cleaned_csv)
            # csv_entry.save()
            # parsing the csv and saving to the database

            # MONGODB WORKS HERE
            # Create a CSV reader object
            reader = csv.DictReader(cleaned_csv)

            # Loop through each row of the CSV file
            for row in reader:
                # Insert the row as a document into the collection
                collection.insert_one(row)

    context = {'form': form}
    return render(request, 'csvs/upload.html', context)
