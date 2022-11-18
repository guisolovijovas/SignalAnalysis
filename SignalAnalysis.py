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

# NOME DOS INTEGRANTES DO GRUPO

# GUILHERME SOARES SOLOVIJOVAS PC3005933
# SERGIO MIGUEL VIANA LOPES
# RODRIGO MARCEL
# JOAO VICTOR PEDRO

# ESTA FUNCÃO GARANTE QUE O GRAFICO NAO FIQUE BORRADO


def make_dpi_aware():
    import ctypes
    import platform
    if int(platform.release()) >= 8:
        ctypes.windll.shcore.SetProcessDpiAwareness(True)


make_dpi_aware()  # CHAMA A FUNCÃO

# FUNCÃO QUE FAZ COM QUE OS GRAFICOS SEJAM DESENHADOS NA INTERFACE GRÁFICA


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

# FUNCÃO QUE ACHA O INDEX DE UMA LISTA ONDE VALOR DO TEMPO É IGUAL AO PERIODO


def find_index(t, periodo):
    for i in range(len(t)):
        if math.isclose(t[i], periodo, abs_tol=0.00004):
            return i

# FUNCÃO QUE LIMPA OS GRÁFICOS E OS CAMPOS DE EXIBICÃO DOS DADOS/MILTILINES, ALEM DE ZERAR VARIAVEIS


def clean_graphs():
    ax1.cla()
    ax2.cla()
    ax3.cla()
    ax4.cla()
    window['-ML1-'].update('')
    window['-ML2-'].update('')
    t_global = ''
    s_global = ''
    frequencias_global = ''
    amplitudes_global = ''

# FUNCÃO QUE DESENHA OS GRÁFICOS E SUAS CARACTERISTICAS


def draw_graphs():
    ax1.grid(True)
    ax2.grid(True)
    ax3.grid(True)
    ax4.grid(True)
    ax1.set_ylabel('Tensão(Vrms)')
    ax1.set_xlabel('Tempo (s)')
    ax2.set_ylabel('Tensão(Vrms)')
    ax2.set_xlabel('Frequência (Hz)')
    ax3.set_ylabel('Corrente(A)')
    ax3.set_xlabel('Tempo (s)')
    ax4.set_ylabel('Corrente(A)')
    ax4.set_xlabel('Frequência (Hz)')
    draw_figure_w_toolbar(window['-CANVAS-'].TKCanvas,
                          fig, window['controls_cv'].TKCanvas)
    draw_figure_w_toolbar(window['-CANVAS2-'].TKCanvas,
                          fig2, window['controls_cv2'].TKCanvas)

# ESTA CLASSE GERA A BARRA DE FERRAMENTAS PARA INTERACAO COM OS GRAFICOS (ZOOM E MOVIMENTAR)


class Toolbar(NavigationToolbar2Tk):
    def __init__(self, *args, **kwargs):
        super(Toolbar, self).__init__(*args, **kwargs)

# FUNCAO QUE VERIFICA E VALIDA OS DADOS QUE O USUARIO INSERE NOS CAMPOS, PARA EVITAR COLOCAR AMPLITUDE ZERO OU DEIXAR CAMPO VAZIO


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

# FUNCÃO RESPONSAVEL POR LER QUAIS CAMPOS FORAM IDENTIFICADOS COM ERRO NA FUNCÃO ANTERIOR


def generate_error_message(values_invalid):
    error_message = ''
    for value_invalid in values_invalid:
        error_message += ('\nCampo ** {} ** vazio ou nulo'.format(value_invalid))

    return error_message

# FUNCÃO QUE FAZ A SOMA DOS QUADRADOS DE N NUMEROS/LISTA


def sum_of_squares(lst):
    sum = 0
    for x in lst:
        sum = sum + x ** 2
    return sum


# AQUI É ONDE O CODIGO LÊ A RESOLUCAO DA TELA DO USUARIO
user32 = ctypes.windll.user32
screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

# ESCOLHA DO TEMA/COR DA INTERFACE
sg.theme('BrownBlue')

