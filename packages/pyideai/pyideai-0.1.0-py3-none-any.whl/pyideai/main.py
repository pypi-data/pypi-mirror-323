import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.keys import Keys
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

class PyIdeAI:
	"""
	A class to interact with the ideai.dev website using Selenium WebDriver.

	This class provides methods to initialize a web driver, navigate to the ideai.dev site,
	and extract project information based on user prompts. It utilizes BeautifulSoup for HTML
	parsing and supports both Firefox and Chrome browsers.

	Attributes:
		browser (str): "f" for Firefox, "c" for Chrome. Firefox by default.
		driver_options (Options): Options for configuring the selected browser.
		is_shown (bool): Whether the execution should be shown or not. False by default.

	Methods:
		retrieve_similar_projects(user_prompt): Navigates to ideai.dev, submits a user prompt, and returns
												a list of projects extracted from the resulting page.
	"""

	def __init__(self, browser="f", driver_options=None, is_shown=False):
		"""
		Initializes the PyIdeAI class with the specified browser and options.

		Args:
			browser (str): The browser to use ("f" for Firefox, "c" for Chrome).
			driver_options (Options): Options for the selected browser.
			is_shown (bool): Whether to run the browser in headless mode.
		"""
		self.driver_options = driver_options or (FirefoxOptions() if browser == "f" else ChromeOptions())
		
		if not is_shown:
			self.driver_options.add_argument("--headless")  # Run in headless mode

		if browser == "f":
			self.service = FirefoxService(GeckoDriverManager().install())
			self.driver = webdriver.Firefox(service=self.service, options=self.driver_options)
		elif browser == "c":
			self.service = ChromeService(ChromeDriverManager().install())
			self.driver = webdriver.Chrome(service=self.service, options=self.driver_options)
		else:
			raise ValueError("Invalid browser choice. Use 'f' for Firefox or 'c' for Chrome.")

	def retrieve_similar_projects(self, user_prompt):
		"""Navigates to ideai.dev, submits a user prompt, and returns a list of projects."""
		try:
			# Navigate to ideai.dev
			self.driver.get("https://ideai.dev")

			# Wait for the search box to be present and visible
			search_box = WebDriverWait(self.driver, 30).until(
				EC.visibility_of_element_located((By.XPATH, "//textarea[@placeholder='Type your next world-changing idea here.']"))
			)

			# Paste the user prompt into the search box
			search_box.send_keys(user_prompt)

			# Optionally, submit the form (if needed)
			search_box.send_keys(Keys.RETURN)

			# Wait for the "New Idea" button to be present and visible
			WebDriverWait(self.driver, 60).until(
				EC.visibility_of_element_located((By.XPATH, "//button[contains(text(), 'New Idea')]"))
			)

			# Get the page HTML
			page_html = self.driver.page_source
			projects = self.html_to_projects(page_html)
			return projects
		finally:
			# Close the driver
			self.driver.quit()

	def html_to_projects(self, page_html):
		"""Parses the HTML content to extract project titles, descriptions, and links."""
		soup = BeautifulSoup(page_html, 'html.parser')

		# Find all project cards using the exact class name
		project_cards = soup.find_all('div', class_='rounded-lg border border-zinc-200 bg-white text-zinc-950 shadow-sm dark:border-zinc-800 dark:bg-zinc-950 dark:text-zinc-50 w-full')

		# Extract titles, descriptions, and links
		projects = []
		for card in project_cards[:-1]:  # Last one is sign up

			# Extract the title
			title_div = card.find('div', class_='font-semibold tracking-tight cursor-pointer text-left text-lg flex items-center')
			title = title_div.get_text(strip=True) if title_div else None

			# Locate the title element using Selenium instead of BeautifulSoup
			title_element = self.driver.find_element(By.XPATH, f"//div[contains(text(), '{title}')]")
			
			# Simulate click on title_element to navigate to the project details
			self.driver.execute_script("arguments[0].click();", title_element)
			time.sleep(2)  # Wait for the page to load or the JavaScript to execute

			# Switch to the new tab
			self.driver.switch_to.window(self.driver.window_handles[1])

			# Capture the current URL after the click
			link = self.driver.current_url

			# Extract the description
			description_div = card.find('div', class_='text-sm text-zinc-500 dark:text-zinc-400 text-left font-normal')
			description = description_div.text.strip() if description_div else None

			tags_divs = card.find_all('div', class_='inline-flex items-center rounded-full border px-2.5 py-0.5 transition-colors focus:outline-none focus:ring-2 focus:ring-zinc-950 focus:ring-offset-2 dark:border-zinc-800 dark:focus:ring-zinc-300 border-transparent bg-zinc-900 text-zinc-50 hover:bg-zinc-900/80 dark:bg-zinc-50 dark:text-zinc-900 dark:hover:bg-zinc-50/80 text-sm font-medium')
			tags = [tag.get_text(strip=True) for tag in tags_divs]

			# Add the extracted information to the projects list
			projects.append({
				'title': title,
				'description': description,
				'link': link,
				"tags": tags
			})

			# Close the new tab and switch back to the original tab
			self.driver.close()
			self.driver.switch_to.window(self.driver.window_handles[0])

		return projects


