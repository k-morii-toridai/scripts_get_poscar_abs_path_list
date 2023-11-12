import re
import time
import itertools
import subprocess
from tqdm import tqdm
from pathlib import Path
from multiprocessing import Pool, cpu_count 
import numpy as np


def get_subdir_list(p_sub_list):
    """
    To get a sub directory path list, Use thie func().
    
    pram: p_aub_list: specify a directory which sub dirs is gotten from.
    """
    # 引数の直下のディレクトリ・パスの一覧を取得
    sub_dir_list_temp = []
    for p_sub in tqdm(p_sub_list):
        sub_dir_list_temp.append([p_s_s for p_s_s in p_sub.iterdir()])
    # ２次元リストを１次元リスト化
    return sum(sub_dir_list_temp, [])


p = Path('/mnt/ssd_elecom_black_c2c/cif/')
p_sub_list = [p_s for p_s in p.glob('[1-9]')]

cif_path_list = get_subdir_list(get_subdir_list(get_subdir_list(p_sub_list)))
print(f"len(cif_path_list): {len(cif_path_list)}")


def poscar_folder_filter(path):   
    path_str = str(path)
    return not('.cif' in path_str)


poscar_folder_path_list_filter = list(map(poscar_folder_filter, cif_path_list))
poscar_folder_path_list = np.array(cif_path_list)[poscar_folder_path_list_filter]
print(f"len(poscar_folder_path_list): {len(poscar_folder_path_list)}")


def iterdir_func(poscar_dir):
    return list(poscar_dir.iterdir())
    
def flatten_func(list_2dim):
    return list(itertools.chain.from_iterable(list_2dim))

# 並列化
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
    pattern = '.+/POSCAR$'
    string = str(path)
    return re.search(pattern, string)

poscar_file_path_list = [path for path in poscar_mixed_path_list if poscar_file_filter(path)]
print(f"len(poscar_file_path_list): {len(poscar_file_path_list)}")
np.save('poscar_abs_path_list.npy', np.array(poscar_file_path_list))
    