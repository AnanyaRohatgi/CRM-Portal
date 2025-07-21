import csv

INPUT_CSV = 'encoded-Account_Contact_FinalData_final_2 (1)(mighthave tochabge).csv'         # Your original 95,000-row CSV
OUTPUT_CSV = 'last_48000.csv'       # New CSV with last 48,000 rows

# Read the entire file
with open(INPUT_CSV, encoding='utf-8-sig') as infile:
    reader = list(csv.reader(infile))
    headers = reader[0]
    all_rows = reader[1:]

# Get the last 48,000 rows
last_rows = all_rows[-48000:]

# Write to new CSV
with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(headers)
    writer.writerows(last_rows)

print(f"✅ Done! Extracted {len(last_rows)} rows into {OUTPUT_CSV}")
