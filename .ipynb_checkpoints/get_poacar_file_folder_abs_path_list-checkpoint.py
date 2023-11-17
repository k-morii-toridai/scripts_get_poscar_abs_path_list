import re
import itertools
from tqdm import tqdm
from pathlib import Path
from multiprocessing import Pool, cpu_count

import numpy as np


def iterdir_func(poscar_dir):
    return list(poscar_dir.iterdir())


def flatten_func(list_2dim):
    return list(itertools.chain.from_iterable(list_2dim))


def get_subdir_list(dir_list):
    return flatten_func(list(map(iterdir_func, dir_list)))


p = Path('/mnt/ssd_elecom_black_c2c/cif/')
p_s_list = [p_sub_folder for p_sub_folder in p.glob('[1-9]')]
p_ssss_list = get_subdir_list(get_subdir_list(get_subdir_list(p_s_list)))


def poscar_folder_filter(path):
    pattern = '[0-9]{6}$'  # 正規表現（：末尾が数字６文字で終わる）
    string = str(path)
    return bool(re.search(pattern, string))


# make filter
poscar_folder_path_list_filter = list(map(poscar_folder_filter, p_ssss_list))
# apply filter to p_ssss_list
poscar_folder_path_list = np.array(p_ssss_list)[poscar_folder_path_list_filter]
print(f'len(poscar_folder_path_list): {len(poscar_folder_path_list)}')


# 並列化(POSCARファイルのあるディレクトリの，ファイルorフォルダ一覧を取得)
try:
    pp = Pool(cpu_count() - 1)
    # iterdir
    poscar_mixed_path_list = list(tqdm(pp.imap(iterdir_func, poscar_folder_path_list), total=len(poscar_folder_path_list)))
    # flatten
    poscar_mixed_path_list = flatten_func(poscar_mixed_path_list)
finally:
    pp.close()
    pp.join()


def poscar_file_filter(path):
    pattern = '[0-9]{6}/POSCAR$'  # 正規表現（：末尾が '数字６桁/POSCAR'で終わる）
    string = str(path)
    return bool(re.search(pattern, string))


# make filter
poscar_file_path_list_filter = list(map(poscar_file_filter, poscar_mixed_path_list))
# apply filter to poscar_mixed_path_list
poscar_file_path_list = np.array(poscar_mixed_path_list)[poscar_file_path_list_filter]
print(f"len(poscar_file_path_list): {len(poscar_file_path_list)}")
# save poscar_file_path_list as .npy
np.save('poscar_abs_path_list.npy', poscar_file_path_list)


# make poscar_file_existed_folder_abs_path_list
poscar_folder_path_list = [Path(str(p)[:-7]) for p in poscar_file_path_list]
print(f'len(poscar_folder_path_list): {len(poscar_folder_path_list)}')
# save as .npy file
np.save('poscar_folder_abs_path_list.npy', poscar_folder_path_list)
