import re
import geopandas as gpd
import folium
import numpy as np
import pandas as pd
from folium.plugins import (Fullscreen, LocateControl, MeasureControl,
                            MousePosition)




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


def generate_table_from_dict(dict_sample):

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


def popup_html_from_mongo(sample):
    combined_table = generate_table_from_dict(sample)
    html_list = []

    # Add tag to open and close the table
    combined_table.insert(0, "<table border='1' class='dataframe'> <tbody>")
    combined_table.append("</tbody> </table>")

    combined_table = "".join(combined_table)

    html_table_div = f"""
    <table style="width: 100%;">
    <tbody>
    <tr>
        <td style="padding: 10px;">{combined_table}</td>
    </tr>
    </tbody>
    </table>
    """

    html_list.append(html_table_div)
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




def filter_by_region(df, region):
    gdf_reg = gpd.read_file(region)
    df_intersection = gpd.sjoin(df, gdf_reg, predicate='within')
    df_region_filter = df[df.index.isin(df_intersection.index)]

    return df_region_filter