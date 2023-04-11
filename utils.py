import folium
from folium.plugins import (Draw, Fullscreen, LocateControl, MeasureControl,
                            MousePosition)
import pandas as pd
import numpy as np

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
    half = len(df.columns)/2
    first_half = df.iloc[i,:int(half)]
    last_half = df.iloc[i,int(half):]


    html_first_table = pd.DataFrame(first_half).to_html(header = False)
    html_last_table = pd.DataFrame(last_half).to_html(header = False)
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
    
    print(html_first_table)

    return html_def

def generate_table_fom_dict(dict_sample):

    keys = list(dict_sample.keys())
    print(keys)
    left_col_color = "#ADD8E6"
    right_col_color = "#c2c2c2"
    header_list = []
    table_data_list = []
    for ky in range(len(keys)):
        print(keys[ky])
        if keys[ky] != "Pictures" and keys[ky] != "Species":
            print("dvgcdvdvvdvd")
            table_header = (
                f"""
            
            <td style="background-color: """
                + left_col_color
                + """;"><span style= "margin-left: 4px;"> {} </span></td>""".format(
                    keys[ky]
                )
                + """
            """
            )
            header_list.append(table_header)

            table_data = (
                f"""
            <td style="width: 150px;background-color: """
                + right_col_color
                + """;">{}</td>""".format(dict_sample[keys[ky]])
                + """
            """
            )
            table_data_list.append(table_data)
    return header_list, table_data_list




def popup_html_from_mongo(sample, pics):
    #print(sample)
    sample.pop("Pictures")
    
    keys = list(sample.keys())
    half = int(len(keys)/2)
    #print("FFFFFFFFFFFFFFFFFFFFFFFFF",half)
    first_half = {k: sample[k] for k in list(sample)[:half]}
    last_half = {k: sample[k] for k in list(sample)[half:]}
    #print("FFFFFFFFFFFFFFFFFFFFFFFFF",first_half)
    

    header_list_first, table_data_list_fist = generate_table_fom_dict(first_half)
    header_list_last, table_data_list_last = generate_table_fom_dict(last_half)
    keys = list(sample.keys())
    left_col_color = "#ADD8E6"
    right_col_color = "#c2c2c2"
    html_list = []
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/vega@5"></script>
    <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/vega-lite@5"></script>
    <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>
    </head>
    <body>
    <table style="height: 126px; width: 350px;">
    <tbody>
    <tr>
    """
    html_list.append(html)


    html_complete = html_list + header_list_first
    html_complete.append(" </tr> <tr>")

    html_complete = html_complete + table_data_list_fist
    html_complete.append("</tr> <tr>")

    html_complete = html_complete + header_list_last
    html_complete.append(" </tr> <tr>")

    html_complete = html_complete + table_data_list_last
    html_complete.append("</tr>")

    html_species = (
        f"""
    <table style="height: 126px; width: 350px;">
        <caption>Species</caption>
        <tr>
            <td style="background-color: """
        + left_col_color
        + """;"><span style= "margin-left: 4px;"> Name </span></td>
            <td style="background-color: """
        + left_col_color
        + """;"><span style= "margin-left: 4px;"> Ind </span></td>
        </tr>
    
    """
    )
    html_complete.append(html_species)
    sample["Species"]
    species_sorted = sorted(sample["Species"], key=lambda d: d["Name"])

    for sp in range(len(sample["Species"])):
        html_species_row = (
            """
            <tr>
                <td style="background-color: """
            + right_col_color
            + """;"><span style= "margin-left: 4px;"> {} </span></td>""".format(
                species_sorted[sp]["Name"]
            )
            + """
                <td style="background-color: """
            + right_col_color
            + """;"><span style= "margin-left: 4px;"> {} </span></td>""".format(
                species_sorted[sp]["Ind"]
            )
            + """
            </tr>"""
        )
        html_complete.append(html_species_row)

    html_complete.append("</table>")
    html_complete.append(pics)
    html_def = "".join(html_complete)

    return html_def
