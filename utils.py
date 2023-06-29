import re
import geopandas as gpd
import pandas as pd




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
    link_pictures_link = []

    for ky in range(len(keys)):
        if keys[ky] != "_id":
            if keys[ky] == "Pictures":
                key_table = "Pictures"
                for i in range(len(dict_sample[keys[ky]])):
                    link_pictures_link.append(
                        f'<li><a href="{ dict_sample[keys[ky]][i]}">{dict_sample[keys[ky]][i].split("/")[-1].split("?")[0]}</a></li>'
                    )
                value = f'<td>{" ".join(link_pictures_link)}</td>'
            elif keys[ky] == "eventDate":
                key_table = "eventDate"
                value = f'<td>{dict_sample[keys[ky]].strftime("%Y-%m-%d")}</td>'
            else:
                if keys[ky]=="specieName":
                    key_table="Species Name"
                elif keys[ky]=="ENBIC2ID":
                    key_table="ENBIC2ID"
                elif keys[ky]=="NaturalSite":
                    key_table="Natural Site"
                elif keys[ky]=="gbifID":
                    key_table="gbifID"
                elif keys[ky]=="institutionCode":
                    key_table="Institution Code"
                elif keys[ky]=="catalogNumber":
                    key_table="Catalog Number"
                elif keys[ky]=="scientificName":
                    key_table="Scientific Name"
                elif keys[ky]=="aut_infra":
                    key_table="aut_infra"
                elif keys[ky]=="taxonRankInterpreted":
                    key_table="Taxon Rank Interpreted"
                elif keys[ky]=="speciesInterpreted":
                    key_table="Species Interpreted"
                elif keys[ky]=="identifiedBy":
                    key_table="Identified By"
                elif keys[ky]=="dateIdentified":
                    key_table="Date Identified"
                elif keys[ky]=="countryCode":
                    key_table="Country Code"
                elif keys[ky]=="stateProvince":
                    key_table="State Province"
                elif keys[ky]=="locality":
                    key_table="Locality"
                elif keys[ky]=="decimalLatitude":
                    key_table="Latitude"
                elif keys[ky]=="decimalLongitude":
                    key_table="Longitude"
                elif keys[ky]=="MGRS":
                    key_table="MGRS"
                elif keys[ky]=="coordinateUncertaintyInMeters":
                    key_table="Coordinate Uncertainty(m)"
                elif keys[ky]=="elevation":
                    key_table="Elevation"
                elif keys[ky]=="eventDate":
                    key_table="EventDate"
                elif keys[ky]=="remarks":
                    key_table="Remarks"
                else:
                    key_table = keys[ky]
                value = f"<td>{dict_sample[keys[ky]]}</td>"
            if dict_sample[keys[ky]]=="":
                value=f"<td>Undefined</td>"

            table = f"""
            <tr>
                <th>{key_table}</th>
                {value}
            </tr>
            """
            table_list.append(table)

    return table_list


def popup_html_from_mongo(sample):
    combined_table = generate_table_from_dict(sample)
    html_list = []

    # Add tag to open and close the table
    combined_table.insert(
        0, "<table border='1' class='dataframe' style='margin: 0 auto;'> <tbody>"
    )
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

