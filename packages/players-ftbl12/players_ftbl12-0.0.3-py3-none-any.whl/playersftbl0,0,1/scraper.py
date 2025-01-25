import requests
from bs4 import BeautifulSoup

def scrape_team(url):
    """
    Bu fonksiyon, verilen URL'deki takım bilgilerini çekip döndürür.

    Args:
    - url (str): Transfermarkt üzerindeki takım sayfasının URL'si

    Returns:
    - dict: Başlıklar ve verilerle birlikte takım bilgisi
    - str: Hata mesajı
    """
    try:
        # Sayfaya istek gönder
        response = requests.get(url)
        
        # Başarılı cevap alındığında işleme başla
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # İlgili tabloyu bul
            table_div = soup.find('div', {'id': 'yw1'})

            if table_div:
                rows = table_div.find_all('tr')

                # Başlıkları al
                headers = rows[0].find_all('th')
                headers_text = [header.get_text(strip=True) for header in headers]

                # Veri satırlarını al
                data = []
                for row in rows[1:]:
                    cols = row.find_all('td')
                    cols_text = [col.get_text(strip=True) for col in cols]
                    data.append(cols_text)

                return {"headers": headers_text, "data": data}
            else:
                return "Tablo bulunamadı!"
        else:
            return f"Sayfaya erişim başarısız: {response.status_code}"
    except Exception as e:
        # Hata durumunda genel mesaj
        return f"Bir hata oluştu: {str(e)}"

# Test URL
# print(scrape_team("https://www.transfermarkt.com.tr/besiktas-istanbul/startseite/verein/114"))
