from selenium.common.exceptions import TimeoutException
import re
import pandas as pd
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuración de opciones para Firefox
opts = Options()
opts.add_argument("--start-maximized")

# Inicializar el driver de Firefox
driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(), options=opts)

# Asignar la url en Airbnb de Barcelona
url = 'https://www.airbnb.com/s/Barcelona--Spain/homes'

driver.get(url)
# Lista para almacenar la información de las habitaciones
listaHab = []
# Inicializando el número de paginaciónes el actual y hasta donde se piensa recorrer
max_page = 7
current_page = 1
# Recorrer hasta el número de páginas máxima asignadas
try:
    while current_page <= max_page:
        print(f"Procesando página {current_page}...")
        sleep(3)
        # Extraer la lista de habitaciones de la página principal
        listaHabitacionAirBnB = driver.find_elements(By.XPATH, "//div[@itemprop='itemListElement']")
        # Iterar sobre cada habitación para extraer la información
        for hab in listaHabitacionAirBnB:
            try:
                # Extraer nombre y precio desde la página principal
                nombre = hab.find_element(By.XPATH, ".//div[@data-testid='listing-card-title']").text
                precio = hab.find_element(By.XPATH, ".//span[@class='_11jcbg2']").text
                # Extraer y procesar puntuación y número de reseñas desde la página principal
                cadenaPuntuacion = hab.find_element(By.XPATH, ".//div[contains(@class, 't1a9j9y7')]").text
                patron = r"(\d+\.\d+)\s*\(.*?(\d+)\)"
                resultado = re.search(patron, cadenaPuntuacion)
                puntuacion = 0
                resenias = 0
                if resultado:
                    puntuacion = resultado.group(1)
                    resenias = resultado.group(2)
                # Abrir el detalle de cada habitación en una nueva pestaña    
                link_detalle = hab.find_element(By.XPATH, ".//a[contains(@class, 'rfexzly')]").get_attribute("href")
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[-1])  # Cambiar a la nueva pestaña
                driver.get(link_detalle)  # Ir a la URL del detalle de la habitación

                # Extraer la dirección en la página del detalle
                try:
                    direccion = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'toieuka')]/h2"))
                    ).text
                except TimeoutException:
                    direccion=""
                    print("No se encontró el elemento de dirección en la página de detalle.")
                # Extraer descripción de cuarto en la página del detalle
                try:
                    descripcionCuarto = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'o1kjrihn')]//li[1]"))
                    ).text
                except TimeoutException:
                    descripcionCuarto = "0"
                    print("No se encontró el elemento de dirección en la página de detalle.")
                numeroHabitaciones = re.search(r"\d+", descripcionCuarto)    
                # Guardar los datos en un objeto
                habitacion = {
                    "nombrePropiedad": nombre,
                    "direccion": direccion,
                    "precio": precio,
                    "puntuacion": puntuacion,
                    "resenias": resenias,
                    "numeroHabitaciones": numeroHabitaciones.group()  
                }                    
                listaHab.append(habitacion)
                # Cerrar la pestaña de detalle y regresar a la pestaña principal
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

            except Exception as e:
                print(f"Error inesperado: {e}")        
        # Redirigir a la siguiente página
        try:
            onClickSiguientePagina = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@aria-label, 'Siguiente') or contains(@aria-label, 'Next') or contains(@aria-label, 'Next page')]"))
            )
            onClickSiguientePagina.click()
            current_page += 1
            # Esperar a que la nueva página cargue
            sleep(3)
        except Exception:
            print("No se encontró el botón de la siguiente página o se alcanzó la última página.")
            break

finally:
    # Guardar los resultados en un archivo CSV
    df = pd.DataFrame(listaHab)
    df.to_csv('airbnbBarcelonaScraping.csv', index=False, encoding='utf-16')
    print("Datos guardados en 'airbnbBarcelonaScraping.csv'")
    # Cerrar el navegador
    driver.quit()
