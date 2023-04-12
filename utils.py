import re

import folium
import numpy as np
import pandas as pd
from folium.plugins import (Fullscreen, LocateControl, MeasureControl,
                            MousePosition)


def generate_map(location, zoom) -> folium.Map:
    map_folium = folium.Map(location=location, zoom_start=zoom)

    Fullscreen().add_to(map_folium)
    LocateControl().add_to(map_folium)
    MousePosition().add_to(map_folium)
    MeasureControl("bottomleft").add_to(map_folium)
    map_layers_dict = {
        "World Street Map": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
        "Satellite": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        "Google Maps": "https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
        "Google Satellite": "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
        "Google Terrain": "https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}",
        "Google Satellite Hybrid": "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
    }
    for layer in map_layers_dict:
        folium.TileLayer(
            tiles=map_layers_dict[layer], attr=layer, name=layer, show=False
        ).add_to(map_folium)

    folium.LayerControl(position="bottomleft").add_to(map_folium)
    return map_folium


def popup_html_from_df(df, row, vega_chart):

    i = row
    half = len(df.columns) / 2
    first_half = df.iloc[i, : int(half)]
    last_half = df.iloc[i, int(half) :]

    html_first_table = pd.DataFrame(first_half).to_html(header=False)
    html_last_table = pd.DataFrame(last_half).to_html(header=False)
    header_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/vega@5"></script>
    <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/vega-lite@5"></script>
    <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>
    </head>
    <body>
    """

    html_chart = f"""
    
    <div id="vis1"></div>

    <script type="text/javascript">
    vegaEmbed('#vis1', {vega_chart.to_json(indent=None)})
    </script>
    """

    html_table_div = f"""
    <table style="border-collapse: collapse; width: 100%;" border="1">
    <tbody>
    <tr>
    <td style="width: 50%;">{html_first_table}</td>
    <td style="width: 50%;">{html_last_table}</td>
    </tr>
    </tbody>
    </table>
 
    
    """
    html_def = header_html + html_chart + html_table_div + " </body> </html>"

    return html_def


def generate_table_fom_dict(dict_sample):

    keys = list(dict_sample.keys())
    table_list = []
    for ky in range(len(keys)):
        if keys[ky] != "Pictures" and keys[ky] != "Species":
            table = (
                f"""
            <tr>
                <th  """
                + """> {}</th>""".format(keys[ky])
                + """
                <td """
                + """>{}</td>""".format(dict_sample[keys[ky]])
                + """
            </tr>
            """
            )
            table_list.append(table)
    return table_list


def popup_html_from_mongo(sample, pics):
    # print(sample)
    sample.pop("Pictures")

    keys = list(sample.keys())
    half = int(len(keys) / 2)

    first_half = {k: sample[k] for k in list(sample)[:half]}
    last_half = {k: sample[k] for k in list(sample)[half:]}

    first_table = generate_table_fom_dict(first_half)
    last_table = generate_table_fom_dict(last_half)
    keys = list(sample.keys())
    html_list = []

    # Add tag to open and close each table
    first_table.insert(0, "<table border='1' class='dataframe'> <tbody>")
    first_table.append("</tbody> </table>")

    last_table.insert(0, "<table border='1' class='dataframe'> <tbody>")
    last_table.append("</tbody> </table>")

    last_table = "".join(last_table)
    first_table = "".join(first_table)

    html_table_div = f"""
    <table style="border-collapse: collapse; width: 100%;" border="1">
    <tbody>
    <tr>
        <td style="width: 50%;">{first_table}</td>
        <td style="width: 50%;">{last_table}</td>
    </tr>
    </tbody>
    </table>
 
    
    """
    html_list.append(html_table_div)

    html_species = f"""
    <table style= "width: 100%; margin-top: 10px" class='dataframe' border='1'>
        <caption style="background-color:#3630a3; 
                  color:white; 
                  padding:5px;">Species</caption>
        <tr>
            <th> Name </th>
            <th> Ind </span></th>
        </tr>
    
    """
    html_list.append(html_species)
    sample["Species"]
    species_sorted = sorted(sample["Species"], key=lambda d: d["Name"])

    for sp in range(len(sample["Species"])):
        html_species_row = (
            """
            <tr>
                <td> {}</td>""".format(
                species_sorted[sp]["Name"]
            )
            + """
                <td> {} </td>""".format(
                species_sorted[sp]["Ind"]
            )
            + """
            </tr>"""
        )
        html_list.append(html_species_row)

    html_list.append("</table>")
    html_list.append(pics)
    html_def = "".join(html_list)

    return html_def


def diacritic_sensitive_regex(string):
    string = re.sub(r"[aáàäâ]", "[a,á,à,ä,â]", string)
    string = re.sub(r"[AÁÀÄÂ]", "[A,a,á,à,ä,â]", string)
    string = re.sub(r"[eéëè]", "[e,é,ë,è]", string)
    string = re.sub(r"[EÉËÈ]", "[E,e,é,ë,è]", string)
    string = re.sub(r"[iíïì]", "[i,í,ï,ì]", string)
    string = re.sub(r"[IÍÏÌ]", "[I,i,í,ï,ì]", string)
    string = re.sub(r"[oóöò]", "[o,ó,ö,ò]", string)
    string = re.sub(r"[OÓÖÒ]", "[O,o,ó,ö,ò]", string)
    string = re.sub(r"[uúüù]", "[u,ü,ú,ù]", string)
    string = re.sub(r"[UÚÜÙ]", "[U,u,ü,ú,ù]", string)
    return string
