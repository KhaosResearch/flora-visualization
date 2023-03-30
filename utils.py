from folium.plugins import (Draw, Fullscreen, LocateControl, MeasureControl,
                            MousePosition)
import folium

def generate_map() -> folium.Map:
    map_folium = folium.Map(location=[36.71485, -4.49663],
    zoom_start=15)

    
    Fullscreen().add_to(map_folium)
    LocateControl().add_to(map_folium)
    MousePosition().add_to(map_folium)
    MeasureControl("bottomleft").add_to(map_folium)



    return map_folium

def popup_html(df, row, vega_chart):
    i = row
    utm = df['UTM'].iloc[i] 
    humedity = df['Humedad'].iloc[i]
    porcentage_humedity = df['% Humedad'].iloc[i] 
    organic_materia = df['Materia Orgánica'].iloc[i] 
    

    left_col_color = "#ADD8E6"
    right_col_color = "#c2c2c2"
    
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
        <td style="background-color: """+ left_col_color +""";"><span style= "margin-left: 4px;"> UTM </span></td>
        <td style="background-color: """+ left_col_color +""";"><span style= "margin-left: 4px;"> Humedity </span></td>
        <td style="background-color: """+ left_col_color +""";"><span style= "margin-left: 4px;"> % Humedity </span></td>
        <td style="background-color: """+ left_col_color +""";"><span style= "margin-left: 4px;"> Organic Materia </span></td>

    </tr>

    <tr>
        <td style="width: 150px;background-color: """+ right_col_color +""";">{}</td>""".format(utm) + """
        <td style="width: 150px;background-color: """+ right_col_color +""";">{}</td>""".format(humedity) + """
        <td style="width: 150px;background-color: """+ right_col_color +""";">{}</td>""".format(porcentage_humedity) + """
        <td style="width: 150px;background-color: """+ right_col_color +""";">{}</td>""".format(organic_materia) + """
    </tr>
    </tbody>
    </table>
    <div id="vis1"></div>

    <script type="text/javascript">
    vegaEmbed('#vis1', {}).catch(console.error);""".format(vega_chart.to_json(indent=None)) + """
    </script>
    </body>
    </html>
    """
    htmlw = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/vega@5"></script>
    <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/vega-lite@5"></script>
    <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>
    </head>
    <body>

    <div id="vis1"></div>

    <script type="text/javascript">
    vegaEmbed('#vis1', {vega_chart.to_json(indent=None)}).catch(console.error);
    </script>
    </body>
    </html>"""
    return html