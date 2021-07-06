from selenium import webdriver
import pandas as pd
from datetime import datetime, timedelta
import bs4 as bs
import lxml
import requests

class WebRatesScraper:
    def __init__(self):
        driver = webdriver.Chrome()
        driver.get('http://www.cmegroup.com/ftp/pub/settle/stlint')

        self.cme_text = driver.page_source
        driver.quit()

    def getIMMDate(self, IMMcode, month):
        '''Takes 5 character IMM code (e.g. SEP23) and returns effective date as datetime object'''
        if month == 1:
            offset = 31
        else:
            offset = 93

        from datetime import datetime, timedelta
        month_dict = {
            'JAN': 1,
            'FEB': 2,
            'MAR': 3,
            'APR': 4,
            'MAY': 5,
            'JUN': 6,
            'JLY': 7,
            'AUG': 8,
            'SEP': 9,
            'OCT': 10,
            'NOV': 11,
            'DEC': 12,

        }

        month = month_dict[IMMcode[0:3]]

        year_prefix = str(datetime.now().year)[:2]

        year = int(year_prefix + IMMcode[3:])

        the_date = datetime(year, month, 1)
        end_date = the_date + timedelta(days=offset)
        temp = the_date.replace(day=1)
        temp_end = end_date.replace(day=1)
        nth_week = 3
        week_day = 2
        adj = (week_day - temp.weekday()) % 7
        adj_end = (week_day - temp_end.weekday()) % 7
        temp += timedelta(days=adj)
        temp += timedelta(weeks=nth_week - 1)
        temp_end += timedelta(days=adj_end)
        temp_end += timedelta(weeks=nth_week - 1)

        return datetime.strftime(temp, "%m/%d/%Y"), datetime.strftime(temp_end, "%m/%d/%Y")

    def get_effr(self):
        url = "https://markets.newyorkfed.org/read?productCode=50&eventCodes=500&limit=25&startPosition=0&sort=postDt:-1&format=xml"

        url_link = requests.get(url)
        file = bs.BeautifulSoup(url_link.text, "lxml")
        find_table = file.find("percentrate")

        return find_table.text

    def get_obfr(self):
        url = "https://markets.newyorkfed.org/read?productCode=50&eventCodes=505&limit=25&startPosition=0&sort=postDt:-1&format=xml"

        url_link = requests.get(url)
        file = bs.BeautifulSoup(url_link.text, "lxml")
        find_table = file.find("percentrate")

        return find_table.text

    def get_eurodollar_strip(self):


        start = self.cme_text.find("ED CME EURODOLLAR FUTURES") + len("ED CME EURODOLLAR FUTURES") + 1
        end = self.cme_text.find("EM 1-MONTH EURODOLLAR FUTURE")

        edf = self.cme_text[start:end]
        end = edf.find("TOTAL")
        edf = edf[:end]
        data = edf.splitlines()

        df = pd.DataFrame([x[:56].split() for x in data])
        df.columns = ['Expiry', 'Open', 'High', 'Low', 'Last', 'Sett']
        df.set_index('Expiry', inplace=True)
        df = df.head(28)


        df = df.apply(pd.to_numeric, errors='ignore')
        expiry = df.index.tolist()

        start = []
        end = []
        for d in expiry:
            s, e = self.getIMMDate(d, 3)
            start.append(s)
            end.append(e)

        df2 = pd.DataFrame(list(zip(expiry, start, end)), columns=['Expiry', 'Start', 'End'])

        df = df.merge(df2, left_on='Expiry', right_on='Expiry')
        return df

    def get_30_day_fed_funds_strip(self):
        start = self.cme_text.find("FF 30 DAY FED FUNDS FUTURES") + len("FF 30 DAY FED FUNDS FUTURES") + 1
        end = self.cme_text.find("FV 5 YEAR US TREASURY NOTE FUTURES")

        edf = self.cme_text[start:end]
        end = edf.find("TOTAL")
        edf = edf[:end]
        data = edf.splitlines()


        df = pd.DataFrame([x[:56].split() for x in data])
        df.columns = ['Expiry', 'Open', 'High', 'Low', 'Last', 'Sett']
        df.set_index('Expiry', inplace=True)
        df = df.head(21)


        df = df.apply(pd.to_numeric, errors='ignore')
        expiry = df.index.tolist()

        start = []
        end = []
        for d in expiry:
            s, e = self.getIMMDate(d, 1)
            start.append(s)
            end.append(e)

        df2 = pd.DataFrame(list(zip(expiry, start, end)), columns=['Expiry', 'Start', 'End'])

        df = df.merge(df2, left_on='Expiry', right_on='Expiry')

        return df

    def get_mpc_sonia_strip(self):
        start = self.cme_text.find("MPC MPC SONIA Futures") + len("MPC MPC SONIA Futures") + 1
        end = self.cme_text.find("N1S 10-Year MAC SOFR Swap Futures")

        edf = self.cme_text[start:end]
        end = edf.find("TOTAL")
        edf = edf[:end]
        data = edf.splitlines()
        df = pd.DataFrame([x[:56].split() for x in data])
        df.columns = ['Expiry', 'Open', 'High', 'Low', 'Last', 'Sett']
        df.set_index('Expiry', inplace=True)
        df = df.head(5)


        df = df.apply(pd.to_numeric, errors='ignore')
        expiry = df.index.tolist()

        start = []
        end = []
        for d in expiry:
            s, e = self.getIMMDate(d, 1)
            start.append(s)
            end.append(e)

        df2 = pd.DataFrame(list(zip(expiry, start, end)), columns=['Expiry', 'Start', 'End'])

        df = df.merge(df2, left_on='Expiry', right_on='Expiry')

        return df

    def get_3M_sonia_strip(self):
        start = self.cme_text.find("SON Three-Month SONIA Futures") + len("SON Three-Month SONIA Futures") + 1
        end = self.cme_text.find("SPX SYNTH ON ED CAL SPRD")

        edf = self.cme_text[start:end]
        end = edf.find("TOTAL")
        edf = edf[:end]
        data = edf.splitlines()


        df = pd.DataFrame([x[:56].split() for x in data])
        df.columns = ['Expiry', 'Open', 'High', 'Low', 'Last', 'Sett']
        df.set_index('Expiry', inplace=True)
        df = df.head(20)


        df = df.apply(pd.to_numeric, errors='ignore')
        expiry = df.index.tolist()

        start = []
        end = []
        for d in expiry:
            s, e = self.getIMMDate(d, 3)
            start.append(s)
            end.append(e)

        df2 = pd.DataFrame(list(zip(expiry, start, end)), columns=['Expiry', 'Start', 'End'])

        df = df.merge(df2, left_on='Expiry', right_on='Expiry')

        return df

    def get_1M_sofr_strip(self):
        start = self.cme_text.find("SR1 1-MONTH SOFR FUTURE") + len("SR1 1-MONTH SOFR FUTURE") + 1
        end = self.cme_text.find("SR3 3-MONTH SOFR FUTURE")

        edf = self.cme_text[start:end]
        end = edf.find("TOTAL")
        edf = edf[:end]
        data = edf.splitlines()


        df = pd.DataFrame([x[:56].split() for x in data])
        df.columns = ['Expiry', 'Open', 'High', 'Low', 'Last', 'Sett']
        df.set_index('Expiry', inplace=True)
        df = df.head(11)


        df = df.apply(pd.to_numeric, errors='ignore')
        expiry = df.index.tolist()

        start = []
        end = []
        for d in expiry:
            s, e = self.getIMMDate(d, 1)
            start.append(s)
            end.append(e)

        df2 = pd.DataFrame(list(zip(expiry, start, end)), columns=['Expiry', 'Start', 'End'])

        df = df.merge(df2, left_on='Expiry', right_on='Expiry')

        return df

    def get_3M_sofr_strip(self):
        start = self.cme_text.find("SR3 3-MONTH SOFR FUTURE") + len("SR3 3-MONTH SOFR FUTURE") + 1
        end = self.cme_text.find("T1S 2-Year MAC SOFR Swap Futures")

        edf = self.cme_text[start:end]
        end = edf.find("TOTAL")
        edf = edf[:end]
        data = edf.splitlines()


        df = pd.DataFrame([x[:56].split() for x in data])
        df.columns = ['Expiry', 'Open', 'High', 'Low', 'Last', 'Sett']
        df.set_index('Expiry', inplace=True)
        df = df.head(15)


        df = df.apply(pd.to_numeric, errors='ignore')
        expiry = df.index.tolist()

        start = []
        end = []
        for d in expiry:
            s, e = self.getIMMDate(d, 3)
            start.append(s)
            end.append(e)

        df2 = pd.DataFrame(list(zip(expiry, start, end)), columns=['Expiry', 'Start', 'End'])

        df = df.merge(df2, left_on='Expiry', right_on='Expiry')

        return df

cme = WebRatesScraper()
res = cme.get_effr()
print(res)
res = cme.get_obfr()
print(res)