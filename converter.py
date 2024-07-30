import pandas as pd
import os
import sys
from datetime import datetime

def main():

    def read_existing_data(file_path):
        if not os.path.exists(file_path):
            return set()
        existing_data = set()
        with open(file_path, 'r') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) == 7:
                    symbol, date, _, _, _, _, _ = parts
                    existing_data.add((symbol, date))
        return existing_data

    # Obtener la ruta del directorio donde se encuentra el ejecutable
    if getattr(sys, 'frozen', False):
        script_dir = os.path.dirname(sys.executable)  # Directorio del ejecutable empaquetado
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))  # Directorio del script en desarrollo

    # Construir la ruta a la carpeta 'descargas' dentro del directorio donde se ejecuta el script/emulador
    input_dir = os.path.join(script_dir, 'descargas')

    # Ruta del archivo de salida 'historicos.txt' en el mismo directorio
    output_file = os.path.join(script_dir, 'historicos.txt')

    # Crear el directorio de salida si no existe
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Lista de archivos Excel en la carpeta 'descargas' que no tienen 'PROCESADO' en el nombre
    excel_files = [f for f in os.listdir(input_dir) if f.endswith('.xlsx') and 'PROCESADO' not in f]

    # Leer las fechas existentes en el archivo de salida
    existing_data = read_existing_data(output_file)

    # Obtener la fecha de hoy en el formato utilizado en el archivo (yyyymmdd)
    today_date = datetime.today().strftime('%Y%m%d')

    # Abrir el archivo de salida en modo append
    with open(output_file, 'a') as outfile:
        # Iterar sobre los archivos en la carpeta 'descargas'
        for filename in excel_files:
            # Extraer el nombre del símbolo del nombre del archivo sin la palabra "history"
            symbol = filename.split(' ')[1]  # Esto asume que el nombre del archivo es "history AAISA.xlsx"
            symbol = symbol.replace('.xlsx', '')  # Quitar la extensión .xlsx si es necesario
            input_path = os.path.join(input_dir, filename)
            
            # Leer el archivo Excel
            df = pd.read_excel(input_path, header=None)  # Lee el archivo Excel sin encabezados
            
            # Asumir que los datos empiezan desde la tercera fila y en las columnas A a F
            df_selected = df.iloc[3:, :6]
            df_selected.columns = ['Fecha', 'Open', 'High', 'Low', 'Close', 'Volume']
            
            # Filtrar las filas que no están en los datos existentes y no tienen la fecha de hoy
            new_rows = df_selected[~df_selected.apply(lambda row: 
                (symbol, datetime.strptime(row['Fecha'], '%d-%m-%Y').strftime('%Y%m%d')) in existing_data 
                or datetime.strptime(row['Fecha'], '%d-%m-%Y').strftime('%Y%m%d') == today_date, axis=1)]
            
            # Escribir los datos filtrados en el archivo de salida
            for _, row in new_rows.iterrows():
                formatted_date = datetime.strptime(row['Fecha'], '%d-%m-%Y').strftime('%Y%m%d')
                line = f"{symbol},{formatted_date},{row['Open']},{row['High']},{row['Low']},{row['Close']},{row['Volume']}\n"
                outfile.write(line)
                print(f"Datos agregados al archivo: {line.strip()}")
            
            # Renombrar el archivo procesado
            base_new_filename = filename.replace('.xlsx', '_PROCESADO.xlsx')
            new_filename = base_new_filename
            counter = 1
            while os.path.exists(os.path.join(input_dir, new_filename)):
                new_filename = base_new_filename.replace('_PROCESADO.xlsx', f'_PROCESADO_{counter}.xlsx')
                counter += 1
            new_path = os.path.join(input_dir, new_filename)
            os.rename(input_path, new_path)
            print(f"Archivo renombrado a: {new_filename}")

    print(f"Datos combinados guardados en: {output_file}")

    # Ordenar el archivo de salida por el nombre del símbolo
    with open(output_file, 'r') as f:
        lines = f.readlines()
        # Ordenar las líneas por el nombre del símbolo
        lines_sorted = sorted(lines, key=lambda x: x.split(',')[0])

    # Escribir las líneas ordenadas de vuelta al archivo
    with open(output_file, 'w') as f:
        f.writelines(lines_sorted)

    print(f"Archivo ordenado por nombre de símbolo: {output_file}")
