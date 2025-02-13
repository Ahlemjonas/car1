import os

from django.conf import settings
from django.core.files import File
from django.db import IntegrityError

# Assuming your project settings module is located at 'core.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()
from home.models import Car, Photo



def add_photos_to_car(car_folder_path, car):
    photos_folder_path = os.path.join(car_folder_path, 'photos')
    if os.path.exists(photos_folder_path):
        photo_files = [f for f in os.listdir(photos_folder_path) if f.endswith(('.jpg', '.jpeg', '.png'))]
        for order, photo_file in enumerate(photo_files):
            photo_path = os.path.join(photos_folder_path, photo_file)
            with open(photo_path, 'rb') as f:
                photo = Photo(car=car, order=order)
                photo.image.save(photo_file, File(f))
                print(f"Added photo: {photo_file} to car: {car.mark} {car.model}")


def main(base_dir):
    print(f"Processing directory: {base_dir}")
    for car_folder in os.listdir(base_dir):
        car_folder_path = os.path.join(base_dir, car_folder)
        if os.path.isdir(car_folder_path):
            car_info_file = [f for f in os.listdir(car_folder_path) if f.endswith('.txt')]
            if car_info_file:
                car_info_file_path = os.path.join(car_folder_path, car_info_file[0])
                car_info = parse_car_info(car_info_file_path)

                name, year = extract_name_and_year(car_folder)
                try:
                    car = Car.objects.get(vin=car_info.get('vin', 'Unknown'))
                    add_photos_to_car(car_folder_path, car)
                except Car.DoesNotExist:
                    print(f"No car found with VIN {car_info.get('vin', 'Unknown')}")


def parse_car_info(file_path):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()

        car_info = {}

        if len(lines) > 1:
            car_info['price'] = lines[1].split(': ')[1].strip() if ': ' in lines[1] else '0.00'

        description_index = None
        for i, line in enumerate(lines):
            if line.strip().lower() == 'description':
                description_index = i
                break

        if description_index is not None:
            car_info['description'] = ' '.join([line.strip() for line in lines[description_index + 1:]])

        for line in lines[3:description_index if description_index else len(lines)]:
            if ':' in line:
                key, value = line.split(':', 1)
                car_info[key.strip().lower()] = value.strip()

        return car_info
    except Exception as e:
        print(f"Error parsing file {file_path}: {e}")
        return {}


def extract_name_and_year(folder_name):
    parts = folder_name.split()
    year = parts[1]
    name = ' '.join(parts[2:])
    return name, year


if __name__ == "__main__":
    base_directory = 'C:/Users/Acer/Desktop/tema'
    print("Starting process...")
    main(base_directory)
    print("Process completed.")
