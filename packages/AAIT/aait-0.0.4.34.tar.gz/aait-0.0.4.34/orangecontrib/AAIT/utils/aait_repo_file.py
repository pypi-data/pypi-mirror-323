import json
import os
import subprocess
import zipfile
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from ..utils import MetManagement


def generate_listing_json(directory_to_list):
    """
    generate a file file_info.json  with size of file in directory
    for low level devellopper only
    -> use create_index_file
    """
    output_json_file = directory_to_list+'/files_info.json'
    if os.path.isfile(output_json_file):
        os.remove(output_json_file)

    def list_files_recursive(directory):
        files_info = {}

        for root, dirs, files in os.walk(directory):
            for file in files:

                file_path = os.path.join(root, file).replace("\\","/")
                file_size = os.path.getsize(file_path)
                file_path=file_path[len(directory)+1:]
                files_info[file_path]=file_size

        return files_info

    def save_to_json(data, output_file):
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    files_info = list_files_recursive(directory_to_list)
    save_to_json(files_info, output_json_file)
    return files_info

def add_file_to_zip_file(folder,file_in,zip_file):
    """
    folder : a point to start relative path
    file in : a file to add to zip file
    zip file : destination zip file
    for exemple I want to add C:/dir1/dir2/dir3/qwerty.txt to
    C:/dir1//dir2/example.zip and index dir3/qwerty.txt
    folder = C:/dir1/
    file_in=C:/dir1/dir2/dir3/qwerty.txt
    zip_file  C:/dir2/example.zip
    """
    path_in=folder+file_in
    with open(path_in, 'rb') as f:
        contenu = f.read()
    with zipfile.ZipFile(zip_file, 'a', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(file_in, contenu)

def create_index_file(in_repo_file,out_repo_file):
    """
    delete files_info.json and regenerate it
    with file contain a dictionnary filename:filesize
    out_repo_file is not used
    """
    if not os.path.isfile(in_repo_file):
        raise Exception("The specified path is not a file "+in_repo_file)
    if 0!=MetManagement.get_size(in_repo_file):
        raise Exception("The file " + in_repo_file+ " need to be empty to use this functions")
    print(MetManagement.get_size(in_repo_file))
    folder_to_process=os.path.dirname(in_repo_file).replace("\\","/")
    file_info=generate_listing_json(folder_to_process)
    return

def decode(repo_file,file_to_read):
    """
    /!\ be carrefull with big file (ram saturation)
    return containt of a zipped file
    """
    if os.path.isfile(repo_file)==False:
        return None
    file_to_read=os.path.splitext(os.path.basename(repo_file))[0]+"/"+file_to_read
    with zipfile.ZipFile(repo_file, 'r') as zip_ref:
        with zip_ref.open(file_to_read) as file:
            content = file.read()
            return content.decode('utf-8')
    return None
def decode_to_file(zip_path, target_path, output_path):
    """
    extract a file from a zip file and write it on hdd
    example : I want to extract dir1/qwerty.txt from C:/dir1/dir2/zipfile.zip to C:/dir_a/dir_b/dir1/qwerty.txt
    zip_path=C:/dir1/dir2/zipfile.zip
    target_path=dir1/qwerty.txt
    output_path=C:/dir_a/dir_b/
    """
    chunk_size = 1024 * 1024 * 100 # 100 Mo
    target_path=os.path.splitext(os.path.basename(zip_path))[0]+"/"+target_path
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        target_path = target_path.rstrip('/')
        files_to_extract = [f for f in zip_ref.namelist() if f.startswith(target_path)]

        if len(files_to_extract) == 0:
            raise FileNotFoundError(f"{target_path} not found in the archive.")

        if len(files_to_extract) == 1 and not files_to_extract[0].endswith('/'):
            # Cible est un fichier unique
            output_file_path = output_path
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
            with zip_ref.open(files_to_extract[0]) as source, open(output_file_path, 'wb') as target:
                #target.write(source.read())
                while True:
                    # read and write a chunk to avoid ram limitation
                    chunk = source.read(chunk_size)
                    if not chunk:
                        break
                    target.write(chunk)
        else:
            # Cible est un dossier ou plusieurs fichiers
            for file in files_to_extract:
                relative_path = os.path.relpath(file, start=target_path)
                destination_path = os.path.join(output_path, relative_path)

                if file.endswith('/'):
                    os.makedirs(destination_path, exist_ok=True)
                else:
                    os.makedirs(os.path.dirname(destination_path), exist_ok=True)
                    with zip_ref.open(file) as source, open(destination_path, 'wb') as target:
                        #target.write(source.read())
                        while True:
                            # read and write a chunk to avoid ram limitation
                            chunk = source.read(chunk_size)
                            if not chunk:
                                break
                            target.write(chunk)


def download_from_folder_server(base_url, local_dir=".", target_subfolder="", visited=None):
    """
    Recursively downloads all files and subdirectories from the specified
    `target_subfolder` on a Freebox server (or similar) at `base_url`,
    recreating the folder structure under the given `local_dir`.

    Parameters
    ----------
    base_url : str
        The base URL of the shared folder.
        Example: "http://88.172.137.71:40386/share/ma0UJQ8-jqb9uqiM/"
    local_dir : str
        The local directory where everything (files/subfolders) will be stored.
        Defaults to the current directory.
    target_subfolder : str
        A subdirectory (or file) relative to `base_url`.
        Examples:
            - "test" for a subfolder named 'test'
            - "my_file.txt" for a specific file
            - "" (empty) for the root folder
    visited : set
        A set of URLs already visited (used internally to avoid loops).
    """

    # Ensure we have a set to keep track of visited URLs
    if visited is None:
        visited = set()

    # Build the full URL by combining base_url + target_subfolder
    # e.g. base_url="http://server.com/share/", target_subfolder="test"
    #      => full_url="http://server.com/share/test"
    full_url = base_url.rstrip('/') + '/' + target_subfolder.strip('/')

    # If we've already processed this URL, skip it (avoid cycles)
    if full_url in visited:
        return
    visited.add(full_url)

    # Ensure local_dir exists. If `target_subfolder` is provided,
    # create a subfolder in local_dir (mimicking the same name).
    # For the *first* call, we combine local_dir + target_subfolder
    # so that the target subfolder is placed inside local_dir.
    # However, if target_subfolder is empty, we use local_dir directly.

    # local_target_dir => the local directory corresponding exactly to `target_subfolder`
    local_target_dir = os.path.join(local_dir, target_subfolder.strip('/')) if target_subfolder else local_dir
    os.makedirs(local_target_dir, exist_ok=True)

    print(f"> Attempting to access: {full_url}")
    try:
        response = requests.get(full_url)
        response.raise_for_status()
    except Exception as e:
        print(f"Unable to retrieve {full_url}: {e}")
        return

    # Parse the HTML to check if it's a listing or a single file
    soup = BeautifulSoup(response.text, 'html.parser')

    # Freebox listing typically has <h1> containing "Contenu de", plus a <table> of files
    h1 = soup.find('h1')
    has_contenu_de = (h1 and "Contenu de" in h1.get_text())
    table = soup.find('table')

    if has_contenu_de and table:
        # ===========================================
        # CASE 1: It's a directory listing (Freebox)
        # ===========================================
        print(f"Directory listing detected for: {full_url}")

        rows = table.find_all('tr')
        for row in rows:
            # Each row might have a link <a href="...">
            links = row.find_all('a', href=True)
            if not links:
                continue

            link = links[0]
            href = link['href']

            # Skip links like "../"
            if href.startswith('../'):
                continue

            # The name of the child (folder or file) from the HREF
            child_name = href.strip('/')
            # Build the child's full URL
            child_url = urljoin(full_url + '/', href)

            # If the link ends with '/', treat it as a subdirectory
            if href.endswith('/'):
                # We want to download everything inside that subdir
                # We'll call the same function, passing the *same* base_url,
                # but with an updated target_subfolder that includes the subfolder.
                new_target_subfolder = os.path.join(target_subfolder.strip('/'), child_name)
                # On Windows, os.path.join might create backslashes;
                # let's normalize them to forward slashes for the URL parts:
                new_target_subfolder = new_target_subfolder.replace('\\', '/')

                download_from_folder_server(
                    base_url=base_url,
                    local_dir=local_dir,
                    target_subfolder=new_target_subfolder,
                    visited=visited
                )
            else:
                # It's a file => download
                local_filename = os.path.join(local_target_dir, child_name)
                print(f"Downloading file: {child_url} => {local_filename}")

                process = subprocess.run(
                    ["curl", "-s", "-L", "-o", local_filename, child_url],
                    capture_output=True
                )
                if process.returncode != 0:
                    err_msg = process.stderr.decode('utf-8', errors='replace')
                    print(f"Download failed for {child_url}: {err_msg}")
                else:
                    print(f"File downloaded: {local_filename}")

    else:
        # =========================================
        # CASE 2: Probably a single file
        # =========================================
        filename = os.path.basename(target_subfolder.strip('/'))
        if not filename:
            print(f"Unable to deduce a file name from {full_url}")
            return

        local_filename = os.path.join(local_target_dir, filename)
        print(f"Downloading a single file: {full_url} => {local_filename}")

        process = subprocess.run(
            ["curl", "-s", "-L", "-o", local_filename, full_url],
            capture_output=True
        )
        if process.returncode != 0:
            err_msg = process.stderr.decode('utf-8', errors='replace')
            print(f"Download failed for {full_url}: {err_msg}")
        else:
            print(f"File downloaded: {local_filename}")


if __name__ == "__main__":
    download_from_folder_server("http://88.172.137.71:40386/share/ma0UJQ8-jqb9uqiM/",r"C:\Users\timot\Desktop\Nouveau dossier (2)","AAIT_v240916")
    in_repo_file="C:/Users/jean-/Desktop/AAIT_v240916/repository.aait"
    out_repo_file="C:/Users/jean-/Desktop/AAIT_v240916/AAIT_v240828.aait"
    create_index_file(in_repo_file, out_repo_file)

