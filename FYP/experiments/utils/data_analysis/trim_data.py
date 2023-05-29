import csv


def trim(filename = "example.csv"):
    start_keyword = "start"
    end_keyword = "end"

    # Read the CSV file into a list of dictionaries
    with open(filename, "r") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    # Find the index of the row containing the start keyword
    start_index = None
    for i, row in enumerate(rows):
        if start_keyword in row.values():
            start_index = i
            break

    # Find the index of the row containing the end keyword
    end_index = None
    for i, row in enumerate(rows):
        if end_keyword in row.values():
            end_index = i
            break

    # Remove all rows before the start index and after the end index
    if start_index is not None:
        rows = rows[start_index:]
    if end_index is not None:
        rows = rows[:end_index+1]

    # Write the filtered rows back to the CSV file
    with open(filename, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=reader.fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


trim('C:\\Users\\matil\\Desktop\\FYP\\code_env\\eeg-notebooks\\FYP\\data\\AudioVisual\\1\\3\\synched_data.csv')
