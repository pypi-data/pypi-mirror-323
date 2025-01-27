import subprocess
import shutil
import os
from exiftool import ExifToolHelper
import re
import time


def is_exiftool_installed():
    try:
        result = subprocess.run(
            ["exiftool", "-ver"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return result.returncode == 0
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def is_homebrew_installed():
    try:
        result = subprocess.run(
            ["brew", "-v"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return result.returncode == 0
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def install_exiftool():
    # Install exiftool via homebrew if given permission
    if not is_exiftool_installed():
        exiftool = (
            input(
                "Exiftool (https://exiftool.org) is not installed. It is needed to read the metadata of your images for sorting. Would you like to install it with Homebrew (https://brew.sh)? (y/n) "
            )
            .lower()
            .strip(" ")
        )
        if exiftool == "y" and not is_homebrew_installed():
            homebrew = (
                input(
                    "Homebrew is not installed. Would you like to install it and proceed with the installation of Exiftool? (y/n) "
                )
                .lower()
                .strip(" ")
            )
            if homebrew == "y":
                subprocess.run(
                    [
                        "/bin/bash",
                        "-c",
                        "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)",
                    ]
                )
                subprocess.run(["brew", "install", "exiftool"])
            else:
                print(
                    "Exiftool is needed to sort images. Please install it manually from https://exiftool.org and try again."
                )
        elif exiftool == "y" and is_homebrew_installed():
            subprocess.run(["brew", "install", "exiftool"])
        else:
            print(
                "Exiftool is needed to sort images. Please install it manually from https://exiftool.org and try again."
            )


def locations():
    print("Hello! I am sorting pictures for you. Let's get started.")
    while True:
        before_sorting = (
            input("Where are the pictures located? ").strip(" ").strip('"').strip("'")
        )
        if os.path.exists(before_sorting) and os.path.isdir(before_sorting):
            break
        else:
            before_help = (
                input(
                    "This folder does not exist. You need to enter the exact path. Do you need help? (y/n) "
                )
                .lower()
                .strip(" ")
            )
            if before_help == "y":
                print(
                    f"Just drag the folder into the terminal or copy the path in Finder/Explorer and paste it here."
                )
            if before_help == "n":
                continue

    while True:
        after_sorting = (
            input("Where should the pictures be moved and sorted? ")
            .strip(" ")
            .strip('"')
            .strip("'")
        )

        if os.path.exists(after_sorting) and os.path.isdir(after_sorting):

            if os.listdir(after_sorting) != []:
                not_empty = (
                    input(
                        "This folder is not empty. Are you sure you want to proceed? (y/n) "
                    )
                    .lower()
                    .strip(" ")
                )
                if not_empty == "y":
                    break
                if not_empty in ("n", ""):
                    continue
            elif before_sorting == after_sorting:
                print(
                    "This is the original folder. Please choose a different folder to sort the pictures into."
                )
                continue
            else:
                break
        else:
            print("This folder does not exist. You need to enter the exact path.")

    return before_sorting, after_sorting


def folder_structure():
    while True:
        try:
            detail: str = input(
                "Do you want to sort into subfolders for \n1. Year, \n2. Year and Month or \n3. Year, Month and Day? \n4. No, I don't \nPictures that fall into the same category will be numbered consecutively. (1 / 2 or press enter / 3 / 4) "
            ).strip(" ")

            if detail not in ["1", "2", "3", "4"] and detail != "":
                raise ValueError

            if detail == "":
                detail = "2"

            detail: int = int(detail)

        except ValueError:
            print("Please enter a number between 1 and 3 or press enter.")
            continue

        break
    return detail


def extract_image_dates(file_path):
    try:
        with ExifToolHelper() as et:
            metadata = et.get_metadata(file_path)
            modification_date = metadata[0].get("File:FileModifyDate")
        return modification_date

    except Exception:
        return None


def filename_regex(file: str):
    matches = re.search(
        r"^(.*?)(\(\d+\)| Kopie)?(\.\w+)$", file
    )  # also works for paths! apparently macos adds " Kopie" to copied files?
    return matches.groups()


def date_regex(date: str):
    matches = re.search(
        r"^(\d{4}):(\d{2}):(\d{2}) ([0-1][0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])((?:\+|-)\d{2}):(00)$",
        date
    )
    return matches.groups()


def get_pfd(src: str):  #  [[path, {"file": file, "date": date}], ...]
    pfd: list = []
    for dirpath, _, filenames in os.walk(src):
        for file in filenames:
            if not filename_regex(file)[1]:  # files with (1), (2), (3) etc. directly before the extension are ignored, since they are usually copies.
                fd_dict: dict = {}
                rpath = os.path.join(dirpath, file)
                date = extract_image_dates(rpath)
                if date:
                    fd_dict["file"] = file
                    fd_dict["date"] = date
                    pfd.append([dirpath, fd_dict])
    return pfd


def mkdir_y(pfd: list, dst: str):
    years = []
    for element in pfd:
        years.append(date_regex(element[1]["date"])[0])

    years = set(years)
    for year in years:
        os.makedirs(os.path.join(dst, year), exist_ok=True)
    return years


def mkdir_ym(pfd: list, dst: str):
    years_months = []
    for element in pfd:
        years_months.append(
            (date_regex(element[1]["date"])[0], date_regex(element[1]["date"])[1])
        )
    years_months = set(years_months)
    for year_month in years_months:
        os.makedirs(
            os.path.join(dst, year_month[0], f"{year_month[0]}-{year_month[1]}"),
            exist_ok=True,
        )
    return years_months


def mkdir_ymd(pfd: list, dst: str):
    years_months_days = []
    for element in pfd:
        years_months_days.append(
            (
                date_regex(element[1]["date"])[0],
                date_regex(element[1]["date"])[1],
                date_regex(element[1]["date"])[2],
            )
        )
    years_months_days = set(years_months_days)
    for year_month_day in years_months_days:
        os.makedirs(
            os.path.join(
                dst,
                year_month_day[0],
                f"{year_month_day[0]}-{year_month_day[1]}",
                f"{year_month_day[0]}-{year_month_day[1]}-{year_month_day[2]}",
            ),
            exist_ok=True,
        )
    return years_months_days


def mkdir_tool(folder_structure: int, pfd: list, dst: str):
    if folder_structure == 1:
        mkdir_y(pfd, dst)
    elif folder_structure == 2:
        mkdir_y(pfd, dst)
        mkdir_ym(pfd, dst)
    elif folder_structure == 3:
        mkdir_y(pfd, dst)
        mkdir_ym(pfd, dst)
        mkdir_ymd(pfd, dst)


def time_conv(s: str):
    time_format = "%Y:%m:%d %H:%M:%S%z"
    time_before_without_offset = ":".join(s[:-6])
    offset = ":".join(date_regex(s)[-2:])
    time_before_with_offset = time_before_without_offset + offset
    return time.mktime(time.strptime(s, time_format))


def num_remove_regex(s: str):
    matches = re.search(r"^(.*)(_\d+)(\.\w+)$", s)
    return matches.groups()[0], matches.groups()[2]


def copy_and_rename(src: str, dst: str, pfd: list, folder_structure: int):
    rdict: dict = {}
    for element in pfd:
        rpath = os.path.join(element[0], element[1]["file"])
        comp_time = time_conv(element[1]["date"])
        rdict[rpath] = comp_time, element[1]["date"]

    rdict = dict(sorted(rdict.items(), key=lambda item: item[1][1]))
    k = 1
    for key, value in rdict.items():
        rdict[key] = value[1]
        ext = filename_regex(key)[2]
        if folder_structure == 1:
            year = date_regex(rdict[key])[0]
            wpath = os.path.join(dst, year, f"{year}_{k}{ext}")
            shutil.copy2(key, wpath)

        elif folder_structure == 2:
            year = date_regex(rdict[key])[0]
            month = date_regex(rdict[key])[1]
            wpath = os.path.join(
                dst, year, f"{year}-{month}", f"{year}-{month}_{k}{ext}"
            )
            shutil.copy2(key, wpath)

        elif folder_structure == 3:
            year = date_regex(rdict[key])[0]
            month = date_regex(rdict[key])[1]
            day = date_regex(rdict[key])[2]
            wpath = os.path.join(
                dst,
                year,
                f"{year}-{month}",
                f"{year}-{month}-{day}",
                f"{year}-{month}-{day}_{k}{ext}",
            )
            shutil.copy2(key, wpath)

        elif folder_structure == 4:
            wpath = os.path.join(dst, f"{k}{ext}")
            shutil.copy2(key, wpath)
        k += 1

    for dirpath, _, filenames in os.walk(dst):
        k = 1
        for filename in sorted(filenames):
            num_removed = num_remove_regex(filename)
            os.rename(
                os.path.join(dirpath, filename),
                os.path.join(dirpath, f"{num_removed[0]}_{k}{num_removed[1]}"),
            )
            k += 1
