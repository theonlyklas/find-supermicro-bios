import requests
import pdb
from bs4 import BeautifulSoup
import time
import os
import sys
import re
import fnmatch
from enum import Enum

global PAGE_SAVE_PATH
PAGE_SAVE_PATH = "D:\\Programming\\find-supermicro-bios\\Pages"
global BASE_DOWNLOAD_URL 
BASE_DOWNLOAD_URL = "https://www.supermicro.com/support/resources/getfile.php?SoftwareItemID="
global DEAD_PAGE_INDICES 
DEAD_PAGE_INDICES = []
global VALID_CHOICES_Y_N
VALID_CHOICES_Y_N = ['y', 'n']

global GENERIC_Y_N_PROMPT
GENERIC_Y_N_PROMPT = SafeUserPrompt("Please enter Y/N: ", "Please enter Y/N: ", VALID_CHOICES_Y_N)
global GENERIC_SAFE_INDEX_PROMPT
GENERIC_SAFE_INDEX_PROMPT = SafeIndexPrompt(SafeUserPrompt("Specify index, valid index must be >= 0: " + BASE_DOWNLOAD_URL, "INVALID INDEX! Specify index, valid index must be >= 0: " + BASE_DOWNLOAD_URL, myValidChoices=None))

class SafeUserPrompt:
    def default_constructor(self):
        return SafeUserPrompt(self, myUserPrompt="Please specify a valid user prompt, error text, and choices.", myErrorText="Please specify a valid user prompt, error text, and choices.", myValidChoices=None)

    def __init__(self, myUserPrompt, myErrorText, myValidChoices):
        UserPrompt = myUserPrompt
        ErrorText = myErrorText
        ValidChoices = myValidChoices

    def get_choice_safely(self):
        choice = ""

        while (True):
            try:
                choice = input(UserPrompt).lower()
                if (True == (choice in ValidChoices)):                
                    break
                else:
                    print(ErrorText)
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print(ErrorText)

        return choice

class SafeIndexPrompt(SafeUserPrompt):
    def __init__(self, myUserPrompt, myErrorText, myValidChoices):
        UserPrompt = myUserPrompt
        ErrorText = myErrorText
        ValidChoices = None

    def get_choice_safely(self):
        requested_index = -1

        while (True):
            try:
                requested_index = int(input(UserPrompt))
                if (True == (requested_index >= 0)):                
                    break
                else:
                    print(ErrorText)
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print(ErrorText)
        
        return requested_index

class ScriptRunMode(Enum):
    INVALID_RUN_MODE = -1
    DOWNLOAD_FILE_RANGE = 0
    SEARCH_DOWNLOADED_FILES = 1

class ScriptParametersBase:
    RunMode = ScriptRunMode.INVALID_RUN_MODE
    PathToSavedPages = ""
    
class DownloadFiles(ScriptParametersBase):
    def default_constructor(self):
        return DownloadFiles(myRunMode = ScriptRunMode.INVALID_RUN_MODE, myPathToSavedPages = "", myIndicesToDownload = [])

    def __init__(self, myRunMode, myPathToSavedPages, myIndicesToDownload):
        RunMode = myRunMode
        PathToSavedPages = myPathToSavedPages
        IndicesToDownload = myIndicesToDownload

class SearchDownloadedFiles(ScriptParametersBase):
    def default_constructor(self):
        return SearchDownloadedFiles(myRunMode = ScriptRunMode.INVALID_RUN_MODE, myPathToSavedPages = "", myFilenameToFind = "")

    def __init__(self, myRunMode, myFilenameToFind, myPathToSavedPages):
        RunMode = myRunMode
        PathToSavedPages = myPathToSavedPages
        FilenameToFind = myFilenameToFind

def get_page(url, i):
    page = requests.get(url)
    if (page.url != url):
        save_page(page, i)
    else:
        DEAD_PAGE_INDICES.append(i)

def save_page(page, i):
    try:
        os.mkdir(PAGE_SAVE_PATH + "/" + str(i), 755)
    except Exception as e:
        #TODO: look for changes in files?
        print(e)

    print("attempting to save " + page.url)
    try:
        open(PAGE_SAVE_PATH + "/" + str(i) + "/" + page.url[page.url.rfind('/'):], 'wb').write(page.content)
        print("SUCCESSFULLY saved " + page.url)
    except Exception as e:
        print("FAILED to save " + page.url)
        print(e)

def save_dead_page_indices():
    print("attempting to save dead page indices")
    try:   
        dead_page_file = open(PAGE_SAVE_PATH + "/_DEADPAGES_.TXT", 'w')

        for i in range(len(DEAD_PAGE_INDICES)):
            dead_page_file.write(str(DEAD_PAGE_INDICES[i]) + ",")
        
        dead_page_file.close()

        print("SUCCESSFULLY saved dead page indices: " + str(len(DEAD_PAGE_INDICES)))
    except Exception as e:
        print("FAILED to save dead page indices: " + str(len(DEAD_PAGE_INDICES)))
        print(e)

def find_last_downloaded_file_index():
    max_so_far = 0
    for root, dirs, files in os.walk(PAGE_SAVE_PATH):
        directory_name_index = root.rfind('Pages\\')
        if (-1 != directory_name_index):
            directory_name_index += len("Pages\\")
            file_index = int(root[directory_name_index:])

            if (file_index > max_so_far):
                max_so_far = file_index

    return max_so_far