# ESTRUTURA DOS INPUTS DO USUARIO(BOTOES, CAMPOS DE TEXTO)
entradas = [[sg.Text('Análise de Sinais')],
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

# LAYOUT DAS TABS
layout_tab1 = [[sg.Canvas(key='controls_cv', expand_x=True, expand_y=True)], [sg.Canvas(key='-CANVAS-', expand_x=True, expand_y=True)],
               [sg.Button('Importar', expand_x=True, expand_y=True, button_color=('white', 'black')), sg.Button('Exportar', expand_x=True, expand_y=True, button_color=('white', 'black')),
                sg.Button('Exportar FFT', expand_x=True, expand_y=True, button_color=('white', 'black'))], [sg.Multiline(size=(10, 25), key='-ML1-', expand_x=True, expand_y=True)]]

layout_tab2 = [[sg.Canvas(key='controls_cv2', expand_x=True, expand_y=True)], [sg.Canvas(key='-CANVAS2-', expand_x=True, expand_y=True)],
               [sg.Multiline(size=(10, 25), key='-ML2-', expand_x=True, expand_y=True)]]

# AGRUPAMENTO DAS TABS
layout_tabgroup = [[sg.Tab('Gráfico Tensão', layout_tab1)], [
    sg.Tab('Gráfico Corrente', layout_tab2)]]

layout_frame = [[sg.TabGroup(layout_tabgroup)]]

menu_def = [['&Ajuda', '&Sobre...'], ]

# AQUI É ONDE TODOS OS ELEMENTOS QUE FORMAM A ESTRUTURA SE AGRUPAM PARA SER GERADO A INTERFACE GRAFICA
layout = [[sg.Menu(menu_def)], [sg.Column(entradas,  vertical_alignment='top'),
                                sg.VSeperator(), sg.Column(layout_frame)]]

# AQUI SE CRIA A JANELA
window = sg.Window('CRIADOR E ANALISADOR DE SINAIS', layout, size=(screensize), finalize=True,
                   element_justification='left', font='Monospace 10', resizable=True, icon=r'Logo.ico')
window.Maximize()  # ABRE A JANELA MAXIMIZADA

# OBTEM O ASPECT RATIO  DA RESOLUCÃO DO USUARIO
aspect_ratio = screensize[0]/screensize[1]
# SE O ASPECT RATIO FOR 16:9 ELE USA UM PARAMETRO ESPECIFICO DO TAMANHO DO GRÁFICO
if (math.isclose(aspect_ratio, 1.77, abs_tol=0.01)):
    figsize_x = screensize[0]/116.3
    figsize_y = figsize_x*0.34

# SE O ASPECT RATIO FOR 5:4 ELE USA UM PARAMETRO ESPECIFICO DO TAMANHO DO GRÁFICO
elif (screensize[0]/screensize[1] == 1.25):
    figsize_x = screensize[0]/116.3
    figsize_y = figsize_x*0.4545

# VARIAVEIS PARA ATRIBUIR OS PLOTS DOS GRAFICOS
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(figsize_x, figsize_y))
fig2, (ax3, ax4) = plt.subplots(1, 2, figsize=(figsize_x, figsize_y))

# VARIAVEIS GLOBAIS
t_global, s_global, file_global, s_import_array, t_import_array, frequencias_global, amplitudes_global = '', '', '', '', '', '', ''
num_pontos, ponto_parada = 20000, 1
carga = 50
offset = 0
sample_rate = num_pontos/ponto_parada

draw_graphs()

# LOOP DE EVENTO
# FUNCÃO PRINCIPAL


