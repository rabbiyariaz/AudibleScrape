import time
import csv
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=chrome_options)
list_of_books = []


def total_pages(page):
    """Get the total number of pages on website."""
    driver.get(f"https://www.audible.com/search?keywords=book&node=18573211011&page={page}")
    div_next_page = driver.find_element(By.ID, "center-4")
    un_list_4 = div_next_page.find_element(By.TAG_NAME, "ul")
    lists_of_pages = un_list_4.find_elements(By.CLASS_NAME, "bc-list-item")[-2]
    totalPages = int(lists_of_pages.text.strip())
    return totalPages


def go_to_next_page(page):
    """Go to the next page"""
    driver.get(f"https://www.audible.com/search?keywords=book&node=18573211011&page={page}")


def scrape_page():
    """Scrape data from the current page."""
    try:
        div_center = driver.find_element(By.ID, "center-3")
        unordered_list = div_center.find_element(By.TAG_NAME, "ul")
        lists = unordered_list.find_elements(By.CSS_SELECTOR, ".bc-list-item.productListItem")

        for book_no, list_ in enumerate(lists):
            book_info = {
                "title": '',
                "images": '',
                "subtitle": '',
                "author": '',
                "narrator": '',
                "runtime": '',
                "release_date": '',
                "language": '',
                "ratings": ''
            }

            # Define field names and their corresponding CSS selectors
            fields = {

                "title": "li h3",
                "images": "picture img",
                "subtitle": ".bc-list-item.subtitle",
                "price": f"buybox-regular-price-{book_no}",
                "author": ".bc-list-item.authorLabel",
                "narrator": ".bc-list-item.narratorLabel",
                "runtime": ".bc-list-item.runtimeLabel",
                "release_date": ".bc-list-item.releaseDateLabel",
                "language": ".bc-list-item.languageLabel",
                "ratings": ".bc-list-item.ratingsLabel"
            }

            for field, selector in fields.items():
                try:
                    # Use CSS selector to find the element and extract text or attribute
                    if field == "images":
                        book_info[field] = list_.find_element(By.CSS_SELECTOR, selector).get_attribute('src')
                    elif field == "price":
                        para = list_.find_element(By.ID, selector)
                        book_info[field] = para.find_elements(By.TAG_NAME, "span")[1].text.strip()
                    else:
                        book_info[field] = list_.find_element(By.CSS_SELECTOR, selector).text.strip()
                except NoSuchElementException:
                    book_info[field] = ''  # Handle missing fields

            list_of_books.append(book_info)
    except NoSuchElementException:
        print("Could not find the book list on this page.")

pages = total_pages(1)
for current_page in range(1, pages + 1):
    scrape_page()
    if current_page == pages:
        break
    go_to_next_page(current_page + 1)
    time.sleep(3)
    print(list_of_books)

csv_file = "books_data.csv"
csv_columns = ["title", "images", "subtitle", "price", "author", "narrator", "runtime", "release_date", "language",
               "ratings"]

try:
    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in list_of_books:
            writer.writerow(data)
    print(f"Data successfully written to {csv_file}")
except IOError:
    print("I/O error occurred while writing to CSV file")
