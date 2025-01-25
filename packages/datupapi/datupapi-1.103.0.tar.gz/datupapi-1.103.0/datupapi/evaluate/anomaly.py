import boto3
import numpy as np
import os
import pandas as pd

from pyod.models.lof import LOF
from datetime import datetime
from datupapi.configure.config import Config
from datupapi.extract.io import IO


class Anomaly(Config):

    DOCKER_CONFIG_PATH = os.path.join('/opt/ml/processing/input', 'config.yml')
    io = IO(config_file=DOCKER_CONFIG_PATH, logfile='data_prepare', log_path='output/logs')

    def __init__(self, config_file,logfile, log_path, *args, **kwargs):
        Config.__init__(self, config_file=config_file, logfile=logfile)
        self.log_path = log_path


    def detectar_anomalias_prep(df, location=False,
                            prob_lim_general=0.85,
                            prob_lim_item=0.95,
                            limite_cambio_demanda=0.1,
                            limite_nan = 0.05 
                            ):
        """
        Función para detectar anomalías y generar alertas en la preparación de nuevos clientes

        Parámetros obligatorios:
        - df: Dataframe a analizar. Debe incluir mínimo las columnas 'timestamp', 'item_id' y 'demand'.

        Parámetros opcionales:
        - location: Indica si existe la columna de location.
        - prob_lim_general: Límite de probabilidad para LOF general(default = 0.85).
        - prob_lim_item: Límite de probabilidad para LOF por item (default = 0.95).
        - limite_cambio_demanda: Límite para la alerta de cambio en la demanda (default = 10%).
        """

        # Preparar dataframe por total y por item
        df['demand'] = df['demand'].astype(float)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        demand_total = df[['timestamp','demand']]
        demand_total = demand_total.groupby('timestamp', as_index=False)['demand'].sum()

        demand_item = df[['timestamp','item_id','demand']]
        demand_item = demand_item.groupby(['timestamp', 'item_id'], as_index=False).agg({'demand': 'sum'}).sort_values(by='timestamp', ascending=False).reset_index(drop=True)
        demand_item = demand_item.reset_index()
        unique_items = demand_item['item_id'].unique()
        print('Unique items:',demand_item['item_id'].nunique())

        if location:
            print("Sección de análsis por item-loc en desarrollo")

        #1. LOF general ------
        demand_reshaped  = demand_total['demand'].values.reshape(-1, 1)
        lof = LOF(n_neighbors = 20, metric ="manhattan", novelty=True)
        lof.fit(demand_reshaped)
        #me quedo sólo con los datos anómalos
        probs = lof.predict_proba(demand_reshaped)
        is_out = probs[:,1] > prob_lim_general
        out = demand_total[is_out]

        #alerta
        alert_anomalies_total = True if not out.empty else False
        alert_anomalies_total_txt = f"Anomalias en el total de la demanda: {out.shape[0]}.\nDetalles: \n{out}" if alert_anomalies_total else ""

        #2. LOF por item ------
        out_if_item2 = pd.DataFrame()
        lof2 = LOF(n_neighbors = 20, metric ="manhattan", novelty=True)

        alerta_max = 0
        alerta_media = 0
        items_alerta_max = []
        items_alerta_media = []

        for item_id in unique_items:
            # Filtrar el DataFrame para el ítem actual
            item_tmp = demand_item[demand_item['item_id'] == item_id]

            # Verificar si hay suficientes datos para el modelo LOF
            if 24 < len(item_tmp) <= 48:
                alerta_media = alerta_media +1
                items_alerta_media.append(item_id)

            if len(item_tmp) > 24:  # Asegurar que haya suficientes puntos para aplicar LOF
                # Aplicar LOF
                lof2.fit(item_tmp[['demand']])
                probs = lof2.predict_proba(item_tmp[['demand']])
                is_out = probs[:, 1] > prob_lim_item
                out2 = item_tmp[is_out]

                # Concatenar los outliers del ítem actual al DataFrame de resultados
                out_if_item2 = pd.concat([out_if_item2, out2[['item_id', 'timestamp', 'demand']]], ignore_index=True)

            else:
                alerta_max = alerta_max + 1
                items_alerta_max.append(item_id)

        out_if_item2 = out_if_item2.drop_duplicates()
        #alerta por anomalias
        alert_anomalies_item = True if not out_if_item2.empty else False
        alert_anomalies_item_txt = f"Items con probabilidad de anomalía: {out_if_item2['item_id'].nunique()}. \nDetalles: \n{out_if_item2}" if alert_anomalies_item else ""

        #3. Alerta por items con poco histórico -------------------
        alert_insufficient_history = True if alerta_max > 0 or alerta_media > 0 else False
        alert_insufficient_history_txt = f"Items con menos de 24 meses en el histórico: {alerta_max}. ({', '.join(map(str, items_alerta_max))}). " if alerta_max > 0 else ""
        alert_insufficient_history_txt += f"Items con menos de 48 meses en el histórico: {alerta_media}. ({', '.join(map(str, items_alerta_media))})." if alerta_media > 0 else ""

        #4. Cambio drástico en la demanda total en comparación con el mes anterior --OJO ESTO DEBE IR DESPUÉS DEL RESAMPLE
        demand_actual = demand_total['demand'].iloc[-1]
        demand_ant = demand_total['demand'].iloc[-2]
        percentage_change = ((demand_actual - demand_ant) / demand_ant) * 100

        alert_demand_var = True if abs(percentage_change) > limite_cambio_demanda*100 else False
        alert_demand_var_txt = f"Variación en la demanda total: {percentage_change:.2f}%." if alert_demand_var else ""
        print(f"Demanda tuvo un cambio del {percentage_change:.2f}% respecto al mes anterior.")

        #5. Columnas con información incompleta
        incomplete_columns = []
        for col in df.columns:
            missing_ratio = df[col].isna().mean()
            print(f"Columna '{col}' tiene un {missing_ratio:.2%} de valores faltantes.")
            if missing_ratio >= limite_nan:
                incomplete_columns.append((col, missing_ratio))  

        if incomplete_columns:
            alert_incomplete_col = True
            column_details = [f"{col} ({missing_ratio:.2%})" for col, missing_ratio in incomplete_columns]
            alert_incomplete_col_txt = f"Columnas con más del {limite_nan * 100:.2f}% de información vacía: {', '.join(column_details)}."
        else:
            alert_incomplete_col = False
            alert_incomplete_col_txt = ""

        ## --------------------- MATRIZ DE ALERTAS ------------------------------

        alert_messages = [alert_anomalies_total_txt,
                        alert_anomalies_item_txt,
                        alert_insufficient_history_txt,
                        alert_demand_var_txt,
                        alert_incomplete_col_txt
                        ]

        alert_summary = '\n'.join(filter(None, alert_messages)) if any(alert_messages) else "Sin alertas"
        print(alert_summary)

        alert_matrix = pd.DataFrame({
            'Anomalias_Total_Demand': [alert_anomalies_total],
            'Anomalias_Item': [alert_anomalies_item],
            'Historico': [alert_insufficient_history],
            'Var_Demanda_Total': [alert_demand_var],
            'Info_Vacia': [alert_incomplete_col],
            'Alertas': [alert_summary]
        })

        return alert_matrix
    

    def detectar_anomalias_estable(
            self,
            prob_lim_general = 0.85,
            prob_lim_item = 0.95,
            limite_cambio_items = 20,
            limite_cambio_demanda = 10,
            limite_nan = 0.5,
            limite_cambio_demanda_item = 50,
            prob_lim_general_frcst = 0.85,
            prob_lim_item_frcst = 0.95,
            limite_precision = 40,
            limite_cambio_loc = 5
            ):
        """
        Función para detectar anomalías y generar alertas en clientes estables

        Parámetros opcionales:
        - prob_lim_general: Límite de probabilidad de anomalía con LOF para el historico general (default = 0.85).
        - prob_lim_item: Límite de probabilidad de anomalía con LOF para el historico por item (default = 0.95).
        - limite_cambio_items: Límite para la alerta de cambio en número de items (default = 20%).
        - limite_cambio_demanda: Límite para la alerta de cambio en la demanda (default = 10%).
        - limite_nan = Límite en porcentaje para alerta de información vacia en las columnas del prep (default = 0.5)
        - limite_cambio_demanda_item = Límite en porcentanje para alerta por cambio de la demanda de un item entre el mes pasado y el actual (default = 50)
        - prob_lim_general_frcst = Límite de probabilidad de anomalía con LOF para los pronósticos generales (default = 0.85)
        - prob_lim_item_frcst = Límite de probabilidad de anomalía con LOF para los pronósticos por item (default = 0.95)
        - limite_precision = Límite en porcentaje de accuracy para generar alerta por precisión baja (default = 40)
        - limite_cambio_loc = Límite en cambio porcentual para alerta por cambios en el número de ubicaciones (default = 5)
        """
        datalake_path_prep = os.dataset_import_path[0]
        datalake_path_forecast = os.results_path + '/Qmfcst/Qmfcst.csv'
        datalake_path_eff = os.results_path + '/Qeff/Qeff.csv'
        location = os.use_location

        print('Ruta prep',datalake_path_prep)
        print('Ruta forecast',datalake_path_forecast)
        print('Ruta eff',datalake_path_eff)
        print('Location:', location)

        # Descargar los datasets
        df_demand = self.io.download_object_csv(datalake_path=datalake_path_prep)
        df_forecast = self.io.download_object_csv(datalake_path=datalake_path_forecast)
        df_eff = self.io.download_object_csv(datalake_path=datalake_path_eff)

        # Preparar Qprep por total y por item
        df_demand['demand'] = df_demand['demand'].astype(float)
        df_demand['timestamp'] = pd.to_datetime(df_demand['timestamp'])

        demand_total = df_demand.groupby('timestamp').sum()
        demand_total = demand_total.drop(columns=['item_id'])

        demand_item = df_demand.groupby(['timestamp','item_id']).sum()
        demand_item = demand_item.reset_index()
        unique_items = demand_item['item_id'].unique()
        
        #------------------------------------ ALERTAS DEL QPREP ---------------------------------
        # 1. LOF general ------
        demand_reshaped = demand_total['demand'].values.reshape(-1, 1)
        lof = LOF(n_neighbors=20, metric="manhattan", novelty=True)
        lof.fit(demand_reshaped)

        # Me quedo sólo con los datos anómalos
        probs = lof.predict_proba(demand_reshaped)
        is_out = probs[:, 1] > prob_lim_general
        out = demand_total[is_out]

        # Alerta
        alert_anomalies_total = not out.empty
        alert_anomalies_total_txt = (f"Anomalias en el total de la demanda: {out.shape[0]}.\nDetalles: \n{out}"
                                    if alert_anomalies_total else "")

        # 2. LOF por item ------
        out_if_item2 = pd.DataFrame()
        lof2 = LOF(n_neighbors=20, metric="manhattan", novelty=True)

        alerta_max = 0
        alerta_media = 0
        items_alerta_max = []
        items_alerta_media = []

        for item_id in unique_items:
            # Filtrar el DataFrame para el ítem actual
            item_tmp = demand_item[demand_item['item_id'] == item_id]

            # Verificar si hay suficientes datos para el modelo LOF
            if 24 < len(item_tmp) <= 48:
                alerta_media += 1
                items_alerta_media.append(item_id)

            if len(item_tmp) > 24:  # Asegurar que haya suficientes puntos para aplicar LOF
                # Aplicar LOF
                lof2.fit(item_tmp[['demand']])
                probs = lof2.predict_proba(item_tmp[['demand']])
                is_out2 = probs[:, 1] > prob_lim_item
                out2 = item_tmp[is_out2]

                # Concatenar los outliers del ítem actual al DataFrame de resultados
                out_if_item2 = pd.concat([out_if_item2, out2[['item_id', 'timestamp', 'demand']]], ignore_index=True)

            else:
                alerta_max += 1
                items_alerta_max.append(item_id)

        out_if_item2 = out_if_item2.drop_duplicates()

        # Alerta por anomalías
        alert_anomalies_item = not out_if_item2.empty
        alert_anomalies_item_txt = (f"Items con probabilidad de anomalía: {out_if_item2['item_id'].nunique()}. \nDetalles: \n{out_if_item2}"
                                    if alert_anomalies_item else "")

        # 3. Alerta por items con poco histórico -------------------
        alert_insufficient_history = alerta_max > 0 or alerta_media > 0
        alert_insufficient_history_txt = (
            f"Items con menos de 24 meses en el histórico: {alerta_max}. ({', '.join(map(str, items_alerta_max))}). "
            if alerta_max > 0 else "")
        alert_insufficient_history_txt += (
            f"Items con menos de 48 meses en el histórico: {alerta_media}. ({', '.join(map(str, items_alerta_media))})."
            if alerta_media > 0 else "")

        # 4. Cambio drástico en la demanda total en comparación con el mes anterior --------------
        demand_actual = demand_total['demand'].iloc[-1]
        demand_ant = demand_total['demand'].iloc[-2]
        percentage_change = ((demand_actual - demand_ant) / demand_ant) * 100

        alert_demand_var = abs(percentage_change) > limite_cambio_demanda * 100
        alert_demand_var_txt = f"Variación en la demanda total: {percentage_change:.2f}%." if alert_demand_var else ""
        print(f"Demanda tuvo un cambio del {percentage_change:.2f}% respecto al mes anterior.")

        ## 5. Cambio drástico en la demanda por items en comparación con el mes anterior -----------
        df_demand['timestamp'] = pd.to_datetime(df_demand['timestamp'])
        df_demand['item_id'] = df_demand['item_id'].astype(str)
        cambio_demand = df_demand[df_demand['timestamp'].isin([df_demand['timestamp'].max(), df_demand['timestamp'].max() - pd.DateOffset(months=1)])]
        cambio_demand = cambio_demand.sort_values(by=['item_id','location','timestamp'], ascending=True)
        cambio_demand['month_prev_demand'] = cambio_demand.groupby('item_id')['demand'].shift(1)
        cambio_demand['month_delta_demand'] = (cambio_demand['demand'] - cambio_demand['month_prev_demand'])/cambio_demand['month_prev_demand']*100
        cambio_demand = cambio_demand.replace([np.inf, -np.inf], 100)
        cambio_demand = cambio_demand.fillna(0)
        cambio_demand = cambio_demand[cambio_demand['timestamp'] == cambio_demand['timestamp'].max()]

        #Alerta
        cambio_demand_alert = cambio_demand[abs(cambio_demand['month_delta_demand'])>limite_cambio_demanda_item]
        items_alerta = cambio_demand_alert['item_id'].nunique()
        alert_demand_item_var = True if cambio_demand_alert['month_delta_demand'].sum() > 0 else False
        alert_demand_item_var_txt = f"Hay {items_alerta} items con una variación en su demanda mayor al {limite_cambio_demanda_item}%." if alert_demand_item_var else ""
        print(alert_demand_item_var_txt)

        # 6. Columnas con información incompleta ---------
        incomplete_columns = []
        for col in df_demand.columns:
            missing_ratio = df_demand[col].isna().mean()
            print(f"Columna '{col}' tiene un {missing_ratio:.2%} de valores faltantes.")
            if missing_ratio >= limite_nan:
                incomplete_columns.append((col, missing_ratio))

        if incomplete_columns:
            alert_incomplete_col = True
            column_details = [f"{col} ({missing_ratio:.2%})" for col, missing_ratio in incomplete_columns]
            alert_incomplete_col_txt = (
                f"Columnas con más del {limite_nan * 100:.2f}% de información vacía: {', '.join(column_details)}."
            )
        else:
            alert_incomplete_col = False
            alert_incomplete_col_txt = ""


        #-------------------------------------- ALERTAS DE MULTIFORECAST --------------------------------------------
        df_forecast = df_forecast[['Date','Item','Target','SuggestedForecast']]
        df_forecast['Date'] = pd.to_datetime(df_forecast['Date'])
        total_mfrcst = df_forecast.groupby('Date').sum()
        total_mfrcst = total_mfrcst.drop(columns=['Item'])

        item_mfrcst = df_forecast.groupby(['Date','Item']).sum()
        item_mfrcst = item_mfrcst.reset_index()
        unique_items = item_mfrcst['Item'].unique()

        print('Items únicos en multiforecast: ',item_mfrcst['Item'].nunique())

        ## 7. LOF para multiforecast general ------------
        forecast_reshaped  = total_mfrcst['SuggestedForecast'].values.reshape(-1, 1)

        #novelty=True permite utilizar el método predict_proba para obtener las probabilidades de cada punto.
        lof_f = LOF(n_neighbors=20, metric="manhattan", novelty=True)
        lof_f.fit(forecast_reshaped)

        ##imprime los labels: 0 para normal, 1 para atípico
        print(lof_f.labels_)

        #me quedo sólo con los datos anómalos
        probs = lof_f.predict_proba(forecast_reshaped)
        is_out3 = probs[:,1] > prob_lim_general_frcst
        out3 = total_mfrcst[is_out3]

        # Alerta
        alert_anomalies_frcst_total = not out.empty
        alert_anomalies_frcst_total_txt = (f"Anomalias en los pronósticos totales: {out3.shape[0]}.\nDetalles: \n{out3}" if alert_anomalies_frcst_total else "")
        print(alert_anomalies_frcst_total_txt)

        ## 8. LOF para multiforecast POR ITEM ---------------
        out_if_item4 = pd.DataFrame()
        lof4 = LOF(n_neighbors = 20, metric ="manhattan")

        for item_id in unique_items:
            # Filtrar el DataFrame para el ítem actual
            item_tmp = item_mfrcst[item_mfrcst['Item'] == item_id]

            # Aplicar LOF
            lof4.fit(item_tmp[['SuggestedForecast', 'Target']])
            probs = lof4.predict_proba(item_tmp[['SuggestedForecast', 'Target']])
            is_out4 = probs[:, 1] > prob_lim_item_frcst
            out4 = item_tmp[is_out4]

            # Concatenar los outliers del ítem actual al DataFrame de resultados
            out_if_item4 = pd.concat([out_if_item4, out4[['Date', 'Item', 'SuggestedForecast', 'Target']]], ignore_index=True)

            #Filtrar solo las fechas en donde target = 0
            out_if_item4 = out_if_item4[out_if_item4['Target'] == 0]


        # Mostrar el DataFrame con todos los outliers encontrados
        out_if_item4 = out_if_item4.drop_duplicates()
        print("Número de items con probabilidad mayor a 95% de anomalía: ",out_if_item4['Item'].nunique())

        # Alerta por anomalías
        alert_anomalies_frcst_item = not out_if_item4.empty
        alert_anomalies_item_frcst_txt = (f"Items con probabilidad de anomalía en los pronósticos: {out_if_item4['Item'].nunique()}. \nDetalles: \n{out_if_item4}"
                                    if alert_anomalies_item else "")

        #-------------------------------------------------- ALERTAS DE EFFICIENCIA --------------------------------------
        df_eff['Item'] = df_eff['Item'].astype(str)
        print(df_eff['Item'].nunique())
        df_eff =df_eff[['Date', 'Item', 'Location', 'Ranking', 'Target', 'SuggestedForecast', 'NextSuggestedForecast',
            'BackSuggestedForecast', 'AccuracySuggForecast', 'AccuracyNextForecast', 'AccuracyBackForecast',
            'ItemType', 'AccuracyBestFit', 'IntervalBestFit']]

        ##9. items con baja precisión ---------------
        items_baja_precision = df_eff[df_eff['AccuracyBestFit']<limite_precision]
        num_items_baja_precision = items_baja_precision['Item'].nunique()

        ##10. items de alto impaco con baja precisión  ------------------
        items_baja_precision_alto = df_eff[(df_eff['AccuracyBestFit']<limite_precision)&(df_eff['ItemType']=='Items Alto Impacto')]
        num_items_baja_precision_alto = items_baja_precision_alto['Item'].nunique()

        #Alerta
        alert_precision = True if num_items_baja_precision > 0 else False
        alert_precision_txt = f"Hay {num_items_baja_precision} items con precisión menor al {limite_precision}%." if alert_precision else ""
        print(alert_precision_txt)

        alert_precision_impato = True if num_items_baja_precision_alto > 0 else False
        alert_precision_impacto_txt = f"Hay {num_items_baja_precision_alto} items de alto impacto con precisión menor al {limite_precision}%." if alert_precision_impato else ""
        print(alert_precision_impacto_txt)

        #------------------------------------------------- ALERTAS DE LOGS ----------------------------------------------------
        sql = f"SELECT * FROM `datup-supplyai-dev.infodatupprocess.TblLogsForecasting` WHERE Project LIKE '{self.io.tenant_id}'"
        gcp_forecast = self.io.download_bigquery_table(project_id='datup-supplyai-dev' ,
                                                tenant_id='infodatupprocess',
                                                table_name='TblLogsForecasting',
                                                sqlQuery=sql,
                                                gcp_key='datup-supplyai-dev-gcp.json')

        gcp_forecast = gcp_forecast.sort_values(by=['Date', 'Time'], ascending=[True, True])
        gcp_forecast['Date'] = pd.to_datetime(gcp_forecast['Date'])

        log_forecast = gcp_forecast.groupby(gcp_forecast['Date'].dt.to_period('M')).tail(1).reset_index(drop=True)
        drop_columns = ['Time', 'Customer', 'Type', 'SeasonalType', 'TrendType', 'ResidualType', 'ForecastNaive', 'AvgResidual',
                        'ForecastLo95', 'ForecastLo80', 'ForecastLo60','ForecastPoint','ForecastUp60','ForecastUp80','ForecastUp95',
                        'MASE', 'SuggestedForecastSales','NextSuggestedForecastSales','BackSuggestedForecastSales']
        log_forecast = log_forecast.drop(columns=drop_columns)
        print(f'Logs descargados y recortados a {log_forecast.shape[0]} ejecuciones.')

        #11. Cambios en el número total de items ----------------------
        num_actual_items = demand_item['item_id'].nunique()
        num_ant_items = log_forecast['Items'].iloc[-2]
        cambio_num_items = ((num_actual_items - num_ant_items) / num_ant_items) * 100

        #Alerta
        alert_items_var = True if abs(cambio_num_items) > 10 else False
        alert_items_var_txt = f"Variación en items: {cambio_num_items:.2f}%." if alert_items_var else ""
        print(f"El número de ítems únicos ha cambiado en un {cambio_num_items:.2f}%.")

        #12. Cambios en el número total de ubicaciones  -------------- DE UBICACIÓN
        if location:
            num_actual_loc = df_demand['location'].nunique()
            num_ant_loc = log_forecast['Locations'].iloc[-2]
            cambio_num_loc = ((num_actual_loc - num_ant_loc) / num_ant_loc) * 100
        else:
            cambio_num_loc = 0

        #Alerta
        alert_loc_var = True if abs(cambio_num_loc) > limite_cambio_loc else False
        alert_loc_var_txt = f"Variación en ubicaciones: {cambio_num_loc:.2f}%." if alert_loc_var else ""
        print(f"El número de ubicaciones únicos ha cambiado en un {cambio_num_loc:.2f}%.")

        ##13. Aumento en el WMAPE
        wmape_actual = log_forecast['WMAPE'].iloc[-1]
        wmape_anterior = log_forecast['WMAPE'].iloc[-2]

        #Alerta
        alert_wmape_var = True if  wmape_anterior < wmape_actual else False
        alert_wmape_var_txt = f"El error promedio aumentó de {wmape_anterior:.2f}% a {wmape_actual:.2f}%" if alert_wmape_var else ""
        print(f"El error pasó de {wmape_anterior:.2f}% a {wmape_actual:.2f}%")
        print(alert_wmape_var_txt)

        ## --------------------- MATRIZ DE ALERTAS ------------------------------
        alert_messages = [
            alert_anomalies_total_txt,
            alert_anomalies_item_txt,
            alert_insufficient_history_txt,
            alert_demand_var_txt,
            alert_demand_item_var_txt,
            alert_incomplete_col_txt,
            alert_anomalies_frcst_total_txt,
            alert_anomalies_item_frcst_txt,
            alert_precision_txt,
            alert_precision_impacto_txt,
            alert_items_var_txt,
            alert_loc_var_txt,
            alert_wmape_var_txt
        ]

        alert_summary = '\n'.join(filter(None, alert_messages)) if any(alert_messages) else "Sin alertas"
        print(alert_summary)

        alert_matrix = pd.DataFrame({
            'FechaEjecucion': [pd.Timestamp.now().date()],
            'AnomaliasPrepTotal': [alert_anomalies_total],
            'AnomaliasPrepItem': [alert_anomalies_item],
            'HistoricoCorto': [alert_insufficient_history],
            'VarDemandaTotal': [alert_demand_var],
            'VarDemanda_Item': [alert_demand_item_var],
            'ColumnasVacias': [alert_incomplete_col],
            'AnomaliasForecastTotal': [alert_anomalies_frcst_total],
            'AnomaliasForecastItem': [alert_anomalies_frcst_item],
            'PrecisionBaja': [alert_precision],
            'PrecisionBaja_ImpactoAlto': [alert_precision_impato],
            'Var_Items': [alert_items_var],
            'Var_Loc': [alert_loc_var],
            'WMAPE': [alert_wmape_var],
            'Alertas': [alert_summary]
        })

        print('Matriz de la ejecuón creada. Calculando número total de alertas....')
        # Número total de alertas

        alert_columns = [
            'AnomaliasPrepTotal',
            'AnomaliasPrepItem',
            'HistoricoCorto',
            'VarDemandaTotal',
            'VarDemanda_Item',
            'ColumnasVacias',
            'AnomaliasForecastTotal',
            'AnomaliasForecastItem',
            'PrecisionBaja',
            'PrecisionBaja_ImpactoAlto',
            'Var_Items',
            'Var_Loc',
            'WMAPE'
        ]

        alert_matrix.insert(1, 'TotalAlertas', alert_matrix[alert_columns].sum(axis=1))

        ####-------------------------CONCATENACIÓN Y CARGA DE LA MATRIZ
        old_matrix = self.io.download_object_csv(datalake_path='output/Alertas/Alertas.csv')
        new_matrix = pd.concat([old_matrix, alert_matrix])
        self.io.upload_csv(new_matrix, q_name='Alertas', datalake_path='output')
        # self.io.populate_bigquery_table(alert_matrix, project_id='datup-supplyai-dev', tenant_id=self.io.tenant_id, table_name='TblAlerts', write_mode='overwrite')
        self.io.populate_bigquery_table(alert_matrix, project_id='datup-supplyai-dev', tenant_id=self.io.tenant_id, table_name='TblAlerts', write_mode='append')
        print('Matriz de alertas cargada en BigQuery')
        return alert_matrix

anomalia = Anomaly()    