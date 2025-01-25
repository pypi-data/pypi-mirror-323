import csv

# Function to read a CSV file and store its columns in separate arrays
def read_csv_file(file_path):
    arrays = {}
    
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        
        # Initialize arrays based on headers
        for header in reader.fieldnames:
            arrays[header] = []
        
        # Populate arrays with data from the CSV file
        for row in reader:
            for header in reader.fieldnames:
                arrays[header].append(row[header])
    
    return arrays

# # Example usage
# file_path = 'data.csv'
# arrays = read_csv_file(file_path)

# # Print the arrays
# for key, array in arrays.items():
#     print(f"{key}: {array}")
