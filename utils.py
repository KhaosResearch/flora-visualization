from folium.plugins import (Draw, Fullscreen, LocateControl, MeasureControl,
                            MousePosition)
import folium

def generate_map(location, zoom) -> folium.Map:
    map_folium = folium.Map(location=location,
    zoom_start=zoom)

    
    Fullscreen().add_to(map_folium)
    LocateControl().add_to(map_folium)
    MousePosition().add_to(map_folium)
    MeasureControl("bottomleft").add_to(map_folium)



    return map_folium

def popup_html_from_df(df, row, vega_chart):
    i = row
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
    header_list= []
    table_data_list= []
    for c in range(len(df.columns)):
        table_header = f"""
        
        <td style="background-color: """+ left_col_color +""";"><span style= "margin-left: 4px;"> {} </span></td>""".format(df.columns[c]) + """
        """
        header_list.append(table_header)

        table_data= f"""
        <td style="width: 150px;background-color: """+ right_col_color +""";">{}</td>""".format(df.loc[i][c]) + """
        """
        table_data_list.append(table_data)
        #</tr>

    html_complete = html_list + header_list
    html_complete.append(' </tr> <tr>' )

    html_complete = html_complete + table_data_list
    html_complete.append('</tr>')


    

    html_chart = f"""
    </tbody>
    </table>
    <div id="vis1"></div>

    <script type="text/javascript">
    vegaEmbed('#vis1', {vega_chart.to_json(indent=None)})
    </script>
    </body>
    </html>
    """
    html_complete.append(html_chart)
    html_def = "".join(html_complete)
    
    return html_def


def popup_html_from_mongo(sample, pics):
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
    header_list= []
    table_data_list= []
    for k in range(len(keys)):
        if keys[k] != "Pictures" and keys[k] != "Species":
            table_header = f"""
            
            <td style="background-color: """+ left_col_color +""";"><span style= "margin-left: 4px;"> {} </span></td>""".format(keys[k]) + """
            """
            header_list.append(table_header)

            table_data= f"""
            <td style="width: 150px;background-color: """+ right_col_color +""";">{}</td>""".format(sample[keys[k]]) + """
            """
            table_data_list.append(table_data)
        

    html_complete = html_list + header_list
    html_complete.append(' </tr> <tr>' )

    html_complete = html_complete + table_data_list
    html_complete.append('</tr>')

    html_species = f"""
    <table style="height: 126px; width: 350px;">
        <caption>Species</caption>
        <tr>
            <td style="background-color: """+ left_col_color +""";"><span style= "margin-left: 4px;"> Name </span></td>
            <td style="background-color: """+ left_col_color +""";"><span style= "margin-left: 4px;"> Ind </span></td>
        </tr>
    
    """
    html_complete.append(html_species)
    for sp in range(len(sample['Species'])):
        html_species_row = """
            <tr>
                <td style="background-color: """+ right_col_color +""";"><span style= "margin-left: 4px;"> {} </span></td>""".format(sample['Species'][sp]['Name']) + """
                <td style="background-color: """+ right_col_color +""";"><span style= "margin-left: 4px;"> {} </span></td>""".format(sample['Species'][sp]['Ind']) + """
            </tr>"""
        html_complete.append(html_species_row)
    
    html_complete.append('</table>')
    html_complete.append(pics)
    html_def = "".join(html_complete)
    
    return html_def