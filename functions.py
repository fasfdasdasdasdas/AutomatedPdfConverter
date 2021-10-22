import os
from tabula.io import read_pdf
import pandas as pd
import numpy as np
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup as soup
import requests
import re
import ssl

def getPdfFiles(home_url, dir_url,filedir):
    # Create Unverified http context
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        # Legacy Python that doesn't verify HTTPS certificates by default
        pass
    else:
        # Handle target environment that doesn't support HTTPS verification
        ssl._create_default_https_context = _create_unverified_https_context

    url = home_url + dir_url

    # Create file if not created
    if not os.path.exists(filedir):
        os.makedirs(filedir)

    #Setup BeautifulSoup webpage acccess
    page = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        webpage = urlopen(page).read()
    except HTTPError as e:
        print('Error code: ', e.code)
        return None
    except URLError as e:
        print('Reason: ', e.reason)
    else:
        soup_page = soup(webpage, "html.parser")

        pdf_link = soup_page.findAll("a")

        urls = []
        names = []
        for link in pdf_link:
            # Find all urls in webpage
            if home_url in link.get('href'):
                full_url = link.get('href')
            else:
                full_url = home_url + link.get('href')

            # Find the ones that end with pdf
            if full_url.endswith(".pdf"):
                # Get the company name and the URL for the pdf
                urls.append(full_url)
                names.append(link.getText())

        name_url = zip(names, urls)
        # Download all of the PDFs into the folder specified
        for name, url in name_url:
            f = open(filedir + name + '.pdf', 'wb')
            url_request = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            webpage = urlopen(url_request).read()
            f.write(webpage)
            f.close()

def mergePdfFiles(filedir, year):
    column_names = ['Name of Health Consumer Organisation', 'Description of and/or purpose of support', 'Nature of Support(monetary value or equivalent) or description of non financial support']
    full_column_names = ['Year', 'Company Name', 'Name of Health Consumer Organisation', 'Description of and/or purpose of support', 'Nature of Support(monetary value or equivalent) or description of non financial support']
    
    # Merging Files
    combined_df = pd.DataFrame(columns=full_column_names)

    for filename in os.listdir(filedir):
        try:
            # Reading pdf
            dfs = read_pdf(filedir + filename, pages="all", guess = True, lattice = True)
            # Columns checking as a few of the pdfs do not read properly
            if len(dfs[0].columns) != 3:
                if len(dfs) > 1:
                    # Check the error company files and may have to do it manually
                    print("Error on " + filename)
                    continue
            # Iterate through the multiple pages
            for df in dfs:
                df.reset_index(drop=True, inplace=True)
                df.columns = df.columns.str.replace('\r', ' ')
                if df.columns[0] == column_names[0]:
                    # Change Column names to standarize
                    df.columns = column_names
                else:
                    new_df = pd.DataFrame([df.columns.values.tolist()], columns=column_names)
                    df.columns = column_names
                    dfs.append(new_df)

            # Check for empty pdfs
            if len(df.index) == 0: 
                print(filename + " is empty")
            
            # Merge all of the separate pages
            merged = pd.concat(dfs)
            merged.reset_index(drop=True, inplace = True)
            # Add new variable 
            merged['Company Name'] = os.path.splitext(filename)[0]
            merged['Year'] = year
            # Combine all of the files into one file
            combined_df = pd.concat([combined_df, merged])
            combined_df.reset_index(drop=True, inplace=True)
        except:
            print("Error on " + filename + ": Please check manually")
            continue

    # Adding another column for cleaned data
    combined_df = combined_df.fillna("Nothing... Please Check Values")

    # Turn it into a csv file
    combined_df.to_csv(filedir + str(year) + ".csv")
    print("Complete: csv file located at: "+ filedir)

def main():
    home_url = 'https://www.medicinesaustralia.com.au'
    dir_url = '/code-of-conduct/transparency-reporting/health-consumer-organisation-support-reports/member-company-reports/'
    filedir = "C:/Users/dt381/OneDrive/Desktop/test"
    year = 2020

    getPdfFiles(home_url, dir_url, filedir + "/")
    mergePdfFiles(filedir + "/", year)

if __name__ == "__main__":
    main()

