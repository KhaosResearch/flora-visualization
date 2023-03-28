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

