import numpy as np
import PySimpleGUI as sg
import matplotlib.pyplot as plt
import time
import ctypes
import math
import random
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from scipy.signal import find_peaks
from scipy import integrate as intg
from math import sqrt, ceil

# Functions to prevent GUI blurring


def make_dpi_aware():
    import ctypes
    import platform
    if int(platform.release()) >= 8:
        ctypes.windll.shcore.SetProcessDpiAwareness(True)


make_dpi_aware()


# Function for drawing


def draw_figure_w_toolbar(canvas, fig, canvas_toolbar):
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


def draw_figure_w_toolbar2(canvas2, fig2, canvas_toolbar2):
    if canvas2.children:
        for child in canvas2.winfo_children():
            child.destroy()
    if canvas_toolbar2.children:
        for child in canvas_toolbar2.winfo_children():
            child.destroy()
    figure_canvas_agg = FigureCanvasTkAgg(fig2, master=canvas2)
    figure_canvas_agg.draw()
    toolbar = Toolbar(figure_canvas_agg, canvas_toolbar2)
    toolbar.update()
    figure_canvas_agg.get_tk_widget().pack(side='right', fill='both', expand=1)

# funcao para achar indice onde t == periodo


def find_index(t, periodo):
    for i in range(len(t)):
        if math.isclose(t[i], periodo, abs_tol=0.00004):
            return i


# funcao para achar indice de uma lista
def find_index2(a_list, item_to_find):
    indices = []
    for idx, value in enumerate(a_list):
        if math.isclose(value, item_to_find, abs_tol=0.1):
            indices.append(idx)
    return indices


def LCMofArray(a):
    lcm = a[0]
    for i in range(1, len(a)):
        lcm = lcm*a[i]//math.gcd(lcm, a[i])
    return lcm


def clean_graphs():
    ax1.cla()
    ax2.cla()
    ax3.cla()
    ax4.cla()
    ax1.grid(True)
    ax2.grid(True)
    ax3.grid(True)
    ax4.grid(True)
    ax1.set_ylabel('Tensão(Vrms)')
    ax1.set_xlabel('Tempo (s)')
    ax2.set_ylabel('Tensão(Vrms)')
    ax2.set_xlabel('Frequência (Hz)')
    ax3.set_ylabel('Corrente')
    ax3.set_xlabel('Tempo (s)')
    ax4.set_ylabel('Corrente')
    ax4.set_xlabel('Frequência (Hz)')
    window['-ML1-'].update('')
    window['-ML2-'].update('')
    draw_figure_w_toolbar(window['-CANVAS-'].TKCanvas,
                          fig, window['controls_cv'].TKCanvas)
    draw_figure_w_toolbar2(
        window['-CANVAS2-'].TKCanvas, fig2, window['controls_cv2'].TKCanvas)
    t_global = ''
    s_global = ''
    frequencias_global = ''
    amplitudes_global = ''


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
        values_invalid.append('Tensão(Vrms)')
        is_valid = False

    elif int(values['-amplitude-']) == 0:
        values_invalid.append('Tensão(Vrms)')
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
            [sg.Push(), sg.T('Harmonica 1 (Hz):'), sg.Input(
                enable_events=True, key='-harmonica1-', size=(4, 1))],
            [sg.Push(), sg.T('Harmonica 2 (Hz):'), sg.Input(
                enable_events=True, key='-harmonica2-', size=(4, 1))],
            [sg.Push(), sg.T('Harmonica 3 (Hz):'), sg.Input(
                enable_events=True, key='-harmonica3-', size=(4, 1))],
            [sg.Push(), sg.T('Harmonica 4 (Hz):'), sg.Input(
                enable_events=True, key='-harmonica4-', size=(4, 1))],
            [sg.Push(), sg.T('Harmonica 5 (Hz):'), sg.Input(
                enable_events=True, key='-harmonica5-', size=(4, 1))],
            [sg.Push(), sg.T('Tensão:'), sg.Input(
                enable_events=True, key='-amplitude-', size=(4, 1))],
            [sg.Push(), sg.Button('Plotar gráfico', button_color=('white', 'springgreen4')), sg.Button('Limpar', button_color=('white', 'firebrick3'))]]
