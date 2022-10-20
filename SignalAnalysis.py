import math
import numpy as np
import PySimpleGUI as sg
import matplotlib.pyplot as plt
import ctypes
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from scipy.signal import find_peaks

# Functions to prevent GUI blurring
def make_dpi_aware():
    import ctypes
    import platform
    if int(platform.release()) >= 8:
        ctypes.windll.shcore.SetProcessDpiAwareness(True)

make_dpi_aware()

# Function for drawing
def draw_figure_w_toolbar(canvas, figure, canvas_toolbar):
    if canvas.children:
        for child in canvas.winfo_children():
            child.destroy()
    if canvas_toolbar.children:
        for child in canvas_toolbar.winfo_children():
            child.destroy()
    figure_canvas_agg = FigureCanvasTkAgg(fig, master=canvas)
    figure_canvas_agg.draw()
    toolbar = Toolbar(figure_canvas_agg, canvas_toolbar)
    toolbar.update()
    figure_canvas_agg.get_tk_widget().pack(side='right', fill='both', expand=1)


class Toolbar(NavigationToolbar2Tk):
    def __init__(self, *args, **kwargs):
        super(Toolbar, self).__init__(*args, **kwargs)

def validate(values):
    is_valid = True
    values_invalid = []

    if len(values['-harmonica1-']) == 0:
        values_invalid.append('Harmonica 1 (Hz)')
        is_valid = False

    if len(values['-harmonica2-']) == 0:
        values_invalid.append('Harmonica 2 (Hz)')
        is_valid = False

    if len(values['-harmonica3-']) == 0:
        values_invalid.append('Harmonica 3 (Hz)')
        is_valid = False

    if len(values['-harmonica4-']) == 0:
        values_invalid.append('Harmonica 4 (Hz)')
        is_valid = False

    if len(values['-harmonica5-']) == 0:
        values_invalid.append('Harmonica 5 (Hz)')
        is_valid = False

    if len(values['-amplitude-']) == 0:
        values_invalid.append('Amplitude (V/I)')
        is_valid = False

    elif int(values['-amplitude-']) == 0:
        values_invalid.append('Amplitude (V/I)')
        is_valid = False

    result = [is_valid, values_invalid]

    return result

def generate_error_message(values_invalid):
    error_message = ''
    for value_invalid in values_invalid:
        error_message += ('\nCampo ** {} ** vazio ou nulo'.format(value_invalid))

    return error_message

def sum_of_squares(lst):
    sum = 0
    for x in lst:
        sum = sum + x ** 2
    return sum

user32 = ctypes.windll.user32
screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
sg.theme('dark teal 9')

entradas = [[sg.Text('ANALISE DE SINAIS')],
            [sg.Push(), sg.T('Harmonica 1 (Hz):'), sg.Input(enable_events=True, key='-harmonica1-', size=(3, 1))],
            [sg.Push(), sg.T('Harmonica 2 (Hz):'), sg.Input(enable_events=True, key='-harmonica2-', size=(3, 1))],
            [sg.Push(), sg.T('Harmonica 3 (Hz):'), sg.Input(enable_events=True, key='-harmonica3-', size=(3, 1))],
            [sg.Push(), sg.T('Harmonica 4 (Hz):'), sg.Input(enable_events=True, key='-harmonica4-', size=(3, 1))],
            [sg.Push(), sg.T('Harmonica 5 (Hz):'), sg.Input(enable_events=True, key='-harmonica5-', size=(3, 1))],
            [sg.Push(), sg.T('Amplitude (V/I) :'), sg.Input(enable_events=True, key='-amplitude-', size=(3, 1))],
            [sg.Button('Plotar gráfico'), sg.Button('Limpar')],[sg.Multiline(size=(2, 10), key='-ML1-', expand_x=True, expand_y=True, no_scrollbar=True)]]
# Layout creation
graficos = [[sg.Canvas(key='controls_cv', expand_x=True, expand_y=True)],[sg.Canvas(key='-CANVAS-', expand_x=True, expand_y=True)],
            [sg.Button('Importar',expand_x=True, expand_y=True), sg.Button('Exportar',expand_x=True, expand_y=True),
             sg.Button('Exportar FFT',expand_x=True, expand_y=True)]]

layout = [[sg.Column(entradas,  vertical_alignment='top'), sg.VSeperator(), sg.Column(graficos)]]

# Create a window. finalize=Must be True.
window = sg.Window('ANALISE DE SINAIS', layout, size=(screensize), finalize=True,
                   element_justification='center', font='Monospace 10', resizable=True)
window.Maximize()
# Create a fig for embedding.
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))

