import requests
import importlib
from bs4 import BeautifulSoup
import os
import zipfile
import shutil

base_url = "https://www.ubisoft.com/en-gb/game/rainbow-six/siege/game-info/maps"
global map_url
global download_url

def check_and_install_module(module_name):
    try:
        importlib.import_module(module_name)
    except ImportError:
        print(f"{module_name} The module is not installed, install the module...")
        import subprocess
        subprocess.run(["pip", "install", module_name])

def get_map_names():
    try:
        response = requests.get(base_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        map_cards = soup.find_all('a', {'class': 'maplist__card'})

        map_names = []
        for card in map_cards:
            map_name = card.find('span').text.strip()
            map_names.append(map_name)

        return map_names
    except Exception as e:
        print(f"Debug: Error in get_map_names - {e}")
        return None


def get_map_blueprint_url(map_name):
    global download_url
    
    try:
        map_name_url = map_name.lower().replace(' ', '-')
        map_url = f"{base_url}/{map_name_url}"
        
        response = requests.get(map_url)
        try:
            response.raise_for_status()
        except requests.HTTPError as err:
            print(f"An HTTP error occurred: {err}")

        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the download button
        download_button = soup.find('a', class_='map-details__gallery__button')

        # Extract the download URL
        if download_button:
            download_url = download_button.get('href')
            return download_url
        else:
            print(f"Error: Download link not found on the {map_name} page.")
        
    except Exception as e:
        print(f"Debug: Error in get_map_blueprint_url - {e}")

    return None


def download_blueprint(zip_url, map_name):
    global download_url
    
    response = requests.get(zip_url)

    if response.status_code == 200:
        save_path = f"./maps/{map_name}_blueprint.zip"
        
        # Ensure the 'maps' directory exists
        os.makedirs('maps', exist_ok=True)
        
        # Save map
        if not os.path.exists(save_path):
            with open(save_path, 'wb') as file:
                file.write(response.content)
            print(f"Done, {map_name}")
            
        # Failed save map cause exist
        else:
            print(f"Error: Unable to download blueprint. File already exists: {save_path}")
            print(f"Failed to download a file at the following Url: {download_url}\n") 
            
    # URL is incorrect
    else:
        print(f"Error: Unable to download {map_name} blueprint. Status code: {response.status_code}")
        
    # URL is empty
    if not zip_url:
            print("Error: Invalid download URL. Download URL is None or empty.")
            return


# Extract and delete files
def extract_and_delete_files(map_names):
    for map_name in map_names:
        zip_path = f"./maps/{map_name}_blueprint.zip"
        extract_folder = f"./maps/{map_name}_blueprint"

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_folder)

        os.remove(zip_path)
        print(f"Extracted and deleted the original file at: {extract_folder}")
        
        # Check for __MACOSX folder and prompt user for deletion
        
        
        # Delete __MACOSX folders
        macosx_folder = os.path.join(extract_folder, "__MACOSX")
        if os.path.exists(macosx_folder):
            shutil.rmtree(macosx_folder)
            print(f"Deleted __MACOSX folder in {extract_folder}")


required_modules = ["requests", "bs4"]
for module in required_modules:
    check_and_install_module(module)

# Get map names
map_names = get_map_names()
if map_names:
    print("Map Names:")
    for map_name in map_names:
        print(map_name)
    print(f"Total number of maps: {len(map_names)}")

    # Download blueprints for each map
    for map_name in map_names:
        download_url = get_map_blueprint_url(map_name)
        download_blueprint(download_url, map_name)
    
    # Ask if user wants to extract and delete the original files
    extract_and_delete = input("Do you want to extract and delete the original files? (y/n): ").lower()

    if extract_and_delete == 'y':
        extract_and_delete_files(map_names)

else:
    print("Error: Unable to get map names.")
