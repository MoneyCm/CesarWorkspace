
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

def setup_driver():
    """Initializes and returns a Selenium Chrome WebDriver."""
    # Optional: Add options to run headless or disable notifications
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--headless") 
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def scrape_observatorio():
    """
    Main function to scrape crime data from the Observatorio del Delito dashboard.
    """
    driver = setup_driver()
    wait = WebDriverWait(driver, 20)  # Increased wait time for slow-loading dashboards
    all_data = []

    # --- 1. Definition of Search Parameters ---
    base_url = "https://www.observatoriodeldelitovalle.co/observatorio"
    categorias_delito = ['Hurtos', 'Homicidios', 'Lesiones Personales']
    municipios_a_buscar = ['CALI', 'JAMUNDÍ', 'PALMIRA']
    anos_a_buscar = ['2023', '2024', '2025']

    try:
        # --- 2. Initial Navigation ---
        print("Navigating to the dashboard...")
        driver.get(base_url)
        
        # Wait for a key element of the dashboard to be visible, e.g., the main container or side menu
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "vertical-menu")))
        print("Dashboard loaded successfully.")

        # --- 3. Nested Loop Iteration ---
        for categoria in categorias_delito:
            try:
                print(f"\nProcessing Category: {categoria}")
                # Click on the corresponding category button in the left menu
                # NOTE: This XPath assumes buttons are within a specific menu structure. Adjust if necessary.
                categoria_button_xpath = f"//div[contains(@class, 'vertical-menu')]//a[contains(., '{categoria}')]"
                categoria_button = wait.until(EC.element_to_be_clickable((By.XPATH, categoria_button_xpath)))
                categoria_button.click()
                
                # Wait for a specific element to signal the page has updated, e.g., a chart title
                wait.until(EC.visibility_of_element_located((By.ID, "chart-container"))) # Placeholder ID
                print(f"  - Category '{categoria}' selected.")

            except (NoSuchElementException, TimeoutException) as e:
                print(f"  - ERROR: Could not find or click category '{categoria}'. Skipping. Error: {e}")
                continue

            for municipio in municipios_a_buscar:
                try:
                    print(f"  - Processing Municipality: {municipio}")
                    # Locate and select from the "MUNICIPIO" dropdown
                    # NOTE: The ID 'municipio-select' is a placeholder. Inspect the page to find the correct ID or name.
                    municipio_dropdown_elem = wait.until(EC.presence_of_element_located((By.ID, "municipio-select")))
                    municipio_select = Select(municipio_dropdown_elem)
                    municipio_select.select_by_visible_text(municipio)
                    
                    # Wait for data to refresh
                    wait.until(EC.staleness_of(municipio_dropdown_elem)) # Wait for the old element to go stale
                    print(f"    - Municipality '{municipio}' selected.")

                except (NoSuchElementException, TimeoutException) as e:
                    print(f"    - ERROR: Could not select municipality '{municipio}'. Skipping. Error: {e}")
                    continue

                for ano in anos_a_buscar:
                    try:
                        print(f"    - Processing Year: {ano}")
                        # Locate and select from the "AÑO" dropdown
                        # NOTE: The ID 'ano-select' is a placeholder.
                        ano_dropdown_elem = wait.until(EC.presence_of_element_located((By.ID, "ano-select")))
                        ano_select = Select(ano_dropdown_elem)
                        ano_select.select_by_visible_text(ano)

                        # Wait for the final data table to refresh
                        # This XPath looks for the specific table based on its preceding header
                        table_xpath = "//h5[contains(text(), 'Día de la Semana y Franja Horaria')]/following-sibling::div//table"
                        wait.until(EC.visibility_of_element_located((By.XPATH, table_xpath)))
                        print(f"      - Year '{ano}' selected. Extracting data...")

                        # --- 4. Data Extraction ---
                        data_table = driver.find_element(By.XPATH, table_xpath)
                        rows = data_table.find_elements(By.TAG_NAME, "tr")
                        
                        # Extract headers (optional, if needed)
                        headers = [header.text for header in rows[0].find_elements(By.TAG_NAME, "th")]

                        # Extract data rows
                        for row in rows[1:]:
                            cells = row.find_elements(By.TAG_NAME, "td")
                            if not cells: continue # Skip empty rows

                            row_data = {headers[i]: cell.text for i, cell in enumerate(cells)}
                            row_data['Categoria'] = categoria
                            row_data['Municipio'] = municipio
                            row_data['Ano'] = ano
                            all_data.append(row_data)
                        
                        print(f"      - Extracted {len(rows) - 1} rows of data.")

                    except (NoSuchElementException, TimeoutException) as e:
                        print(f"      - ERROR: Could not select year '{ano}' or extract data. Skipping. Error: {e}")
                        continue
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    finally:
        # --- 5. Cleanup and Data Export ---
        print("\nClosing browser...")
        if driver:
            driver.quit()

        if all_data:
            print(f"\nTotal rows extracted: {len(all_data)}")
            df = pd.DataFrame(all_data)
            
            # Reorder columns to have context first
            context_cols = ['Categoria', 'Municipio', 'Ano']
            data_cols = [col for col in df.columns if col not in context_cols]
            df = df[context_cols + data_cols]

            output_filename = "reporte_final_delitos.csv"
            df.to_csv(output_filename, index=False, encoding='utf-8-sig')
            print(f"Data successfully exported to '{output_filename}'")
        else:
            print("No data was extracted. The output file was not created.")

if __name__ == "__main__":
    scrape_observatorio()
