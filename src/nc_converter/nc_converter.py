import os

from copy import copy
from time import sleep

path_1 = r'W:\SOFT\py_nc_converter_1c_syntec\tests'

DIR_NAME_FANUC_TO_SYNTEC = 'converted to syntec'
DIR_NAME_SYNTEC_TO_FANUC = 'converted to fanuc'


def generate_list_of_possible_nc_names() -> list[str]:

    NC_NAMES = []
    NC_LETTERS = ["O", "o"]
    PP_SERIES = ["6", "7"]

    for nc_letter in NC_LETTERS:
        for pp_serial in PP_SERIES:
            for ust_no in range(0, 10):
                ust_no = str(ust_no)
                for nc_no in range(0, 100):
                    if nc_no < 10:
                        nc_no = "0" + str(nc_no)
                    else:
                        nc_no = str(nc_no)
                    nc_name_in_list = f"{nc_letter}{pp_serial}{ust_no}{nc_no}"
                    NC_NAMES.append(nc_name_in_list)

    return NC_NAMES


def get_NC_files(
    *, directory: str, all_possible_nc_names: list[str]
) -> list[str]:
    nc_files = []
    all_files_found = os.listdir(path=directory)
    for filename in all_files_found:
        if filename in all_possible_nc_names:
            nc_files.append(filename)
    return nc_files


def convert_nc_from_syntec_to_fanuc(dir: str, filename: str) -> None:
    print(f'Converting {filename} from Syntec to Fanuc . . .')
    with open(f'{directory}\{filename}', 'r') as f:
        source_lines = f.readlines()
    
    result_lines = [f'%;\n', f'{filename};\n']
    
    for line in source_lines:
        if '//.T' in line:
            line: str = copy(line)
            line = line.replace('//.T', '(T')
            line = line.replace(';', ');')
            result_lines.append(line)
        elif '//..T' in line:
            parts = line.split('//')
            parts[0] += ' M6 '
            parts[1] = parts[1].replace('..', '')
            parts[1] = parts[1].replace(';', ');')
            parts[1] = ''.join(['(', parts[1]])
            result_lines.append(''.join(parts))
        else:
            result_lines.append(line)
    result_lines.append('%;\n')
    m_line = result_lines.pop(2)
    result_lines.insert(5, m_line)
    
    with open(f'{directory}\{DIR_NAME_SYNTEC_TO_FANUC}\{filename}', 'w') as f:
        f.writelines(result_lines)


def convert_nc_from_fanuc_to_syntec(dir: str, filename: str) -> None:
    print(f'Converting {filename} from Fanuc to Syntec . . .')
    with open(f'{directory}\{filename}', 'r') as f:
        source_lines = f.readlines()
    
    # result_lines = [f'{filename};\n']
    result_lines = []
    
    for line in source_lines:
        if '%' in line:
            continue
        elif filename in line:
            line = line.replace(filename, '').lstrip()
            result_lines.append(line)
        elif 'M6' in line:
            parts = line.split(sep='M6')
            parts[0] = parts[0].strip()
            parts[1] = parts[1].replace('(', '//..').strip()
            parts[1] = parts[1].replace(')', '')
            
            line = ''.join(parts)
            
            # result_lines.append(line)
            result_lines.insert(0, line)
        elif 'M98' in line:
            line = line.replace('(', '//.')
            line = line.replace(')', '')
            result_lines.append(line)
        else:
            result_lines.append(line)

    
    with open(f'{directory}\{DIR_NAME_FANUC_TO_SYNTEC}\{filename}', 'w') as f:
        f.writelines(result_lines)



def get_file_nc_type(directory: str, file_name: str) -> int:
    """
    1 = Fanuc
    2 = Syntec
    """
    with open(f'{directory}\{file_name}', 'r') as f:
        first_line = f.readline()
    if '%' in first_line:
        return 1
    else:
        return 2


def create_subdir_if_not_present(cwd: str, dir_name: str):
    if not os.path.isdir(f'{cwd}/{dir_name}'):
        os.mkdir(f'{cwd}/{dir_name}')
    

def main(*, directory: str) -> None:
    all_possible_nc_names = generate_list_of_possible_nc_names()

    nc_files = get_NC_files(
        directory=directory, all_possible_nc_names=all_possible_nc_names
    )

    for nc_file in nc_files:
        nc_file_type = get_file_nc_type(directory=directory, file_name=nc_file)
        
        if nc_file_type == 1:
            create_subdir_if_not_present(
                cwd=directory, dir_name=DIR_NAME_FANUC_TO_SYNTEC)            
            convert_nc_from_fanuc_to_syntec(directory, nc_file)
        elif nc_file_type == 2:
            create_subdir_if_not_present(
                cwd=directory, dir_name=DIR_NAME_SYNTEC_TO_FANUC)            
            convert_nc_from_syntec_to_fanuc(directory, nc_file)


if __name__ == "__main__":
    # directory = path_1
    directory = os.getcwd()
    if os.path.isdir(directory):
        try:
            main(directory=directory)
        except FileNotFoundError:
            print("Smth went wrong")
            print("Window will be closed in 10 seconds")
            sleep(10)
