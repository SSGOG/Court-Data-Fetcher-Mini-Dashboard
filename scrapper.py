import os
import time
import requests
from bs4 import BeautifulSoup

CAPTCHA_API_KEY = os.getenv("CAPTCHA_API_KEY")

def fetch_case(case_type, case_number, filing_year):
    base_url = "https://delhihighcourt.nic.in/case-status"  # example
    session = requests.Session()
    # initial GET to get view state / cookies
    resp = session.get(base_url)
    soup = BeautifulSoup(resp.text, "html.parser")
    print("Response URL:", resp.url)
    print("HTML length:", len(resp.text))
    with open("page_debug.html", "w", encoding="utf-8") as f:
        f.write(resp.text)
    # locate hidden form inputs
    viewstate_tag = soup.find("input", {"name": "__VIEWSTATE"})
    eventvalidation_tag = soup.find("input", {"name": "__EVENTVALIDATION"})

    if not viewstate_tag or not eventvalidation_tag:
        raise Exception("Required form fields not found — check if site layout changed or access is blocked.")

    viewstate = viewstate_tag["value"]
    eventvalidation = eventvalidation_tag["value"]
    # if there's CAPTCHA image:
    captcha_img = soup.find("img", id="captchaImage")
    if captcha_img:
        img_url = captcha_img["src"]
        img_resp = session.get(img_url)
        # send to 2captcha
        import base64
        b64 = base64.b64encode(img_resp.content).decode()
        # submit to 2captcha
        r = requests.post("http://2captcha.com/in.php", data={
            'key': CAPTCHA_API_KEY,
            'method': 'base64',
            'body': b64,
            'json': 1
        }).json()
        captcha_id = r['request']
        # poll result
        time.sleep(20)
        r2 = requests.get("http://2captcha.com/res.php", params={
            'key': CAPTCHA_API_KEY, 'action': 'get', 'id': captcha_id, 'json': 1
        }).json()
        captcha_text = r2['request']
    else:
        captcha_text = ""
    # build POST payload
    payload = {
      "__VIEWSTATE": viewstate,
      "__EVENTVALIDATION": eventvalidation,
      "ddlCaseType": case_type,
      "txtCaseNo": case_number,
      "txtYear": filing_year,
      "txtCaptcha": captcha_text,
      "btnSearch": "Search"
    }
    post = session.post(base_url, data=payload)
    page = BeautifulSoup(post.text, "html.parser")
    # parse results
    parties = page.find("span", id="lblParties").text.strip()
    filing_date = page.find("span", id="lblFilingDate").text.strip()
    next_hearing = page.find("span", id="lblNextDate").text.strip()
    orders = []
    table = page.find("table", id="tblOrders")
    for row in table.find_all("tr")[1:]:
        cols = row.find_all("td")
        date = cols[0].text.strip()
        link = cols[1].find("a")["href"]
        orders.append({'date': date, 'pdf_url': session.get(link).url})
    latest = orders[0] if orders else None
    return {
      'parties': parties,
      'filing_date': filing_date,
      'next_hearing': next_hearing,
      'latest_order': latest,
      'raw_html': post.text
    }

