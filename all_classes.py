from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import pandas as pd
from datetime import datetime, timedelta

driver = webdriver.Chrome()

# canvas
login_url = "https://byu.instructure.com/"
driver.get(login_url)
input("Press Enter once logged in to Canvas.")


courses = {
    "class 1": "url1",
    "class 2": "url2",
    "class 3": "url3"
}


today = datetime.today().date()
next_sunday = today + timedelta(days=(6 - today.weekday()))


all_assignments = []


for course_name, url in courses.items():
    driver.get(url)
    time.sleep(1)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    rows = soup.find('table', id='grades_summary').find('tbody').find_all('tr')

    for row in rows:
        name_cell = row.find('th', class_='title')
        if not name_cell:
            continue
        name = name_cell.a.text.strip() if name_cell.a else name_cell.text.strip()

        due_date_cell = row.find('td', class_='due')
        if not due_date_cell:
            continue
        due_date_text = due_date_cell.text.strip()

        if not due_date_text:
            continue

        due_date_parts = due_date_text.split(" by ")
        due_date = datetime.strptime(due_date_parts[0], '%b %d').date().replace(year=today.year)
        if today <= due_date <= next_sunday:
            all_assignments.append([course_name, name, due_date_text])

# learning suite
gradebook_url = "url4"
driver.get(gradebook_url)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-v--353733]")))

soup = BeautifulSoup(driver.page_source, 'html.parser')
assignment_containers = soup.select('div[data-v--353733]')
course_name = "CS 393"

# prevent duplicates
assignment_names = set()

for container in assignment_containers:
    name_element = container.select_one('div.col-start-2.text-sm')
    time_elements = container.select('span > time')

    assignment_name = name_element.get_text().replace("\n", "").replace("\t", "").strip() if name_element else "Not Available"

    if assignment_name in assignment_names:
        continue

    assignment_names.add(assignment_name)

    due_date = "Not Available"
    if len(time_elements) > 1:
        date = time_elements[-2].get_text().strip()
        time = time_elements[-1].get_text().strip().lower()
        

        due_date_text = f"{date} by {time}"


        due_date_text = due_date_text.replace("\xa0", " ").replace(",", "")
        

        date_part = due_date_text.split(" by ")[0].strip()


        print(f"date_only = {date_part}")


        due_date = datetime.strptime(date_part, '%b %d').date().replace(year=today.year)


        if today <= due_date <= next_sunday:
            all_assignments.append([course_name, assignment_name, due_date_text])


df = pd.DataFrame(all_assignments, columns=['Course', 'Assignment Name', 'Due Date'])
df.to_csv('all_assignments.csv', index=False)


driver.quit()
