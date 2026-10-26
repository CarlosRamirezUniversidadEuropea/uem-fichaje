from playwright.sync_api import sync_playwright
from datetime import date, timedelta, datetime
from pathlib import Path

ORACLE_URL = (
    "https://emer.fa.em3.oraclecloud.com/hcmUI/faces/"
    "FndOverview?fndGlobalItemNodeId=itemNode_my_information_absences1"
)

LOG_FILE = Path(__file__).parent / "timesheet.log"

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(message)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} - {message}\n")

def next_weekday(target_weekday):
    today = date.today()
    days_ahead = target_weekday - today.weekday()

    if days_ahead <= 0:
        days_ahead += 7

    return today + timedelta(days=days_ahead)


def create_entry(page, day, first_entry=True):
    # Open Request Time Changes
    if first_entry:
        page.get_by_role(
            "link",
            name="Time and Absences"
        ).click()

        page.wait_for_timeout(2000)

    page.get_by_text(
        "Request Time Changes"
    ).click()

    page.wait_for_timeout(2000)

    page.get_by_title("Select Date").click()

    page.get_by_role(
        "gridcell",
        name=str(day.day)
    ).last.click()

    page.wait_for_timeout(3000)

    page.get_by_role("button", name="Add").click()

    page.get_by_role(
        "textbox",
        name="Número de asignación"
    ).click()

    page.wait_for_timeout(3000)

    page.get_by_text("E07133-").click()

    # Start time 10:00
    page.get_by_title("Select Time").first.click()
    
    page.get_by_role("spinbutton",name="Select Hours").get_by_text("10", exact=True).click(force=True)

    page.locator(
        '[id="__af_Z_window"]'
    ).get_by_role(
        "button",
        name="OK"
    ).click()

    page.wait_for_timeout(3000)

    # End time 17:00
    page.get_by_title("Select Time").nth(1).click()

    page.wait_for_timeout(3000)

    page.get_by_role("spinbutton",name="Select Hours").get_by_text("17").click(force=True)

    page.locator(
        '[id="__af_Z_window"]'
    ).get_by_role(
        "button",
        name="OK"
    ).click()

    page.wait_for_timeout(3000)

    page.get_by_role(
        "textbox",
        name="Comments"
    ).fill("jornada laboral")

    page.wait_for_timeout(2000)

    page.get_by_role(
        "button",
        name="OK"
    ).click()

    page.wait_for_timeout(2000)

    page.get_by_role(
        "button",
        name="Submit"
    ).click()

    page.wait_for_timeout(2000)


with sync_playwright() as p:

    context = p.chromium.launch_persistent_context(
        user_data_dir=r"C:\Temp\oracle-playwright-profile",
        channel="msedge",
        headless=False
    )

    page = context.new_page()

    page.goto(
        "https://emer.fa.em3.oraclecloud.com/hcmUI/faces/FuseWelcome"
    )

    print()
    print("=" * 80)
    print("LOGIN TO ORACLE IF NEEDED")
    print("When you can see the Oracle home page, press ENTER here.")
    print("=" * 80)

    input()

    # Oracle login may have closed the original tab and opened another one
    page = context.pages[-1]

    print("Current URL:", page.url)

    page.wait_for_timeout(3000)

    tuesday = next_weekday(1)
    thursday = next_weekday(3)

    try:
        log(f"Submitting Tuesday {tuesday}")
        create_entry(page, tuesday, first_entry=True)
        log(f"Successfully submitted Tuesday {tuesday}")

    except Exception as e:
        page.screenshot(path="error_tuesday.png")
        log(f"ERROR Tuesday: {e}")

    try:
        log(f"Submitting Thursday {thursday}")
        create_entry(page, thursday, first_entry=False)
        log(f"Successfully submitted Thursday {thursday}")

    except Exception as e:
        page.screenshot(path="error_thursday.png")
        log(f"ERROR Thursday: {e}")

    log("Finished")

    context.close()
