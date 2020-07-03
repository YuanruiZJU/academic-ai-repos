from selenium import webdriver

driver = webdriver.Firefox(executable_path='D:\Study\ml_academic_code\geckodriver\geckodriver.exe')  # Optional argument, if not specified will search path.
driver.get('https://scholar.google.com/scholar?q=Joint 3D Face Reconstruction and Dense Alignment with Position Map Regression Network')
html = driver.page_source
print(html)
driver.close()