# Layout creation
layout_tab1 = [[sg.Canvas(key='controls_cv', expand_x=True, expand_y=True)], [sg.Canvas(key='-CANVAS-', expand_x=True, expand_y=True)],
               [sg.Button('Importar', expand_x=True, expand_y=True, button_color=('white', 'black')), sg.Button('Exportar', expand_x=True, expand_y=True, button_color=('white', 'black')),
                sg.Button('Exportar FFT', expand_x=True, expand_y=True, button_color=('white', 'black'))], [sg.Multiline(size=(10, 25), key='-ML1-', expand_x=True, expand_y=True, no_scrollbar=True)]]

layout_tab2 = [[sg.Canvas(key='controls_cv2', expand_x=True, expand_y=True)], [sg.Canvas(key='-CANVAS2-', expand_x=True, expand_y=True)],
               [sg.Multiline(size=(10, 25), key='-ML2-', expand_x=True, expand_y=True, no_scrollbar=True)]]

layout_tabgroup = [[sg.Tab('Gráfico Tensão', layout_tab1)], [
    sg.Tab('Gráfico Corrente', layout_tab2)]]

layout_frame = [[sg.TabGroup(layout_tabgroup)]]

layout = [[sg.Column(entradas,  vertical_alignment='top'),
           sg.VSeperator(), sg.Column(layout_frame)]]

# Create a window. finalize=Must be True.
window = sg.Window('ANALISE DE SINAIS', layout, size=(screensize), finalize=True,
                   element_justification='left', font='Monospace 10', resizable=True)
window.Maximize()
figsize_x = screensize[0]/116.3
figsize_y = figsize_x*0.4545
# Create a fig for embedding.
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(figsize_x, figsize_y))
fig2, (ax3, ax4) = plt.subplots(1, 2, figsize=(figsize_x, figsize_y))

# Associate fig with Canvas.
clean_graphs()

# Variaveis globais
t_global, s_global, file_global, s_import_array, t_import_array, frequencias_global, amplitudes_global = '', '', '', '', '', '', ''
num_pontos, ponto_parada = 20000, 1

# Event loop


