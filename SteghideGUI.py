import subprocess

import PySimpleGUI as sg
from PySimpleGUI import WIN_CLOSED

if __name__ == '__main__':
    steghide_path = 'steghide'
    enc_algos = subprocess.check_output([steghide_path, '--encinfo'], stderr=subprocess.STDOUT).decode('ascii').split('\n')
    enc_algos = enc_algos[2:-1]
    kv = {algo.split(':')[0]: algo.split(':')[1].split(' ')[1:] for algo in enc_algos}

    tab1_layout = [[sg.Text('Select Embed File', size=(15, 1)), sg.InputText(), sg.FileBrowse()],
                   [sg.Text('Select Cover File', size=(15, 1)), sg.InputText(), sg.FileBrowse()],
                   [sg.Checkbox('Write to existing Cover File', change_submits=True, enable_events=True, default=False,
                                key='ex_cover')],
                   [sg.Text('Select Output Folder', size=(15, 1), key='ex_cover_t'), sg.InputText(key='ex_cover_it'),
                    sg.FolderBrowse()],
                   [sg.Text('Output File Name', size=(15, 1), key='ex_cover_t2'), sg.InputText(key='file_name')],
                   [sg.Checkbox('Encryption', default=True, change_submits=True, enable_events=True, key='enc_cover')],
                   [sg.Text('Encryption Algorithm', size=(15, 1), key='enc_algo_txt'),
                    sg.Combo(list(kv.keys()), size=(10, 1), change_submits=True, enable_events=True, key='enc_algo')],
                   [sg.Text('Encryption Mode', size=(15, 1), key='enc_mode_txt'),
                    sg.Combo(list(), size=(10, 1), key='enc_mode')],
                   [sg.Checkbox('Compression', default=True, key='comp'),
                    sg.Slider(range=(1, 9), orientation='h', size=(45, 5), key='slider')],
                   [sg.Checkbox('Embed Checksum', default=True, key='checksum')],
                   [sg.Text('Passphrase', size=(15, 1)), sg.InputText(key='pass')],
                   [sg.Button('Embed')]]

    tab2_layout = [[sg.Text('Select File to Extract', size=(15, 1)), sg.InputText(), sg.FileBrowse(key='to_extract_file')],
                   [sg.Checkbox('Extract with New File Name', default=True, change_submits=True, enable_events=True, key='new_name')],
                   [sg.Text('Select Output Folder', size=(15, 1), key='new_folder_t'), sg.InputText(key='new_folder_it'),
                    sg.FolderBrowse(key='ext_out_folder')],
                   [sg.Text('Output File Name', size=(15, 1), key='ext_file_t'), sg.InputText(key='ext_file_name')],
                   [sg.Text('Passphrase', size=(15, 1)), sg.InputText(key='ext_pass')],
                   [sg.Button('Extract')]]

    layout = [[sg.TabGroup([[sg.Tab('Embed', tab1_layout), sg.Tab('Extract', tab2_layout)]])]]

    window = sg.Window('Steghide GUI', layout)

    while True:
        event, values = window.read()

        print(event)

        if event == WIN_CLOSED:
            break

        window['ex_cover_t'].update(visible=not values['ex_cover'])
        window['ex_cover_it'].update(visible=not values['ex_cover'])
        window['ex_cover_t2'].update(visible=not values['ex_cover'])
        window['file_name'].update(visible=not values['ex_cover'])
        window['Browse1'].update(visible=not values['ex_cover'])

        window['new_folder_t'].update(visible=values['new_name'])
        window['new_folder_it'].update(visible=values['new_name'])
        window['ext_file_t'].update(visible=values['new_name'])
        window['ext_file_name'].update(visible=values['new_name'])
        window['ext_out_folder'].update(visible=values['new_name'])

        window['enc_algo_txt'].update(visible=values['enc_cover'])
        window['enc_mode_txt'].update(visible=values['enc_cover'])

        window['enc_algo'].update(visible=values['enc_cover'])
        window['enc_mode'].update(visible=values['enc_cover'])

        if event == 'enc_algo':
            window['enc_mode'].update(values=kv[values['enc_algo']])


        if event == 'Embed':
            op = [steghide_path, '--embed', '-q',
                  '-ef', values['Browse'],
                  '-cf', values['Browse0']]
            if not values['ex_cover']:
                op.extend(['-sf', values['Browse1'] + '/' + values['file_name']])

            if values['enc_cover'] and values['enc_algo'] != '' and values['enc_mode'] != '':
                op.extend(['-e', values['enc_algo'] + ' ' + values['enc_mode']])
            else:
                op.extend(['-e', 'none'])

            if values['comp']:
                op.extend(['-z', str(int(values['slider']))])
            else:
                op.append('-Z')

            if not values['checksum']:
                op.append('-K')

            op.extend(['-p', values['pass']])

            try:
                sg.popup(subprocess.check_output(op, stderr=subprocess.STDOUT).decode("utf-8"))
            except subprocess.CalledProcessError as e:
                sg.popup(e.output.decode("utf-8"))

        if event == 'Extract':
            op = [steghide_path, '--extract', '-q', '-sf', values['to_extract_file']]
            if values['new_name']:
                op.extend(['-xf', values['new_folder_it'] + '/' + values['ext_file_name']])
            op.extend(['-p', values['ext_pass']])

            try:
                sg.popup(subprocess.check_output(op, stderr=subprocess.STDOUT).decode("utf-8"))
            except subprocess.CalledProcessError as e:
                sg.popup(e.output.decode("utf-8"))

    window.close()
