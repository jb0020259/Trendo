from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import pandas as pd
import logging

# ---------- CONFIG ----------
KEYWORD = "cybersecurity"
DOWNLOAD_DIR = os.getcwd()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)
# ----------------------------

def highlight_element(driver, element, duration=1):
    """Highlight an element with a red border"""
    try:
        original_style = element.get_attribute('style')
        driver.execute_script("""
            arguments[0].style.border='3px solid red';
            arguments[0].style.backgroundColor='yellow';
        """, element)
        time.sleep(duration)
        driver.execute_script(f"arguments[0].style='{original_style}'", element)
    except Exception as e:
        logger.error(f"Error highlighting element: {str(e)}")

def setup_browser():
    logger.info("Setting up Chrome browser...")
    chrome_options = Options()
    # chrome_options.add_argument("--headless=new")  # Commented out to show browser
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--start-maximized")
    prefs = {"download.default_directory": DOWNLOAD_DIR}
    chrome_options.add_experimental_option("prefs", prefs)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    logger.info("Browser setup completed successfully")
    return driver

def search_and_download(keyword):
    driver = setup_browser()
    wait = WebDriverWait(driver, 20)
    actions = ActionChains(driver)
    
    try:
        logger.info(f"Navigating to Google Trends for keyword: {keyword}")
        driver.get("https://trends.google.com/trends")
        logger.info("Page loaded successfully")
        
        # Wait for and handle cookie consent if present
        try:
            logger.info("Checking for cookie consent popup...")
            cookie_button = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Accept all')]")))
            highlight_element(driver, cookie_button)
            logger.info("Cookie consent button found and highlighted")
            cookie_button.click()
            logger.info("Cookie consent handled successfully")
        except Exception as e:
            logger.info("No cookie consent popup found or already accepted")
        
        # Wait for and find the search box
        logger.info("Looking for Explore button...")
        try:
            # Find and click the Explore button
            explore_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Explore')]")))
            highlight_element(driver, explore_button)
            logger.info("Explore button found and highlighted")
            
            # Click the button to navigate to search page
            actions.move_to_element(explore_button).click().perform()
            logger.info("Clicked Explore button")
            time.sleep(3)  # Wait for navigation
            
            # Now find and interact with the search input on the new page
            logger.info("Looking for search input with label 'Add a search term'...")
            search_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@aria-label='Add a search term']")))
            highlight_element(driver, search_input)
            logger.info("Search input field found and highlighted")
            
            # Clear and enter search term
            search_input.clear()
            search_input.send_keys("gold price")
            logger.info("Entered search term: gold price")
            search_input.send_keys(Keys.RETURN)
            logger.info("Search submitted")
            
        except Exception as e:
            logger.error(f"Error during search interaction: {str(e)}")
            logger.error("Stack trace:", exc_info=True)
            raise

        # Wait for results to load
        logger.info("Waiting for search results to load...")
        time.sleep(5)
        
        # Try to find and click "Explore more" if present
        try:
            logger.info("Looking for 'Explore more' button...")
            explore_more = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Explore more')]")))
            highlight_element(driver, explore_more)
            logger.info("'Explore more' button found and highlighted")
            actions.move_to_element(explore_more).click().perform()
            logger.info("Clicked 'Explore more' button")
            time.sleep(5)
        except Exception as e:
            logger.info("No 'Explore more' button found or not needed")

        # Wait for and click the download button
        logger.info("Looking for download button...")
        download_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Download CSV']")))
        highlight_element(driver, download_button)
        logger.info("Download button found and highlighted")
        
        actions.move_to_element(download_button).click().perform()
        logger.info("Download button clicked")
        time.sleep(5)

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        logger.error("Stack trace:", exc_info=True)
    finally:
        logger.info("Closing browser...")
        driver.quit()
        logger.info("Browser closed successfully")

def find_latest_csv():
    logger.info("Looking for the most recent CSV file...")
    files = [f for f in os.listdir(DOWNLOAD_DIR) if f.endswith(".csv")]
    files = sorted(files, key=lambda x: os.path.getmtime(os.path.join(DOWNLOAD_DIR, x)), reverse=True)
    latest_file = os.path.join(DOWNLOAD_DIR, files[0]) if files else None
    if latest_file:
        logger.info(f"Found latest CSV file: {latest_file}")
    else:
        logger.warning("No CSV files found in the download directory")
    return latest_file

def parse_csv_to_data(file_path):
    logger.info(f"Parsing CSV file: {file_path}")
    df = pd.read_csv(file_path)
    df = df.dropna()
    df.columns = [col.strip() for col in df.columns]
    logger.info(f"CSV parsed successfully. Found {len(df)} rows of data")
    return df

def generate_html(df, keyword):
    logger.info("Generating HTML chart...")
    labels = df[df.columns[0]].tolist()
    data = df[df.columns[1]].tolist()

    chart_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Google Trends for {keyword}</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                max-width: 1000px;
                margin: 0 auto;
                background-color: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }}
            h2 {{
                color: #333;
                text-align: center;
                margin-bottom: 30px;
            }}
            canvas {{
                margin: 20px auto;
                display: block;
            }}
            .stats {{
                margin-top: 20px;
                padding: 15px;
                background-color: #f8f9fa;
                border-radius: 5px;
            }}
            .stats p {{
                margin: 5px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Trend Analysis for "{keyword}"</h2>
            <canvas id="trendChart" width="900" height="400"></canvas>
            <div class="stats">
                <p><strong>Data Points:</strong> {len(df)}</p>
                <p><strong>Date Range:</strong> {labels[0]} to {labels[-1]}</p>
                <p><strong>Average Interest:</strong> {sum(data)/len(data):.2f}</p>
                <p><strong>Peak Interest:</strong> {max(data)}</p>
            </div>
        </div>
        <script>
            const ctx = document.getElementById('trendChart').getContext('2d');
            const trendChart = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: {labels},
                    datasets: [{{
                        label: 'Search Interest',
                        data: {data},
                        borderWidth: 2,
                        borderColor: '#4CAF50',
                        backgroundColor: 'rgba(76, 175, 80, 0.1)',
                        fill: true,
                        tension: 0.3
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        title: {{
                            display: true,
                            text: 'Google Trends Analysis'
                        }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            title: {{
                                display: true,
                                text: 'Interest Over Time'
                            }}
                        }},
                        x: {{
                            title: {{
                                display: true,
                                text: 'Date'
                            }}
                        }}
                    }}
                }}
            }});
        </script>
    </body>
    </html>
    """
    with open("trend_chart.html", "w") as f:
        f.write(chart_html)
    logger.info("HTML chart generated successfully: trend_chart.html")

# Run Everything
if __name__ == "__main__":
    logger.info("Starting Google Trends Analysis...")
    search_and_download(KEYWORD)
    logger.info("Data collection completed")
    
    logger.info("Processing downloaded data...")
    csv_file = find_latest_csv()
    df = parse_csv_to_data(csv_file)
    
    logger.info("Generating visualization...")
    generate_html(df, KEYWORD)
    logger.info("Analysis completed successfully!")