def main():
    while True:
        event, values = window.read()

        if event in (None, "Cancel"):
            break

        elif event == "Plotar gráfico":
            start_counter_ns = time.perf_counter_ns()
            clean_graphs()
            validation_result = validate(values)
            if validation_result[0]:
                ha1, ha2, ha3, ha4, ha5 = int(values['-harmonica1-']), int(values['-harmonica2-']), int(
                    values['-harmonica3-']), int(values['-harmonica4-']), int(values['-harmonica5-'])
                a1 = int(values['-amplitude-'])
                a2 = random.uniform(1, a1/2)
                a3 = random.uniform(1, a2/2)
                a4 = random.uniform(1, a3/2)
                a5 = random.uniform(1, a4/2)
                sample_rate = num_pontos/ponto_parada
                offset = 0
                t = np.linspace(0, ponto_parada, num_pontos, dtype=float)
                s = offset + a1*np.sin(ha1*2*np.pi*t)+a2*np.sin(ha2*2*np.pi*t)+a3*np.sin(
                    ha3*2*np.pi*t)+a4*np.sin(ha4*2*np.pi*t)+a5*np.sin(ha5*2*np.pi*t)
                fft = np.fft.fft(s)
                T = t[1]-t[0]
                N = s.size
                f = np.fft.fftfreq(len(s), T)
                frequencias = f[:N // 2]
                amplitudes = np.abs(fft)[:N // 2] * 1 / N
                t_global = t
                s_global = s
                frequencias_global = frequencias
                amplitudes_global = amplitudes
                peaks, _ = find_peaks(amplitudes)
                peaks2, _ = find_peaks(s)
                harm_freq_list, harm_ampli_list, sinal_freq_list, sinal_ampli_list = [], [], [], []

                for i in range(len(peaks)):
                    harm_freq_list.append(ceil(frequencias[peaks[i]]))
                    harm_ampli_list.append(amplitudes[peaks[i]])

                for i in range(len(peaks2)):
                    sinal_freq_list.append(t[peaks2[i]])
                    sinal_ampli_list.append(s[peaks2[i]])

                gcd_denominator = math.gcd(*harm_freq_list)
                periodo = 1/gcd_denominator
                t_index = find_index(t, periodo)
                t_index_half = int(t_index//2)
                sum_all = sum_of_squares(harm_ampli_list)
                sum_all_sinal = sum_of_squares(s[0:t_index_half])
                max_freq, max_ampli = max(harm_freq_list), max(harm_ampli_list)
                THD = (sqrt((sum_all-(max_ampli**2))/max_ampli**2))*100
                TDD = (sqrt((sum_all-(max_ampli**2))/max_ampli**2))*100
                integral = (intg.trapz(t[0:t_index_half]), s[0: t_index_half])
                valor_medio = periodo * integral[0]
                tensao_rms = sqrt(sum_all_sinal/len(t[0:t_index_half]))
                grafico1 = ax1.plot(t, s)
                grafico2 = ax2.plot(frequencias, amplitudes)
                linha_tensao_rms = ax1.axhline(
                    y=tensao_rms, color='r', linestyle='dashed', label='Tensão RMS')
                linha_valor_pico = ax1.axhline(
                    y=max(sinal_ampli_list), color='b', linestyle='dashed', label='Valor de Pico')
                ax1.grid(True)
                ax2.grid(True)
                ax1.set_xlim([0, periodo])
                ax2.set_ylim([0, max_ampli+10])
                ax2.set_xlim([0, max_freq+10])
                ax1.legend()
                window['-ML1-'].print('THD é: {:0.1f}%'.format(THD))
                window['-ML1-'].print('TDD é: {:0.1f}%'.format(TDD))
                for i in range(len(harm_freq_list)) and range(len(harm_ampli_list)):
                    window['-ML1-'].print('Harmonica {}: {}Hz, Amplitude={:.2f}'.format(
                        i+1, ceil(harm_freq_list[i]), harm_ampli_list[i]))
                window['-ML1-'].print(
                    'Valor Médio: {:0.7f}'.format(valor_medio))
                window['-ML1-'].print(
                    'Tensao RMS: {:0.1f}'.format(tensao_rms))
                window['-ML1-'].print(
                    'Valor de Pico: {:0.1f}'.format(max(sinal_ampli_list)))
                window['-ML1-'].print(
                    'Periodo: {:0.3f}'.format(periodo))
                end_counter_ns = time.perf_counter_ns()
                timer_ns = end_counter_ns - start_counter_ns
                window['-ML1-'].print(
                    'Tempo de execução:', timer_ns/10**9)

            else:
                error_message = generate_error_message(validation_result[1])
                sg.popup('Campo incompleto ou nulo!', error_message)

        elif event == 'Importar':
            filename = sg.popup_get_file('Will not see this message', no_window=True, multiple_files=False,
                                         file_types=(('.txt', '*.txt*'),), )
            clean_graphs()
            if filename == '':
                main()

            else:
                start_counter_ns = time.perf_counter_ns()
                with open(filename, 'r') as fp:
                    num_lines = sum(1 for line in fp)
                    #print('Total lines:', num_lines)

                with open(filename, 'r') as myfile:
                    linhas_t = myfile.readlines()[0:int(num_lines/2)]
                    t_import = []
                    for sub in linhas_t:
                        t_import.append(sub.replace("\n", ""))

                t_import_array = np.array(t_import)
                t_import_array_float = np.asarray(t_import_array, dtype=float)
                with open(filename, 'r') as myfile:
                    linhas_s = myfile.readlines()[int(num_lines/2):num_lines]
                    s_import = []
                    for sub in linhas_s:
                        s_import.append(sub.replace("\n", ""))

                s_import_array = np.array(s_import)
                s_import_array_float = np.asarray(s_import_array, dtype=float)
                fft = np.fft.fft(s_import_array_float)
                T = t_import_array_float[1] - t_import_array_float[0]
                N = s_import_array_float.size
                f = np.fft.fftfreq(len(s_import_array_float), T)
                frequencias = f[:N // 2]
                amplitudes = np.abs(fft)[:N // 2] * 1 / N
                peaks, _ = find_peaks(amplitudes)
                peaks2, _ = find_peaks(s_import_array_float)
                harm_freq_list, harm_ampli_list, sinal_freq_list, sinal_ampli_list = [], [], [], []

                for i in range(len(peaks)):
                    harm_freq_list.append(ceil(frequencias[peaks[i]]))
                    harm_ampli_list.append(amplitudes[peaks[i]])

                for i in range(len(peaks2)):
                    sinal_freq_list.append(t_import_array_float[peaks2[i]])
                    sinal_ampli_list.append(s_import_array_float[peaks2[i]])

                gcd_denominator = math.gcd(*harm_freq_list)
                periodo = 1/gcd_denominator
                t_index = find_index(t_import_array_float, periodo)
                t_index_half = int(t_index//2)
                sum_all = sum_of_squares(harm_ampli_list)
                sum_all_sinal = sum_of_squares(
                    s_import_array_float[0:t_index_half])
                max_freq, max_ampli = max(harm_freq_list), max(harm_ampli_list)
                THD = (sqrt((sum_all-(max_ampli**2))/max_ampli**2))*100
                TDD = (sqrt((sum_all-(max_ampli**2))/max_ampli**2))*100
                integral = (intg.trapz(
                    t_import_array_float[0:t_index_half]), s_import_array_float[0: t_index_half])
                valor_medio = periodo * integral[0]
                tensao_rms = sqrt(
                    sum_all_sinal/len(t_import_array_float[0:t_index_half]))
                grafico1 = ax1.plot(t_import_array_float, s_import_array_float)
                grafico2 = ax2.plot(frequencias, amplitudes)
                linha_tensao_rms = ax1.axhline(
                    y=tensao_rms, color='r', linestyle='dashed', label='Tensão RMS')
                linha_valor_pico = ax1.axhline(
                    y=max(sinal_ampli_list), color='b', linestyle='dashed', label='Valor de Pico')
                ax1.grid(True)
                ax2.grid(True)
                ax1.set_xlim([0, periodo])
                ax2.set_ylim([0, max_ampli+10])
                ax2.set_xlim([0, max_freq+10])
                ax1.legend()
                window['-ML1-'].print('THD é: {:0.1f}%'.format(THD))
                window['-ML1-'].print('TDD é: {:0.1f}%'.format(TDD))
                for i in range(len(harm_freq_list)) and range(len(harm_ampli_list)):
                    window['-ML1-'].print('Harmonica {}: {}Hz, A={:.2f}'.format(
                        i+1, ceil(harm_freq_list[i]), harm_ampli_list[i]))
                window['-ML1-'].print(
                    'Valor Médio: {:0.7f}'.format(valor_medio))
                window['-ML1-'].print(
                    'Tensao RMS: {:0.1f}'.format(tensao_rms))
                window['-ML1-'].print(
                    'Valor de Pico: {:0.1f}'.format(max(sinal_ampli_list)))
                window['-ML1-'].print(
                    'Periodo: {:0.3f}'.format(periodo))
                end_counter_ns = time.perf_counter_ns()
                timer_ns = end_counter_ns - start_counter_ns
                window['-ML1-'].print(
                    'Tempo de execução:', timer_ns/10**9)

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
            clean_graphs()
            draw_figure_w_toolbar(
                window['-CANVAS-'].TKCanvas, fig, window['controls_cv'].TKCanvas)

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
