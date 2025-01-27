import requests
import pandas as pd
import time
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import webbrowser

# ------------------------------
# 1. CONFIGURATION
# ------------------------------
API_KEY = "AIzaSyBxLaZhQrcsr7RkV0TYP0j7VSenOSp72Ps"  # Replace with your actual API key
SEARCH_ENGINE_ID = "23aa25eba259f41c7"  # Replace with your Custom Search Engine ID

# Terms you want to search for:
SEARCH_TERMS = [
    "homeschooling",
    "home educating",
    "unschooling",
    "autodidactic",
    "learning outside of school"
    # add more variations if desired
]

# Number of search results you want per term (max 10 per request in free tier).
# You can paginate if you want more results, but be mindful of query limits.
NUM_RESULTS = 10

# Output Excel file path/name:
OUTPUT_EXCEL_FILE = "homeschool_articles.xlsx"

# SQLite database file path/name:
DB_FILE = "homeschool_articles.db"


# ------------------------------
# 2. HELPER FUNCTION: SEARCH GOOGLE
# ------------------------------
def google_search(query, api_key, cse_id, num_results=10, start_index=1):
    """
    Performs a Google Custom Search using the provided query.
    """
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": api_key,
        "cx": cse_id,
        "num": num_results,     # up to 10 for free tier
        "start": start_index,   # pagination start
        "hq": "Ontario, Canada"
    }
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: Received status code {response.status_code} for query '{query}'")
        return None


# ------------------------------
# 3. MAIN SCRIPT LOGIC
# ------------------------------
def save_to_db(records):
    """
    Save the records to a SQLite database.
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS articles
                 (SearchTerm TEXT, Title TEXT, Snippet TEXT, Link TEXT UNIQUE, DateAccessed TEXT)''')
    
    for record in records:
        c.execute('''INSERT OR IGNORE INTO articles (SearchTerm, Title, Snippet, Link, DateAccessed)
                     VALUES (?, ?, ?, ?, ?)''', 
                  (record["SearchTerm"], record["Title"], record["Snippet"], record["Link"], record["DateAccessed"]))
    
    conn.commit()
    conn.close()

def aggregate_articles():
    """
    Aggregate articles based on the search terms and save them to a SQLite database.
    """
    # A list to hold all records
    all_records = []

    # Connect to the database to fetch existing links
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT Link FROM articles")
    existing_links = {row[0] for row in c.fetchall()}
    conn.close()

    # Loop through each search term
    for term in SEARCH_TERMS:
        start_index = 1
        while start_index <= 100:  # Limit pagination to 100 results
            search_data = google_search(term, API_KEY, SEARCH_ENGINE_ID, NUM_RESULTS, start_index)
            
            if not search_data or "items" not in search_data:
                break

            new_records = []
            for item in search_data["items"]:
                link = item.get("link")
                if link not in existing_links:
                    record = {
                        "SearchTerm": term,
                        "Title": item.get("title"),
                        "Snippet": item.get("snippet"),
                        "Link": link,
                        "DateAccessed": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    new_records.append(record)
                    existing_links.add(link)

            if not new_records:
                break

            all_records.extend(new_records)
            start_index += NUM_RESULTS

            time.sleep(1)  # Sleep to avoid hitting API rate limits

    save_to_db(all_records)
    print(f"Saved {len(all_records)} new articles to the database.")

def open_link(event):
    item = tree.selection()[0]
    link = tree.item(item, "values")[3]
    webbrowser.open(link)

def display_results_in_main_window():
    """
    Display the results from the SQLite database in the main GUI window.
    """
    for row in tree.get_children():
        tree.delete(row)

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM articles")
    rows = c.fetchall()
    conn.close()

    for row in rows:
        tree.insert("", tk.END, values=row)

    # Dynamically resize columns based on the length of the output string in each field
    for col in tree["columns"]:
        max_width = min(max([len(str(tree.set(k, col))) for k in tree.get_children()] + [len(col)]) * 10, 600)
        tree.column(col, width=max_width)

def run_aggregate_articles():
    try:
        aggregate_articles()
        messagebox.showinfo("Success", "Articles aggregated and saved successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def display_existing_results():
    """
    Display existing results from the SQLite database if available.
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM articles")
    rows = c.fetchall()
    conn.close()

    if rows:
        for row in rows:
            tree.insert("", tk.END, values=row)

def create_db_if_not_exists():
    """
    Create the SQLite database and articles table if they do not exist.
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS articles
                 (SearchTerm TEXT, Title TEXT, Snippet TEXT, Link TEXT UNIQUE, DateAccessed TEXT)''')
    conn.commit()
    conn.close()

def main():
    global tree

    create_db_if_not_exists()  # Ensure the database and table are created

    root = tk.Tk()
    root.title("OFTP News")

    label = tk.Label(root, text="Welcome to OFTP News!")
    label.pack(pady=10)

    button_aggregate = tk.Button(root, text="Aggregate Articles", command=run_aggregate_articles)
    button_aggregate.pack(pady=10)

    button_display = tk.Button(root, text="Display Results", command=display_results_in_main_window)
    button_display.pack(pady=10)

    tree = ttk.Treeview(root, columns=("SearchTerm", "Title", "Snippet", "Link", "DateAccessed"), show='headings')
    tree.heading("SearchTerm", text="Search Term")
    tree.heading("Title", text="Title")
    tree.heading("Snippet", text="Snippet")
    tree.heading("Link", text="Link")
    tree.heading("DateAccessed", text="Date Accessed")
    
    tree.pack(expand=True, fill=tk.BOTH)
    tree.bind("<Double-1>", open_link)

    display_existing_results()

    root.mainloop()

# ------------------------------
# 4. RUN THE SCRIPT
# ------------------------------
if __name__ == "__main__":
    main()