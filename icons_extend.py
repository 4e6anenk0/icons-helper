import re
import subprocess
import os
from lxml import etree
from typing import List, Literal
from svgutils.transform import *


CASE_GET = Literal['deep', 'dir', 'test']

def this_path():
    result = subprocess.run(
        'pwd',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding='utf-8'
    )
    return result.stdout


def cmd(cmd: str, shell=False):
    result = ''
    if shell:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-8',
            shell=True
        )
    else:
        result = subprocess.run(
            cmd.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-8'
        )
    return result.stdout.strip()


def _get_command_result(command: list, path: str, *args: str):
    
    def get_subproc_result(command):
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-8'
        )
        return result.stdout

    if (os.path.isdir(path) == True and not args):  
        return(get_subproc_result(command))
    
    elif (os.path.isdir(path) == True and args):
        new_commands = command
        for el in args:
            new_commands.append(el)
        return(get_subproc_result(new_commands))
    
    else:
        print('Failed to get the result. Perhaps the wrong command was transmitted or the path does not indicate the directory')


def get_all_file_in(path: str, case_param: CASE_GET):
    print('run: get_all_file_in')
    match case_param:
        case 'deep': 
            print('case: deep')
            return (_get_command_result(['find', path, '-type', 'f'], path))
        case 'dir':
            print('case: dir')
            return (_get_command_result(['find', path, '-maxdepth', '1', '-type', 'f'], path))
        case 'file':
            return (icon_extend())
        case 'test':
            return (this_path())
        case _:
            return (_get_command_result(['find', path, '-maxdepth', '1', '-type', 'f'], path))


def row_to_list(raw_data: str):
    return(raw_data.split())

def get_float_size_value(fig: SVGFigure) -> float:
    height = 1.0
    width = 1.0
    match_value_height = ''
    match_value_width = ''
    if fig.width and fig.height:
        match_value_height = re.search(r'\d+', fig.height)
        match_value_width = re.search(r'\d+', fig.width)
        if match_value_height and match_value_width:
            height = float(match_value_height.group())
            width = float(match_value_width.group())
    else:
        f_list = str(fig.root.get('viewBox')).split()
        match_value_height = f_list[3]
        match_value_width = f_list[2]
        height = float(match_value_height)
        width = float(match_value_width)

    return {'width': width, 'height': height}


def icon_extend(path_to_icon: str, new_icon_width: int, new_icon_height: int, dump: str):

    ''' This is the main function for implementing the extension. \
        Extend is making the canvas bigger but keeping the size and position of the icon '''

    print("Processing... {}".format(path_to_icon))
    
    fig = fromfile(path_to_icon)
    new_fig = SVGFigure()

    current_height = get_float_size_value(fig=fig)['height']
    current_width = get_float_size_value(fig=fig)['width']

    bias_factor_x = float(new_icon_width) / current_width - 1
    bias_factor_y = float(new_icon_height) / current_height - 1
    
    x_offset_center = current_width / 2
    y_offset_center = current_height / 2
    
    root = fig.getroot()
    root.moveto(x_offset_center * bias_factor_x,
                y_offset_center * bias_factor_y)

    name_file = cmd('basename {}'.format(path_to_icon)).splitlines()[0]

    if not os.path.isdir(dump):
        cmd('mkdir -p {}'.format(dump))
    
    dump_path = '{}/{}'.format(dump, name_file)
    
    new_fig.append(root)
    new_fig.set_size(("{}px".format(new_icon_width), "{}px".format(new_icon_height)))
    new_fig.save(dump_path)


def icons_extend(path_list: List[str], width, height, path, case_param: CASE_GET, dump=this_path()):
    print(path_list)
    for el in path_list:
        icon_extend(el, width, height, dump)
    restore_symlinks(path=path, dump=dump, case_param=case_param)
    print('All files were successfully processed. You can find files along this path: {}'.format(dump))


def restore_symlinks(path: str, dump: str, case_param: CASE_GET):
    print('Restoring symlinks...')
    match case_param:
        case 'deep':
            symlinks = cmd(
                'find {} -type l'.format(path))

            symlinks_name = []

            for el in symlinks.split():
                symlinks_name.append(cmd('basename {}'.format(el)))

            for link in symlinks_name:
                print('Link: {}'.format(link))
                path_symlink = '{}/{}'.format(path, link)

                target = cmd(
                    'readlink -f {} | xargs basename'.format(path_symlink), shell=True)

                cmd('ln -s {} {}'.format('{}/{}'.format(dump, target),
                                         '{}/{}'.format(dump, link)))
        case 'dir':
            symlinks = cmd(
                'find {} -maxdepth 1 -type l'.format(path))

            symlinks_name = []

            for el in symlinks.split():
                symlinks_name.append(cmd('basename {}'.format(el)))
            
            for link in symlinks_name:
                print('Link: {}'.format(link))
                path_symlink = '{}/{}'.format(path, link)

                target = cmd(
                    'readlink -f {} | xargs basename'.format(path_symlink), shell=True)
                
                cmd('ln -s {} {}'.format('{}/{}'.format(dump, target),
                                         '{}/{}'.format(dump, link)))
        case _:
            print("not matched")
