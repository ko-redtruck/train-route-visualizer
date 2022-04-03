from folium.map import Marker
from folium.utilities import parse_options
from branca.element import MacroElement
from jinja2 import Template


class JavascriptMarker(Marker):
    """Add a Marker in the shape of a boat.
    Parameters
    ----------
    location: tuple of length 2, default None
        The latitude and longitude of the marker.
        If None, then the middle of the map is used.
    heading: int, default 0
        Heading of the boat to an angle value between 0 and 360 degrees
    wind_heading: int, default None
        Heading of the wind to an angle value between 0 and 360 degrees
        If None, then no wind is represented.
    wind_speed: int, default 0
        Speed of the wind in knots.
    https://github.com/thomasbrueggemann/leaflet.boatmarker
    """
    _template = Template(u"""
        {% macro script(this, kwargs) %}
            function markerClick(e){
                console.log(this);
                let name = this._popup._content.innerText.trim()
                
                let url = new URL("http://localhost:5000/");
                url.searchParams.set("start",name);
                console.log(url.href);
                //top because leaflet is loaded in an iFrame
                window.top.location.href = url.href;
                /*fetch("http://localhost:5000/?location="+e.latlng)*/
            }
            var {{ this.get_name() }} = L.marker(
                {{ this.location|tojson }},
                {{ this.options|tojson }}
            ).on("click",markerClick).addTo({{ this._parent.get_name() }});
        {% endmacro %}
        """)

    def __init__(self, location, popup=None, icon=None,**kwargs):
        super().__init__(
            location,
            popup=popup,
            icon=icon
        )
  