# Associate fig with Canvas.
draw_figure_w_toolbar(window['-CANVAS-'].TKCanvas, fig, window['controls_cv'].TKCanvas)
ax1.set_ylabel('Tensão(V) / Corrente(I)')
ax1.set_xlabel('Tempo (s)')
ax2.set_ylabel('Amplitude')
ax2.set_xlabel('Frequência (Hz)')

#Variaveis globais
t_global = ''
s_global = ''
file_global = ''
s_import_array = ''
t_import_array = ''
frequencias_global = ''
amplitudes_global = ''

# Event loop
def main():
    while True:
        event, values = window.read()

        if event in (None, "Cancel"):
            break

        elif event == "Plotar gráfico":
            ax1.cla()
            ax2.cla()
            ax1.set_ylabel('Tensão(V) / Corrente(I)')
            ax1.set_xlabel('Tempo (s)')
            ax2.set_ylabel('Amplitude')
            ax2.set_xlabel('Frequência (Hz)')
            draw_figure_w_toolbar(window['-CANVAS-'].TKCanvas, fig, window['controls_cv'].TKCanvas)
            validation_result = validate(values)
            if validation_result[0]:
                ha1 = int(values['-harmonica1-'])
                ha2 = int(values['-harmonica2-'])
                ha3 = int(values['-harmonica3-'])
                ha4 = int(values['-harmonica4-'])
                ha5 = int(values['-harmonica5-'])
                a1 = int(values['-amplitude-'])
                a2 = a1/4
                a3 = a2/3
                a4 = a3/3
                a5 = a4/3
                t = np.linspace(0, 0.1, 1000)
                t_global = t
                s = a1 * np.sin(ha1 * 2 * np.pi * t) + a2 * np.sin(ha2 * 2 * np.pi * t) + a3 * np.sin(ha3 * 2 * np.pi * t) + a4 * np.sin(ha4 * 2 * np.pi * t) + a5 * np.sin(ha5 * 2 * np.pi * t)
                s_global = s
                grafico1 = ax1.plot(t, s)
                ax1.set_ylabel('Tensão(V) / Corrente(I)')
                ax1.set_xlabel('Tempo (s)')
                draw_figure_w_toolbar(window['-CANVAS-'].TKCanvas, fig, window['controls_cv'].TKCanvas)
                fft = np.fft.fft(s)
                T = t[1] - t[0]
                N = s.size
                f = np.fft.fftfreq(len(s), T)
                frequencias = f[:N // 2]
                frequencias_global = frequencias
                amplitudes = np.abs(fft)[:N // 2] * 1 / N
                amplitudes_global = amplitudes
                peaks,_ = find_peaks(amplitudes)
                harm_freq_list = []
                harm_ampli_list = []
                print(type(harm_freq_list))
                print(type(harm_ampli_list))

                for i in range(len(peaks)):
                    harm_freq_list.append(frequencias[peaks[i]])

                for j in range(len(peaks)):
                    harm_ampli_list.append(amplitudes[peaks[j]])


                print('harm_freq_list',harm_freq_list)
                print('harm_ampli_list',harm_ampli_list)
                sum_all = sum_of_squares(harm_ampli_list)
                print('sum_all', sum_all)
                max_freq = max(harm_freq_list)
                max_ampli = max(harm_ampli_list)
                THD = (math.sqrt((sum_all-(max_ampli ** 2))/max_ampli ** 2))*100
                grafico2 = ax2.bar(frequencias, amplitudes)
                ax2.set_ylabel('Amplitude')
                ax2.set_xlabel('Frequência (Hz)')
                ax2.set_xlim([0, max_freq+15])
                draw_figure_w_toolbar(window['-CANVAS-'].TKCanvas, fig, window['controls_cv'].TKCanvas)
                window['-ML1-'].update('THD é: {:0.1f}%'.format(THD))

            else:
                error_message = generate_error_message(validation_result[1])
                sg.popup(error_message)

        elif event == 'Importar':
            filename = sg.popup_get_file('Will not see this message', no_window=True, multiple_files=False,
                                         file_types=(('.txt', '*.txt*'),), )

            if filename == '':
                main()

            ax1.cla()
            ax2.cla()
            draw_figure_w_toolbar(window['-CANVAS-'].TKCanvas, fig, window['controls_cv'].TKCanvas)

            with open(filename, 'r') as myfile:
                linhas_t = myfile.readlines()[0:1000]
                t_import = []
                for sub in linhas_t:
                    t_import.append(sub.replace("\n", ""))
            t_import_array = np.array(t_import)
            t_import_array_float = np.asarray(t_import_array, dtype=float)

            with open(filename, 'r') as myfile:
                linhas_s = myfile.readlines()[1000:2000]
                s_import = []
                for sub in linhas_s:
                    s_import.append(sub.replace("\n", ""))
            s_import_array = np.array(s_import)
            s_import_array_float = np.asarray(s_import_array, dtype=float)

            grafico1 = ax1.plot(t_import_array_float, s_import_array_float)
            ax1.set_ylabel('Tensão(V) / Corrente(I)')
            ax1.set_xlabel('Tempo (s)')
            draw_figure_w_toolbar(window['-CANVAS-'].TKCanvas, fig, window['controls_cv'].TKCanvas)
            fft = np.fft.fft(s_import_array_float)
            T = t_import_array_float[1] - t_import_array_float[0]
            N = s_import_array_float.size
            f = np.fft.fftfreq(len(s_import_array_float), T)
            frequencias = f[:N // 2]
            amplitudes = np.abs(fft)[:N // 2] * 1 / N
            peaks,_ = find_peaks(amplitudes)
            harm_freq_list = []
            harm_ampli_list = []

            for i in range(len(peaks)):
                harm_freq_list.append(frequencias[peaks[i]])

            for j in range(len(peaks)):
                harm_ampli_list.append(amplitudes[peaks[j]])

            sum_all = sum_of_squares(harm_ampli_list)
            max_freq = max(harm_freq_list)
            max_ampli = max(harm_ampli_list)
            THD = (math.sqrt((sum_all - (max_ampli ** 2)) / max_ampli ** 2)) * 100
            grafico2 = ax2.bar(frequencias, amplitudes)
            ax2.set_ylabel('Amplitude')
            ax2.set_xlabel('Frequência (Hz)')
            ax2.set_xlim([0, max_freq + 15])
            draw_figure_w_toolbar(window['-CANVAS-'].TKCanvas, fig, window['controls_cv'].TKCanvas)
            window['-ML1-'].update('THD é: {:0.1f}%'.format(THD))

        elif event == 'Exportar':
            filename = sg.tk.filedialog.asksaveasfile(defaultextension='txt')
            if filename == None:
                main()

            else:
                with open(filename.name, "w") as f:
                    f.write('\n'.join(map(str, t_global)))
                    f.write('\n')
                    f.write('\n'.join(map(str, s_global)))
                    f.close()

        elif event == 'Exportar FFT':
            filename = sg.tk.filedialog.asksaveasfile(defaultextension='txt')
            if filename == None:
                main()

            else:
                with open(filename.name, "w") as f:
                    f.write('\n'.join(map(str, frequencias_global)))
                    f.write('\n')
                    f.write('\n'.join(map(str, amplitudes_global)))
                    f.close()

        elif event == 'Limpar':
            ax1.cla()
            ax2.cla()
            t_global = ''
            s_global = ''
            frequencias_global = ''
            amplitudes_global = ''
            ax1.set_ylabel('Tensão(V) / Corrente(I)')
            ax1.set_xlabel('Tempo (s)')
            ax2.set_ylabel('Amplitude')
            ax2.set_xlabel('Frequência (Hz)')
            window['-ML1-'].update('')
            draw_figure_w_toolbar(window['-CANVAS-'].TKCanvas, fig, window['controls_cv'].TKCanvas)

        elif event == '-harmonica1-' and len(values['-harmonica1-']) and values['-harmonica1-'][-1] not in '0123456789':
            window['-harmonica1-'].update(values['-harmonica1-'][:-1])

        elif event == '-harmonica2-' and len(values['-harmonica2-']) and values['-harmonica2-'][-1] not in '0123456789':
            window['-harmonica2-'].update(values['-harmonica2-'][:-1])

        elif event == '-harmonica3-' and len(values['-harmonica3-']) and values['-harmonica3-'][-1] not in '0123456789':
            window['-harmonica3-'].update(values['-harmonica3-'][:-1])

        elif event == '-harmonica4-' and len(values['-harmonica4-']) and values['-harmonica4-'][-1] not in '0123456789':
            window['-harmonica4-'].update(values['-harmonica4-'][:-1])

        elif event == '-harmonica5-' and len(values['-harmonica5-']) and values['-harmonica5-'][-1] not in '0123456789':
            window['-harmonica5-'].update(values['-harmonica5-'][:-1])

        elif event == '-amplitude-' and len(values['-amplitude-']) and values['-amplitude-'][-1] not in '0123456789':
            window['-amplitude-'].update(values['-amplitude-'][:-1])

# close the window.
main()
window.close()