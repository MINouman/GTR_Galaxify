import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "postgresql://admin:Aikittam1@localhost/samsung_phones"

Base = declarative_base()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

class PhoneSpecs(Base):
    __tablename__ = 'phone_specs'
    id = Column(Integer, primary_key=True)
    model_name = Column(String(100))
    release_date = Column(String(50))
    price_at_launch = Column(String(50))
    network_technology = Column(String(100))
    sim_specs = Column(String(50))
    wifi = Column(String(50))
    bluetooth = Column(String(50))
    gps = Column(String(50))
    nfc = Column(Boolean)
    usb = Column(String(50))
    dimensions = Column(String(50))
    weight = Column(String(50))
    build_materials = Column(String(100))
    colors = Column(String(100))
    display_type = Column(String(50))
    display_size = Column(String(50))
    resolution = Column(String(50))
    protection = Column(String(50))
    refresh_rate = Column(String(50))
    os = Column(String(50))
    chipset = Column(String(50))
    cpu = Column(String(100))
    gpu = Column(String(50))
    ram = Column(String(50))
    internal_storage = Column(String(50))
    expandable_storage = Column(String(50))
    rear_camera = Column(Text)
    front_camera = Column(Text)
    sound_specs = Column(String(100))
    battery_capacity = Column(String(50))
    battery_type = Column(String(50))
    charging_speed = Column(String(50))
    wireless_charging = Column(Boolean)
    sensors = Column(Text)
    additional_features = Column(Text)

Base.metadata.create_all(engine)

target_models = [
    "Galaxy A55", "Galaxy S24 Ultra", "Galaxy S24", "Galaxy S22 Ultra 5G",
    "Galaxy S24 FE", "Galaxy S23 Ultra", "Galaxy S21 Ultra 5G", "Galaxy S23",
    "Galaxy S22 5G", "Galaxy S21 5G", "Galaxy S21 FE", "Galaxy A54",
    "Galaxy S10", "Galaxy S24+", "Galaxy S23 FE", "Galaxy A12",
    "Galaxy Note20 Ultra 5G", "Galaxy S10+", "Galaxy A13", "Galaxy A53 5G",
    "Galaxy A32", "Galaxy A51", "Galaxy A14", "Galaxy M35",
    "Galaxy S20", "Galaxy S20 FE 5G", "Galaxy S20 Ultra 5G", "Galaxy Note10+",
    "Galaxy Tab A9", "Galaxy S9"
]

def scrape_gsmarena():
    base_url = "https://www.gsmarena.com/samsung-phones-f-9-0-r1-p1.php"
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    phone_links = soup.select('div.makers ul li a')

    for phone in phone_links:
        model_name_tag = phone.find('span')
        if model_name_tag:
            model_name = model_name_tag.text.strip()
        else:
            print("Model name not found, skipping...")
            continue

        if model_name not in target_models:
            print(f"Skipping: {model_name}")
            continue

        print(f"Processing: {model_name}")

        phone_url = f"https://www.gsmarena.com/{phone['href']}"
        phone_response = requests.get(phone_url)
        phone_soup = BeautifulSoup(phone_response.text, 'html.parser')

        release_date = price_at_launch = network_technology = sim_specs = ''
        wifi = bluetooth = gps = nfc = usb = ''
        dimensions = weight = build_materials = colors = ''
        display_type = display_size = resolution = protection = refresh_rate = ''
        os = chipset = cpu = gpu = ram = internal_storage = expandable_storage = ''
        rear_camera = front_camera = sound_specs = ''
        battery_capacity = battery_type = charging_speed = ''
        wireless_charging = sensors = additional_features = ''

        specs_table = phone_soup.find_all('table', class_='specs-table')

        for table in specs_table:
            rows = table.find_all('tr')
            for row in rows:
                th = row.find('th').text.strip() if row.find('th') else ''
                td = row.find('td').text.strip() if row.find('td') else ''

                if 'Launch' in th:
                    release_date = td
                elif 'Price' in th:
                    price_at_launch = td
                elif 'Technology' in th:
                    network_technology = td
                elif 'SIM' in th:
                    sim_specs = td
                elif 'WLAN' in th:
                    wifi = td
                elif 'Bluetooth' in th:
                    bluetooth = td
                elif 'GPS' in th:
                    gps = td
                elif 'NFC' in th:
                    nfc = 'Yes' in td
                elif 'USB' in th:
                    usb = td
                elif 'Dimensions' in th:
                    dimensions = td
                elif 'Weight' in th:
                    weight = td
                elif 'Build' in th:
                    build_materials = td
                elif 'Colors' in th:
                    colors = td
                elif 'Type' in th:
                    display_type = td
                elif 'Size' in th:
                    display_size = td
                elif 'Resolution' in th:
                    resolution = td
                elif 'Protection' in th:
                    protection = td
                elif 'OS' in th:
                    os = td
                elif 'Chipset' in th:
                    chipset = td
                elif 'CPU' in th:
                    cpu = td
                elif 'GPU' in th:
                    gpu = td
                elif 'Internal' in th:
                    internal_storage = td
                elif 'Main Camera' in th:
                    rear_camera = td
                elif 'Selfie camera' in th:
                    front_camera = td
                elif 'Battery' in th:
                    battery_capacity = td

        phone_data = PhoneSpecs(
            model_name=model_name,
            release_date=release_date,
            price_at_launch=price_at_launch,
            network_technology=network_technology,
            sim_specs=sim_specs,
            wifi=wifi,
            bluetooth=bluetooth,
            gps=gps,
            nfc=nfc,
            usb=usb,
            dimensions=dimensions,
            weight=weight,
            build_materials=build_materials,
            colors=colors,
            display_type=display_type,
            display_size=display_size,
            resolution=resolution,
            protection=protection,
            os=os,
            chipset=chipset,
            cpu=cpu,
            gpu=gpu,
            ram=ram,
            internal_storage=internal_storage,
            expandable_storage=expandable_storage,
            rear_camera=rear_camera,
            front_camera=front_camera,
            sound_specs=sound_specs,
            battery_capacity=battery_capacity
        )
        session.add(phone_data)

    session.commit()
    print("Data scraping and storage completed for target models!")

if __name__ == "__main__":
    scrape_gsmarena()