def main():
    while True:
        event, values = window.read()

        if event in (None, "Cancel"):
            break

        elif event == "Plotar gráfico":  # SE O USUARIO APERTAR "PLOTAR GRAFICO" ESTE CODIGO A SEGUIR É EXECUTADO
            # INICIA CONTADOR DE TEMPO (USEI PARA MEDIR TEMPO DE EXECUCÃO DO CODIGO)
            start_counter_ns = time.perf_counter_ns()
            clean_graphs()  # CHAMO A FUNCAO DE LIMPAR GRAFICOS
            draw_graphs()  # CHAMO A FUNCAO DE DESENHAR OS GRAFICOS
            # RECEBE O STATUS DE VALIDACÃO DOS INPUTS
            validation_result = validate(values)
            # SE TODOS OS CAMPOS DE INPUT'S DO USUARIO FOREM VALIDADOS O CODIGO PROSSEGUE
            if validation_result[0]:
                # ATRIBUI OS VALORES DIGITADO NOS CAMPOS A ESTAS VARIAVES ABAIXO, SENDO (HA) ABREVIACÃO DE HARMONICA E A1 (AMPLITUDE)
                ha1, ha2, ha3, ha4, ha5 = int(values['-harmonica1-']), int(values['-harmonica2-']), int(
                    values['-harmonica3-']), int(values['-harmonica4-']), int(values['-harmonica5-'])
                a1 = int(values['-amplitude-'])
                a2 = random.uniform(1, a1/2)
                a3 = random.uniform(1, a2/2)
                a4 = random.uniform(1, a3/2)
                a5 = random.uniform(1, a4/2)

                # PONTOS QUE REPRESENTAM o TEMPO
                t = np.linspace(0, ponto_parada, num_pontos, dtype=float)

                # PONTOS QUE REPRESENTAM O SINAL/AMPLITUDE DA TENSAO
                s = offset + a1*np.sin(ha1*2*np.pi*t)+a2*np.sin(ha2*2*np.pi*t)+a3*np.sin(
                    ha3*2*np.pi*t)+a4*np.sin(ha4*2*np.pi*t)+a5*np.sin(ha5*2*np.pi*t)  # PONTOS QUE REPRESENTAM A AMPLITUDE DO SINAL EM FUNCÃO DO TEMPO

                # PONTOS QUE REPRESENTAM AMPLITUDE DA CORRENTE DADA DETERMINADA CARGA EM OHMS
                corrente = s/carga

                fft, fft2 = np.fft.fft(s), np.fft.fft(corrente)
                T = t[1]-t[0]
                N, N2 = s.size, corrente.size
                f, f2 = np.fft.fftfreq(
                    len(s), T), np.fft.fftfreq(len(corrente), T)
                frequencias, frequencias2 = f[:N // 2], f2[:N2 // 2]
                amplitudes, amplitudes2 = np.abs(
                    fft)[:N // 2] * 1 / N, np.abs(fft2)[:N2 // 2] * 1 / N2
                t_global = t
                s_global = s
                frequencias_global = frequencias
                amplitudes_global = amplitudes

                # OBTEM VALORES DE PICO  DA FFT DO SINAL DA TENSAO
                peaks, _ = find_peaks(amplitudes)

                # OBTEM VALORES DE PICO DO SINAL DA TENSAO
                peaks2, _ = find_peaks(s)

                # OBTEM VALORES DE PICO DA FFT DA CORRENTE
                peaks3, _ = find_peaks(amplitudes2)

                # OBTEM VALORES DE PICO DO SINAL DA CORRENTE
                peaks4, _ = find_peaks(corrente)

                # LISTAS QUE VÃO RECEBER OS VALORES DE PICO
                harm_freq_list, harm_ampli_list, sinal_ampli_list, sinal_ampli_list2, corrente_freq_list, corrente_ampli_list = [], [], [], [], [], []

                # TODOS ESSES 'FOR' ESTAO ATRIBUNDO OS VALORES DE PICOS NAS LISTAS
                for i in range(len(peaks)):
                    harm_freq_list.append(ceil(frequencias[peaks[i]]))
                    harm_ampli_list.append(amplitudes[peaks[i]])

                for i in range(len(peaks2)):
                    sinal_ampli_list.append(s[peaks2[i]])

                for i in range(len(peaks3)):
                    corrente_freq_list.append(ceil(frequencias2[peaks3[i]]))
                    corrente_ampli_list.append(amplitudes2[peaks3[i]])

                for i in range(len(peaks4)):
                    sinal_ampli_list2.append(corrente[peaks4[i]])

                # GCD DENOMINATOR USA UMA FUNCAO DA BIBLIOTECA MATH PARA DESCOBRIR O MAIOR DIVISOR COMUM DE UMA DADA LISTA
                # E É USADO NO METODO DE OBTENCÃO DO PERIODO
                gcd_denominator = math.gcd(*harm_freq_list)
                gcd_denominator_corrente = math.gcd(*corrente_freq_list)

                # VALORES DOS PERIODOS, O PRIMEIRO É DA TENSÃO E  SEGUNDO DA CORRENTE
                periodo = 1/gcd_denominator
                periodo2 = 1/gcd_denominator_corrente

                # ESTA VARIAVEL T_INDEX NADA MAIS É DO QUE A CORDENADA X,Y NO EIXO DO TEMPO DO PERIODO
                # PORTANTO USAMOS A FUNCÃO FIND_PEAKS PARA ACHAR ESSA CORDENADA ONDE T == PERIODO
                t_index = find_index(t, periodo)  # TENSÃO
                t_index2 = find_index(t, periodo2)  # CORRENTE

                # T_INDEX_HALF EH O PONTO MEDIO DO PERIODO E ELE É NECESSARIO PARA CALCULAR A INTEGRAL
                t_index_half = int(t_index//2)
                t_index_half2 = int(t_index2//2)

                # SUM_ALL É A SOMA DOS QUADRADOS DE TODAS AS AMPLITUDE, TEMOS ESSA SOMAS TANTO PARA A TENSAO QUANTO PARA A CORRENTE
                sum_all = sum_of_squares(harm_ampli_list)
                sum_all2 = sum_of_squares(corrente_ampli_list)

                # SUM_ALL_SINAL 1,2 É A SOMA DOS QUADRADOS DOS VALORES DE AMPLITUDE DA TENSÃO E CORRENTE INDO DE 0 A METADE DO PERIODO
                sum_all_sinal = sum_of_squares(s[0:t_index_half])
                sum_all_sinal2 = sum_of_squares(corrente[0:t_index_half2])

                # VARIAVEIS QUE RECEBEM O MAIOR VALOR DA FREQUENCIA E DA AMPLITUDE USANDO O GRAFICO DA FFT
                max_freq, max_ampli = max(harm_freq_list), max(harm_ampli_list)
                max_freq_corrente, max_ampli_corrente = max(
                    corrente_freq_list), max(corrente_ampli_list)

                # AQUI TEMOS AS EQUACOES DE THD,TDD
                THD = (sqrt((sum_all-(max_ampli**2))/max_ampli**2))*100
                TDD = (sqrt((sum_all-(max_ampli**2)) /
                       max(sinal_ampli_list)**2))*100
                THD2 = (sqrt((sum_all2-(max_ampli_corrente**2)) /
                        max_ampli_corrente**2))*100
                TDD2 = (sqrt((sum_all2-(max_ampli_corrente**2)) /
                        max(sinal_ampli_list2)**2))*100

                # CÁLCULO DAS INTEGRAIS
                integral = (intg.trapz(t[0:t_index_half]), s[0: t_index_half])
                integral2 = (intg.trapz(
                    t[0:t_index_half2]), corrente[0: t_index_half2])

                # VALORES MÉDIO
                valor_medio = periodo * integral[0]
                valor_medio2 = periodo2 * integral2[0]

                # VALOR EFICAZ
                tensao_rms = sqrt(sum_all_sinal/len(t[0:t_index_half]))
                corrente_rms = sqrt(sum_all_sinal2/len(t[0:t_index_half2]))

                # ESSA PARTE PLOTA OS GRÁFICOS COM OS PONTOS GERADOS ANTERIORMENTE
                grafico1 = ax1.plot(t, s)
                grafico2 = ax2.plot(frequencias, amplitudes)
                grafico3 = ax3.plot(t, corrente)
                grafico4 = ax4.plot(frequencias2, amplitudes2)

                # LINHAS QUE MOSTRAM NO GRÁFICO VALOR DE PICO E VALOR EFICAZ
                linha_tensao_rms = ax1.axhline(
                    y=tensao_rms, color='r', linestyle='dashed', label='Valor Eficaz da Tensão')
                linha_valor_pico = ax1.axhline(
                    y=max(sinal_ampli_list), color='b', linestyle='dashed', label='Valor de Pico')
                linha_tensao_rms2 = ax3.axhline(
                    y=corrente_rms, color='r', linestyle='dashed', label='Valor Eficaz da Corrente')
                linha_valor_pico = ax3.axhline(
                    y=max(sinal_ampli_list2), color='b', linestyle='dashed', label='Valor de Pico')

                # GERA AS LEGENDAS E DEFINE DE ONDE ATÉ ONDE O GRÁFICO SERA DESENHADO
                ax1.legend()
                ax3.legend()
                ax1.set_xlim([0, periodo])
                ax2.set_ylim([0, max_ampli+(max_ampli*0.1)])
                ax2.set_xlim([0, max_freq+(max_freq*0.1)])
                ax3.set_xlim([0, periodo2])
                ax4.set_ylim([0, max_ampli_corrente+(max_ampli_corrente*0.1)])
                ax4.set_xlim([0, max_freq_corrente+(max_freq_corrente*0.1)])

                # TODA ESSA PARTE PARA BAIXO ESTÁ DESTINADA A ESCREVER NO CAMPO DE TEXTO (MULTILINE) OS VALORES OBTIDOS NOS CÁLCULOS
                window['-ML1-'].print('THD é: {:0.1f}%'.format(THD))
                window['-ML1-'].print('TDD é: {:0.1f}%'.format(TDD))
                for i in range(len(harm_freq_list)) and range(len(harm_ampli_list)):
                    window['-ML1-'].print('Harmônica {}: {}Hz, Amplitude={:.2f}'.format(
                        i+1, ceil(harm_freq_list[i]), harm_ampli_list[i]))
                window['-ML1-'].print(
                    'Valor Médio: {:0.7f}'.format(valor_medio))
                window['-ML1-'].print(
                    'Valor Eficaz da Tensão: {:0.1f}'.format(tensao_rms))
                window['-ML1-'].print(
                    'Valor de Pico: {:0.1f}'.format(max(sinal_ampli_list)))
                window['-ML1-'].print(
                    'Período: {:0.3f}'.format(periodo))
                end_counter_ns = time.perf_counter_ns()
                timer_ns = end_counter_ns - start_counter_ns
                window['-ML1-'].print(
                    'Tempo de execução:', timer_ns/10**9)
                window['-ML1-'].print('Taxa de amostagem {}Hz'.format(int(sample_rate)))

                window['-ML2-'].print('THD é: {:0.1f}%'.format(THD2))
                window['-ML2-'].print('TDD é: {:0.1f}%'.format(TDD2))
                for i in range(len(corrente_freq_list)) and range(len(corrente_ampli_list)):
                    window['-ML2-'].print('Harmônica {}: {}Hz, Amplitude={:.2f}'.format(
                        i+1, ceil(corrente_freq_list[i]), corrente_ampli_list[i]))
                window['-ML2-'].print(
                    'Valor Médio: {:0.7f}'.format(valor_medio2))
                window['-ML2-'].print(
                    'Valor Eficaz da Corrente: {:0.1f}'.format(corrente_rms))
                window['-ML2-'].print(
                    'Valor de Pico: {:0.1f}'.format(max(sinal_ampli_list2)))
                window['-ML2-'].print(
                    'Período: {:0.3f}'.format(periodo2))
                end_counter_ns = time.perf_counter_ns()
                timer_ns = end_counter_ns - start_counter_ns
                window['-ML2-'].print(
                    'Tempo de execução:', timer_ns/10**9)
                window['-ML2-'].print('Taxa de amostagem {}Hz'.format(int(sample_rate)))

            else:
                # ESSE TRECHO É RESPONSAVEL POR MOSTRAR AO USUARIO UM POPUP COM CAMPOS QUE ELE NAO PREENCHEU OU COLOCOU VALOR NULO
                error_message = generate_error_message(validation_result[1])
                sg.popup('Campo incompleto ou nulo!',
                         error_message, title='Erro')

        elif event == 'Importar':
            filename = sg.popup_get_file('Will not see this message', no_window=True, multiple_files=False,
                                         file_types=(('.txt', '*.txt*'),), )
            clean_graphs()
            draw_graphs()

            # SE O USUÁRIO ABRIR O FILE DIALOG E NÃO SELECIONAR UM ARQUIVO PARA ABRIR (OU SEJA ) FILENAME == '' CHAMA A FUNCÃO MAIN() PARA EVITAR
            # FECHAMENTO DA TELA.
            if filename == '':
                main()

            # SE FOR ESCOLHIDO UM ARQUIVO ESSE ELSE PROSSEGUE
            else:
                start_counter_ns = time.perf_counter_ns()
                # ESSE PRIMEIRO WITH TEM COMO OBJETIVO LER QUANTAS LINHAS TEM O .TXT UTILIZAMOS ISSO PARA LER ARQUIVOS .TXT DE QUALQUER NÚMERO
                # DE PONTOS.
                with open(filename, 'r') as fp:
                    num_lines = sum(1 for line in fp)
                    # print('Total lines:', num_lines)

                # ESSE WITH BASICAMENTE LÊ TODAS AS LINHAS ATÉ A METADE E ATRIBUI ESSES VALORES PARA UMA LISTA NESTE CASO (T_IMPORT)
                with open(filename, 'r') as myfile:
                    linhas_t = myfile.readlines()[0:int(num_lines/2)]
                    t_import = []
                    for sub in linhas_t:
                        t_import.append(sub.replace("\n", ""))

                # TRANSFORMA A LISTA T_IMPORT EM UM ARRAY DA BIBLIOTECA NUMPY
                t_import_array = np.array(t_import)
                # ATRIBUI O ARRAY A VARIAVEL T E CONVERTE O ARRAY PARA O TIPO FLOAT
                t = np.asarray(t_import_array, dtype=float)

                # ESSE WITH BASICAMENTE LÊ TODAS AS LINHAS ATÉ A METADE E ATRIBUI ESSES VALORES PARA UMA LISTA NESTE CASO (S_IMPORT)
                with open(filename, 'r') as myfile:
                    linhas_s = myfile.readlines()[int(num_lines/2):num_lines]
                    s_import = []
                    for sub in linhas_s:
                        s_import.append(sub.replace("\n", ""))

                # TRANSFORMA A LISTA S_IMPORT EM UM ARRAY DA BIBLIOTECA NUMPY
                s_import_array = np.array(s_import)
                # ATRIBUI O ARRAY A VARIAVEL S E CONVERTE O ARRAY PARA O TIPO FLOAT
                s = np.asarray(s_import_array, dtype=float)

                # SAMPLE RATE É UMA VARIAVEL QUE CALCULA A AMOSTRAGEM DO GRÁFICO IMPORTADO ATRAVEZ DO SEM TAMANHO E DE ONDE PARTIU E ONDE CHEGOU
                sample_rate_local = len(t)/(max(t)-min(t))

                # PONTOS QUE REPRESENTAM AMPLITUDE DA CORRENTE DADA DETERMINADA CARGA EM OHMS
                corrente = s/carga
                fft, fft2 = np.fft.fft(s), np.fft.fft(corrente)
                T = t[1] - t[0]
                N, N2 = s.size, corrente.size
                f, f2 = np.fft.fftfreq(
                    len(s), T), np.fft.fftfreq(len(corrente), T)
                frequencias, frequencias2 = f[:N // 2], f2[:N2 // 2]
                amplitudes, amplitudes2 = np.abs(
                    fft)[:N // 2] * 1 / N, np.abs(fft2)[:N2 // 2] * 1 / N2
                t_global = t
                s_global = s

                # OBTEM VALORES DE PICO  DA FFT DO SINAL DA TENSAO
                peaks, _ = find_peaks(amplitudes)

                # OBTEM VALORES DE PICO DO SINAL DA TENSAO
                peaks2, _ = find_peaks(s)

                # OBTEM VALORES DE PICO DA FFT DA CORRENTE
                peaks3, _ = find_peaks(amplitudes2)

                # OBTEM VALORES DE PICO DO SINAL DA CORRENTE
                peaks4, _ = find_peaks(corrente)

                # LISTAS QUE VÃO RECEBER OS VALORES DE PICO
                harm_freq_list, harm_ampli_list, sinal_ampli_list, sinal_ampli_list2, corrente_freq_list, corrente_ampli_list = [], [], [], [], [], []

                # TODOS ESSES 'FOR' ESTAO ATRIBUNDO OS VALORES DE PICOS NAS LISTAS
                for i in range(len(peaks)):
                    harm_freq_list.append(ceil(frequencias[peaks[i]]))
                    harm_ampli_list.append(amplitudes[peaks[i]])

                for i in range(len(peaks2)):
                    sinal_ampli_list.append(s[peaks2[i]])

                for i in range(len(peaks3)):
                    corrente_freq_list.append(ceil(frequencias2[peaks3[i]]))
                    corrente_ampli_list.append(amplitudes2[peaks3[i]])

                for i in range(len(peaks4)):
                    sinal_ampli_list2.append(corrente[peaks4[i]])

                # GCD DENOMINATOR USA UMA FUNCAO DA BIBLIOTECA MATH PARA DESCOBRIR O MAIOR DIVISOR COMUM DE UMA DADA LISTA
                # E É USADO NO METODO DE OBTENCÃO DO PERIODO
                gcd_denominator = math.gcd(*harm_freq_list)
                gcd_denominator_corrente = math.gcd(*corrente_freq_list)

                # VALORES DOS PERIODOS, O PRIMEIRO É DA TENSÃO E  SEGUNDO DA CORRENTE
                periodo = 1/gcd_denominator
                periodo2 = 1/gcd_denominator_corrente

                # ESTA VARIAVEL T_INDEX NADA MAIS É DO QUE A CORDENADA X,Y NO EIXO DO TEMPO DO PERIODO
                # PORTANTO USAMOS A FUNCÃO FIND_PEAKS PARA ACHAR ESSA CORDENADA ONDE T == PERIODO
                t_index = find_index(t, periodo)
                t_index2 = find_index(t, periodo2)

                # T_INDEX_HALF EH O PONTO MEDIO DO PERIODO E ELE É NECESSARIO PARA CALCULAR A INTEGRAL
                t_index_half = int(t_index//2)
                t_index_half2 = int(t_index2//2)

                # SUM_ALL É A SOMA DOS QUADRADOS DE TODAS AS AMPLITUDE, TEMOS ESSA SOMAS TANTO PARA A TENSAO QUANTO PARA A CORRENTE
                sum_all = sum_of_squares(harm_ampli_list)
                sum_all2 = sum_of_squares(corrente_ampli_list)

                # SUM_ALL_SINAL 1,2 É A SOMA DOS QUADRADOS DOS VALORES DE AMPLITUDE DA TENSÃO E CORRENTE INDO DE 0 A METADE DO PERIODO
                sum_all_sinal = sum_of_squares(
                    s[0:t_index_half])
                sum_all_sinal2 = sum_of_squares(corrente[0:t_index_half2])

                # VARIAVEIS QUE RECEBEM O MAIOR VALOR DA FREQUENCIA E DA AMPLITUDE USANDO O GRAFICO DA FFT
                max_freq, max_ampli = max(harm_freq_list), max(harm_ampli_list)
                max_freq_corrente, max_ampli_corrente = max(
                    corrente_freq_list), max(corrente_ampli_list)

                # AQUI TEMOS AS EQUACOES DE THD,TDD
                THD = (sqrt((sum_all-(max_ampli**2))/max_ampli**2))*100
                TDD = (sqrt((sum_all-(max_ampli**2)) /
                       max(sinal_ampli_list)**2))*100
                THD2 = (sqrt((sum_all2-(max_ampli_corrente**2)) /
                        max_ampli_corrente**2))*100
                TDD2 = (sqrt((sum_all2-(max_ampli_corrente**2)) /
                        max(sinal_ampli_list2)**2))*100

                # CÁLCULO DAS INTEGRAIS
                integral = (intg.trapz(
                    t[0:t_index_half]), s[0: t_index_half])
                integral2 = (intg.trapz(
                    t[0:t_index_half2]), corrente[0: t_index_half2])

                # VALORES MÉDIO
                valor_medio = periodo * integral[0]
                valor_medio2 = periodo2 * integral2[0]

                # VALOR EFICAZ
                tensao_rms = sqrt(
                    sum_all_sinal/len(t[0:t_index_half]))
                corrente_rms = sqrt(
                    sum_all_sinal2/len(t[0:t_index_half2]))

                # ESSA PARTE PLOTA OS GRÁFICOS COM OS PONTOS GERADOS ANTERIORMENTE
                grafico1 = ax1.plot(t, s)
                grafico2 = ax2.plot(frequencias, amplitudes)
                grafico3 = ax3.plot(t, corrente)
                grafico4 = ax4.plot(frequencias2, amplitudes2)

                # LINHAS QUE MOSTRAM NO GRÁFICO VALOR DE PICO E VALOR EFICAZ
                linha_tensao_rms = ax1.axhline(
                    y=tensao_rms, color='r', linestyle='dashed', label='Valor Eficaz da Tensão')
                linha_valor_pico = ax1.axhline(
                    y=max(sinal_ampli_list), color='b', linestyle='dashed', label='Valor de Pico')
                linha_tensao_rms2 = ax3.axhline(
                    y=corrente_rms, color='r', linestyle='dashed', label='Valor Eficaz da Corrente')
                linha_valor_pico = ax3.axhline(
                    y=max(sinal_ampli_list2), color='b', linestyle='dashed', label='Valor de Pico')

                # GERA AS LEGENDAS E DEFINE DE ONDE ATÉ ONDE O GRÁFICO SERA DESENHADO
                ax1.legend()
                ax3.legend()
                ax1.set_xlim([0, periodo])
                ax2.set_ylim([0, max_ampli+(max_ampli*0.1)])
                ax2.set_xlim([0, max_freq+(max_freq*0.1)])
                ax3.set_xlim([0, periodo2])
                ax4.set_ylim([0, max_ampli_corrente+(max_ampli_corrente*0.1)])
                ax4.set_xlim([0, max_freq_corrente+(max_freq_corrente*0.1)])

                # TODA ESSA PARTE PARA BAIXO ESTÁ DESTINADA A ESCREVER NO CAMPO DE TEXTO (MULTILINE) OS VALORES OBTIDOS NOS CÁLCULOS
                window['-ML1-'].print('THD é: {:0.1f}%'.format(THD))
                window['-ML1-'].print('TDD é: {:0.1f}%'.format(TDD))
                for i in range(len(harm_freq_list)) and range(len(harm_ampli_list)):
                    window['-ML1-'].print('Harmônica {}: {}Hz, A={:.2f}'.format(
                        i+1, ceil(harm_freq_list[i]), harm_ampli_list[i]))
                window['-ML1-'].print(
                    'Valor Médio: {:0.7f}'.format(valor_medio))
                window['-ML1-'].print(
                    'Tensao RMS: {:0.1f}'.format(tensao_rms))
                window['-ML1-'].print(
                    'Valor de Pico: {:0.1f}'.format(max(sinal_ampli_list)))
                window['-ML1-'].print(
                    'Período: {:0.3f}'.format(periodo))
                end_counter_ns = time.perf_counter_ns()
                timer_ns = end_counter_ns - start_counter_ns
                window['-ML1-'].print(
                    'Tempo de execução:', timer_ns/10**9)
                window['-ML1-'].print(
                    'Taxa de amostagem {}Hz'.format(int(sample_rate_local)))

                window['-ML2-'].print('THD é: {:0.1f}%'.format(THD2))
                window['-ML2-'].print('TDD é: {:0.1f}%'.format(TDD2))
                for i in range(len(corrente_freq_list)) and range(len(corrente_ampli_list)):
                    window['-ML2-'].print('Harmônica {}: {}Hz, Amplitude={:.2f}'.format(
                        i+1, ceil(corrente_freq_list[i]), corrente_ampli_list[i]))
                window['-ML2-'].print(
                    'Valor Médio: {:0.7f}'.format(valor_medio2))
                window['-ML2-'].print(
                    'Valor Eficaz da Corrente: {:0.1f}'.format(corrente_rms))
                window['-ML2-'].print(
                    'Valor de Pico: {:0.1f}'.format(max(sinal_ampli_list2)))
                window['-ML2-'].print(
                    'Período: {:0.3f}'.format(periodo2))
                end_counter_ns = time.perf_counter_ns()
                timer_ns = end_counter_ns - start_counter_ns
                window['-ML2-'].print(
                    'Tempo de execução:', timer_ns/10**9)
                window['-ML2-'].print(
                    'Taxa de amostagem {}Hz'.format(int(sample_rate_local)))

        elif event == 'Exportar':
            # FILENAME É A VARIÁVEL QUE RECEBE O NOME DO ARQUIVO ESCOLHIDO PELO USUARIO NA HORA DE SALVAR O ARQUIVO
            filename = sg.tk.filedialog.asksaveasfile(defaultextension='txt')
            # AQUI ELE CHECA SE FOI ESCOLHIDO ALGUM ARQUIVO EXISTENTE
            if filename == None:
                main()

            else:
                # ESCREVE TODOS OS PONTOS DE T E LOGO EM SEGUIDA OS DE S
                with open(filename.name, "w") as f:
                    f.write('\n'.join(map(str, t_global)))
                    f.write('\n')
                    f.write('\n'.join(map(str, s_global)))
                    f.close()

        elif event == 'Exportar FFT':
            # AO PRESSIONAR ESTE BOTÃO ELE EXPORTA A TABELA DE PONTOS DO GRÁFICO DA FFT PARA UM TXT
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
            # SEMPRE QUE PRESSIONADO O BOTÃO LIMPAR VAI SER LIMPO OS GRÁFICOS AS VARIAVEIS GLOBAIS E EM SEGUIDA VAI SER DESENHADO GRÁFICOS LIMPOS
            # SEM NENHUMA LINHA PLOTADA
            clean_graphs()
            draw_graphs()

        elif event == 'Sobre...':
            sg.popup('Sobre esse programa:\nEsse software tem como intúito conseguir criar um sinal puro ou ruídoso com base na soma de várias senóides, além de analisar e devolver valores de THD(Total Harmonic Distortion),TDD(Total Demand Distortion),Valor Médio,Valor Eficaz,Valor de Pico e período do sinal.', 'Nome dos integrantes:\nGuilherme Soares Solovijovas\nSergio Miguel Viana Lopes\nRodrigo Marcel\nJoão Victor Pedro', 'Versão 1.0',
                     'Utiliza a versão {} do PySimpleGUI'.format(sg.version),  grab_anywhere=True, title='Sobre o Software')

        # TODO ESSES ELIF'S TEM O OBJETIVO DE IMPEDIR QUE O USUÁRIO INSIRA ALGUM CARACTER NAO DESEJADO NO CAMPO DE INPUT, COM A INTECÃO DE EVITAR
        # ERROS NO CÓDIGO, BASICAMENTE ELE LÊ O QUE FOI DIGITADO E SE NÃO FOR UM CARACTER DA LISTA DOS PERMITIDOS ELE APAGA
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

        elif event == '-carga-' and len(values['-carga-']) and values['-carga-'][-1] not in '0123456789':
            window['-carga-'].update(values['-carga-'][:-1])


# FECHA A JANLEA
main()
window.close()