def find_all_matches_by_pattern(pattern_to_find, path):
    print("attempting to find all pattern matches of " + pattern_to_find + " in " + path)
    files_found = []
    try:
        for root, dirs, files in os.walk(path):
            for name in files:
                if fnmatch.fnmatch(name, pattern_to_find):
                    files_found.append(os.path.join(root, name))
    except Exception as e:
        print("Something went wrong trying to find all pattern matches of " + pattern_to_find + " in " + path)
        print(e)

    return files_found

def find_all_matches(filename_to_find, path):
    print("attempting to find all matches of " + filename_to_find + " in " + path)
    files_found = []
    try:
        for root, dirs, files in os.walk(path):
            if filename_to_find in files:
                files_found.append(os.path.join(root, filename_to_find))
    except Exception as e:
        print("Something went wrong trying to find all matches of " + filename_to_find + " in " + path)
        print(e)

    return files_found

def find_first_matching_file(filename_to_find, path):
    try:
        for root, dirs, files in os.walk(path):
            if name in files:
                return os.path.join(root, name)
    except Exception as e:
        print("Something went wrong while trying to find the first matching file for " + filename_to_find + " in " + path)
        print(e)
    
    return ""

def find_file_in_saved_pages(filename_to_find):
    print("attempting to find " + filename_to_find)
    try:
        matches = find_all_matches(filename_to_find, PAGE_SAVE_PATH)

        if (len(matches) > 0):
            print("Files found!")
            for match in matches:
                print(match)
        else:
            matches = find_all_matches(filename_to_find, PAGE_SAVE_PATH)
    except Exception as e:
        print("Something went wrong while attempting to find " + filename_to_find)
        print(e)

def create_download_files_script_parameters():
    AnotherDownloadIndexRangePrompt = SafeUserPrompt("Do you want to specify another range of file indices to download? Y/N", "Do you want to specify another range of file indices to download? Y/N", VALID_CHOICES_Y_N)
    StartingEndingIndexSwapPrompt = SafeUserPrompt("Your starting file download index is greater than your ending file download index.  Do you want to SWAP these values or DISCARD this range?  S/D:", "Your starting file download index is greater than your ending file download index.  Do you want to SWAP these values or DISCARD this range?  S/D:", ["s", "d"])
    script_downloading_files_parameters = DownloadFiles.default_constructor(ScriptParametersBase())

    choice = "y"
    while ("y" == choice):
        try:
            if (len(script_downloading_files_parameters.IndicesToDownload) > 0):
                print("Currently specified page ranges to download:")
                for index_ranges in script_downloading_files_parameters.IndicesToDownload:
                    print(str(index_ranges))

            print("Specifying STARTING index of next range of files to download.")
            starting_index = GENERIC_SAFE_INDEX_PROMPT.get_choice_safely()
            print("Specifying ENDING index of next range of files to download.")
            ending_index = GENERIC_SAFE_INDEX_PROMPT.get_choice_safely()

            if (starting_index > ending_index):
                index_swap_choice = StartingEndingIndexSwapPrompt.get_choice_safely()

                if ('s' == index_swap_choice):
                    script_downloading_files_parameters.IndicesToDownload.append([ending_index, starting_index])
                else:
                    continue
            else:
                script_downloading_files_parameters.IndicesToDownload.append([starting_index, ending_index])
            
            choice = AnotherDownloadIndexRangePrompt.get_choice_safely()
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print("Error occured!")
            print(e)
            choice = AnotherDownloadIndexRangePrompt.get_choice_safely()
    
    return script_downloading_files_parameters

def create_search_files_script_parameters():
    while 
    try:
        choice = ("Search for a file in your downloaded pages? Y/N")
        if ("Y" == choice or "y" == choice):
            choice = input("Do you want to use pattern matching?")

            if ("Y" == choice or "y" == choice):
                filename_to_find = input("Enter a pattern to search for:  ")

            return
    except Exception as e:
        print("Something went wrong setting the starting index for downloading!")
        print(e)

    return -1

def ask_for_script_parameters():
    script_parameters = create_download_files_script_parameters()

    if (ScriptRunMode.INVALID_RUN_MODE != script_parameters.RunMode):
        return script_parameters
    
    script_parameters = create_search_files_script_parameters()
    if (ScriptRunMode.INVALID_RUN_MODE != script_parameters.RunMode):
        return script_parameters

def main():
    if (1 == len(sys.argv)):
        script_parameters = ask_for_script_parameters()

    
    if (ScriptRunMode.INVALID_RUN_MODE == script_parameters.RunMode):
        print("Invalid script run mode specified!")
        return

    if (ScriptRunMode.DOWNLOAD_FILE_RANGE == script_parameters.RunMode):
        try:
            os.mkdir(script_parameters.PAGE_SAVE_PATH, 755)
        except:
            print("")

        i_exception_shift = 0
        range_start = find_last_downloaded_file_index()
        print("Grabbing files starting at " + str(range_start))

        for i in range(range_start, 1000000):
            try:
                i -= i_exception_shift
                url = BASE_DOWNLOAD_URL + str(i)
                get_page(url, i)

                if (i % 10 == 0):
                    print(i)
                    save_dead_page_indices()

                time.sleep(1)
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print(e)
                print("error occured WTF")
                i_exception_shift += 1
                time.sleep(10)

main()