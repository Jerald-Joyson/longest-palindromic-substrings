# I'm really sorry for this code as I don't know how to set operations in Solr, 
# and I did it by using Google and StackOverflow and also chatgpt 

# https://github.com/Jerald-Joyson/longest-palindromic-substrings


import subprocess
import pysolr
import pandas as pd
from datetime import datetime
import requests

# 1. Function to check collection existence
def checkCollectionExists(p_collection_name):
    command = f"./solr-9.7.0/bin/solr status"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return p_collection_name in result.stdout

# 2. Function to create a collection
def createCollection(p_collection_name):
    if checkCollectionExists(p_collection_name):
        print(f"Collection '{p_collection_name}' already exists.")
    else:
        command = f"./solr-9.7.0/bin/solr create -c {p_collection_name}"
        subprocess.run(command, shell=True)
        print(f"Collection '{p_collection_name}' created.")
        disableAutoCreateFields(p_collection_name)

# 3. Function to disable auto-create fields
def disableAutoCreateFields(p_collection_name):
    command = f"curl http://localhost:8983/solr/{p_collection_name}/config -d '{{\"set-user-property\": {{\"update.autoCreateFields\":\"false\"}}}}'"
    subprocess.run(command, shell=True)
    print(f"Auto-create fields disabled for collection '{p_collection_name}'.")

# 4. Function to format date to Solr's acceptable format
def format_date(date_val):
    if pd.isna(date_val):
        return None
    if isinstance(date_val, (int, float)):
        # Assume it's a Excel-style date (number of days since 1900-01-01)
        return (datetime(1900, 1, 1) + timedelta(days=int(date_val) - 2)).strftime('%Y-%m-%dT%H:%M:%SZ')
    try:
        return datetime.strptime(str(date_val), '%m/%d/%Y').strftime('%Y-%m-%dT%H:%M:%SZ')
    except ValueError:
        return str(date_val)  # If it's not a valid date, return the original string



# 5. Function to index data excluding a specific column
def indexData(p_collection_name, p_exclude_column):
    solr = pysolr.Solr(f'http://localhost:8983/solr/{p_collection_name}')
    try:
        # Get the schema fields
        schema_fields = get_schema_fields(p_collection_name)
        
        df = pd.read_csv('employee_data.csv', encoding='ISO-8859-1')  # Specifying encoding
        df = df.drop(columns=[p_exclude_column])  # Exclude the specified column

        # Rename problematic columns and remove special characters
        df.columns = df.columns.str.replace(' ', '_').str.replace('[^a-zA-Z0-9_]', '')

        # Ensure 'id' field is present
        if 'Employee_ID' in df.columns:
            df = df.rename(columns={'Employee_ID': 'id'})
        elif 'id' not in df.columns:
            df['id'] = df.index.astype(str)

        # Format date fields
        date_columns = ['Hire_Date', 'Exit_Date']
        for col in date_columns:
            if col in df.columns:
                df[col] = df[col].apply(format_date)

        # Convert DataFrame to list of dicts
        records = df.to_dict(orient='records')

        # Clean up field values and remove fields not in the schema
        cleaned_records = []
        for record in records:
            cleaned_record = {}
            for key, value in record.items():
                if key in schema_fields or key == 'id':  # Always include 'id' field
                    if pd.isna(value):
                        cleaned_record[key] = None
                    elif isinstance(value, str):
                        # Remove dollar signs and commas from numeric fields
                        if key in ['Annual_Salary', 'Bonus']:
                            cleaned_record[key] = value.replace('$', '').replace(',', '').strip()
                        # Convert percentage to float
                        elif key == 'Bonus':
                            cleaned_record[key] = float(value.rstrip('%')) / 100 if value else 0.0
                        else:
                            cleaned_record[key] = value
                    else:
                        cleaned_record[key] = value

            # Ensure 'id' is a string
            if 'id' in cleaned_record:
                cleaned_record['id'] = str(cleaned_record['id'])
            else:
                raise ValueError("Record is missing 'id' field")

            cleaned_records.append(cleaned_record)

        solr.add(cleaned_records)
        print(f"Data indexed to collection '{p_collection_name}', excluding column '{p_exclude_column}'.")
    except Exception as e:
        print(f"Error indexing data: {e}")
        raise  # Re-raise the exception to see the full traceback
def get_schema_fields(collection_name):
    schema_url = f"http://localhost:8983/solr/{collection_name}/schema/fields"
    response = requests.get(schema_url)
    if response.status_code == 200:
        fields = response.json()['fields']
        return set(field['name'] for field in fields)
    else:
        raise Exception(f"Failed to get schema fields: {response.text}")

# 6. Function to search by a column value
def searchByColumn(p_collection_name, p_column_name, p_column_value):
    solr = pysolr.Solr(f'http://localhost:8983/solr/{p_collection_name}')
    try:
        results = solr.search(f"{p_column_name}:{p_column_value}")
        print(f"Results for {p_column_name} = {p_column_value} in collection '{p_collection_name}':")
        for result in results:
            print(result)
    except Exception as e:
        print(f"Error during search: {e}")

# 7. Function to get the employee count
def getEmpCount(p_collection_name):
    solr = pysolr.Solr(f'http://localhost:8983/solr/{p_collection_name}')
    results = solr.search("*:*")
    print(f"Total employee count in collection '{p_collection_name}': {results.hits}")
    return results.hits

# 8. Function to delete employee by ID
def delEmpById(p_collection_name, p_employee_id):
    solr = pysolr.Solr(f'http://localhost:8983/solr/{p_collection_name}')
    try:
        solr.delete(id=p_employee_id)
        print(f"Employee with ID '{p_employee_id}' deleted from collection '{p_collection_name}'.")
    except Exception as e:
        print(f"Error deleting employee: {e}")

# 9. Function to get department facets (grouping by department)
def getDepFacet(p_collection_name):
    solr = pysolr.Solr(f'http://localhost:8983/solr/{p_collection_name}')
    try:
        results = solr.search("*:*", **{
            'facet': 'true',
            'facet.field': 'Department'
        })
        print(f"Department facets for collection '{p_collection_name}':")
        facets = results.facets['facet_fields']['Department']
        for i in range(0, len(facets), 2):
            print(f"{facets[i]}: {facets[i + 1]} employees")
        return facets
    except Exception as e:
        print(f"Error fetching department facets: {e}")

# Main Execution Flow
if __name__ == "__main__":
    v_nameCollection = "Hash_Jerald"
    v_phoneCollection = "Hash_3353"

    # Create collections
    createCollection(v_nameCollection)
    createCollection(v_phoneCollection)

    # Get employee count before indexing
    getEmpCount(v_nameCollection)
    getEmpCount(v_phoneCollection)

    # Index data excluding specific columns
    indexData(v_nameCollection, 'Department')
    indexData(v_phoneCollection, 'Gender')

    # Delete a specific employee by ID
    delEmpById(v_nameCollection, 'E02003')

    # Get employee count after deletion
    getEmpCount(v_nameCollection)

    # Search by column
    searchByColumn(v_nameCollection, 'Department', 'IT')
    searchByColumn(v_nameCollection, 'Gender', 'Male')
    searchByColumn(v_phoneCollection, 'Department', 'IT')

    # Get department facets
    getDepFacet(v_nameCollection)
    getDepFacet(v_phoneCollection)