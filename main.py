#!/usr/bin/env pipenv-shebang
import os
import time
import datetime
import logging.config

import yaml
import pretty_errors
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# setup logs
dirpath = os.path.join(os.path.dirname(__file__), 'logs')
if not os.path.isdir(dirpath):
    os.mkdir(dirpath)

logs = ['info.log', 'error.log']
for log in logs:
    filepath = os.path.join(dirpath, log)
    if not os.path.isfile(filepath):
        with open(filepath, 'w') as f:
            pass

# init logger
with open('logging.yaml', 'r') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)
    logging.config.dictConfig(config)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# init driver
driverpath = os.path.join(os.path.dirname(__file__), 'chromedriver')
options = Options()
options.add_experimental_option('detach', True)
options.add_argument('--ignore-ssl-errors=yes')
options.add_argument('--ignore-certificate-errors')
driver = webdriver.Chrome(executable_path=driverpath, options=options)


def login():
    try:
        driver.get('')
        driver.find_element(By.NAME, 'id_petugas').send_keys('')
        driver.find_element(By.NAME, 'password').send_keys('')
    except (NoSuchElementException) as e:
        logger.exception(e)
        driver.quit()


def search(nik, contents, i):
    try:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.NAME, 'NIK')))
        driver.find_element(By.NAME, 'NIK').send_keys(nik)
        driver.find_element(By.NAME, 'cari').click()

        data = get_data(i)
        contents.append(data)
        time.sleep(1)
        driver.find_element(By.LINK_TEXT, 'Cari Lagi').click()
    except(TimeoutException):
        print('search() timeout')
        logger.info('search() timeout')
        driver.quit()
    except(NoSuchElementException) as e:
        logger.exception(e)
        driver.quit()


def get_data(i):
    try:
        table_container = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.TAG_NAME, 'table')))
        nik = table_container.find_element(By.XPATH, '//tbody/tr[1]/td').text
        no_kk = table_container.find_element(By.XPATH, '//tbody/tr[2]/td').text
        nama = table_container.find_element(By.XPATH, '//tbody/tr[3]/td').text
        ttl = table_container.find_element(By.XPATH, '//tbody/tr[4]/td').text
        jenis_kelamin = table_container.find_element(
            By.XPATH, '//tbody/tr[5]/td').text
        jenis_kelamin = jenis_kelamin.upper()
        alamat = table_container.find_element(
            By.XPATH, '//tbody/tr[6]/td').text
        alamat = alamat.replace(',', '.') if alamat != '' else '-'
        rt = table_container.find_element(By.XPATH, '//tbody/tr[7]/td').text
        rt = f'RT {rt}' if rt != '' else ''
        rw = table_container.find_element(By.XPATH, '//tbody/tr[8]/td').text
        rw = f'RW {rw}' if rw != '' else ''
        desa = table_container.find_element(By.XPATH, '//tbody/tr[9]/td').text
        kecamatan = table_container.find_element(
            By.XPATH, '//tbody/tr[10]/td').text
        kota = table_container.find_element(By.XPATH, '//tbody/tr[11]/td').text
        provinsi = table_container.find_element(
            By.XPATH, '//tbody/tr[12]/td').text
        pekerjaan = table_container.find_element(
            By.XPATH, '//tbody/tr[13]/td').text
        nama_ibu = table_container.find_element(
            By.XPATH, '//tbody/tr[14]/td').text

        data = [nik, no_kk, nama, ttl, jenis_kelamin, alamat,
                desa, kecamatan, kota, provinsi, pekerjaan, nama_ibu]
        data = '|'.join(data)
        logger.info(f'{i}. {data}')
        return data
    except(TimeoutException):
        logger.info('get_element() timeout')
        driver.quit()
    except(NoSuchElementException) as e:
        logger.exception(e)
        driver.quit()


def read_source():
    filepath = os.path.join(os.path.dirname(__file__), 'source.txt')
    if not os.path.isfile(filepath):
        logger.info('\"source.txt\" is not found')
        driver.quit()
    else:
        with open(filepath, 'r') as f:
            i = 1
            lines = f.readlines()
            max_line = len(lines)
            contents = []

            for line in lines:
                search(line.rstrip(), contents, i)
                if i == max_line:
                    write_result(contents)
                i += 1


def write_result(contents):
    dirpath = os.path.join(os.path.dirname(__file__), 'dist')
    if not os.path.isdir(dirpath):
        os.mkdir(dirpath)

    uid = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'result_{uid}.txt'
    filepath = os.path.join(dirpath, filename)
    with open(filepath, 'w') as f:
        content = '\n'.join(contents)
        f.write(content)
        logger.info(
            f'Successfully to get {len(contents)} data and saved to {filename}')
        driver.quit()


if __name__ == '__main__':
    login()
    time.sleep(10)
    read_source()
