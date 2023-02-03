
import holoviews as hv
import panel as pn
import numpy as np
import pandas as pd
import re
import hvplot.pandas
import param
import plotly.graph_objects as go

from holoviews import opts, dim
from panel.template import FastGridTemplate, DarkTheme

df = pd.read_csv("https://raw.githubusercontent.com/elias-abril-f/dashboard-data/main/trips_by_year.csv?token=GHSAT0AAAAAAB5MTXZ6M4E4XFVWULJ3YVTKY65B5FQ", sep=",")
df2 = pd.read_csv("https://raw.githubusercontent.com/elias-abril-f/dashboard-data/main/trips_by_month.csv?token=GHSAT0AAAAAAB5MTXZ6YKKMVLTXWBSMWRVUY65B5UQ", sep=",")
df3 = pd.read_csv("https://raw.githubusercontent.com/elias-abril-f/dashboard-data/main/trips_by_hour.csv?token=GHSAT0AAAAAAB5MTXZ637IWDZIU56OIUFOQY65B57Q", sep=",")
df3["mean"] = df3["trips"].mean()
df4 = pd.read_csv("https://raw.githubusercontent.com/elias-abril-f/dashboard-data/main/trips_by_weekday.csv?token=GHSAT0AAAAAAB5MTXZ7P7HBLZSYD3CKXPLIY65B6OQ", sep=",")
chordData = pd.read_csv("https://raw.githubusercontent.com/elias-abril-f/dashboard-data/main/top10.csv?token=GHSAT0AAAAAAB5MTXZ6I46W7P4H24D3OEYEY65B6VQ")

HEADER_ACCENT = "#1c1c1c"

def _create_barandlinewidget(data, x, main, accent, title="title"):
    class Plot(param.Parameterized):
        column = param.ObjectSelector(default=f"trips({x})", objects=[f"duration({x})", f"trips({x})"])
        
        @param.depends('column')
        def create_plot(self):
            def hooks(plot, element):
                p = plot.state
                p.toolbar.autohide= True
                p.toolbar.logo = None
                if "trips" in self.column:
                    p.yaxis.ticker=[0,2000000,4000000,6000000,8000000]
                    p.yaxis.major_label_overrides={0:"0",2000000:"2M",4000000:"4M",6000000:"6M",8000000:"8M"} 
                else:
                    p.yaxis.ticker = np.arange(0, 1400, 200)
                    p.yaxis.major_label.overrides={0:"0", 200:"200", 400:"400", 600:"600", 800:"800", 1000:"1000",1200:"1200", 1400:"1400"}
    
            
            plot = data.hvplot.bar(x,
                                self.column,
                                color=main,
                                line_color="white",
                                xlabel=str(x).capitalize(),
                                ylabel=re.sub(r"\([a-z,A-Z]*\)","", str(self.column)).capitalize(),
                                responsive=True).opts(hooks=[hooks],legend_position='bottom_right') \
                                * data.hvplot.line(x,
                                                   f"mean{self.column}",
                                                   color=accent,
                                                   line_color="white",
                                                   responsive=True, 
                                                   label="Mean")
            return plot

    plot = Plot()
    dmap = hv.DynamicMap(plot.create_plot)
    return pn.Column(
        pn.Param(plot.param, name=title, show_labels=False, width = 500),
        dmap, sizing_mode="stretch_both")
    
def _create_barandline(data, main, accent, title="Title"):
    
    class Plot(param.Parameterized):        
        def create_plot(self):
            
            def hooks(plot, element):
                p = plot.state
                p.toolbar.autohide = True
                p.toolbar.logo = None
                p.yaxis.ticker=[0,2000000,4000000,6000000,8000000]
                p.yaxis.major_label_overrides={0:"0",2000000:"2M",4000000:"4M",6000000:"6M",8000000:"8M"} 
                
            return data.hvplot(kind="bar",
                            x="time",
                            title=title,
                            y="trips",
                            color=main,
                            xlabel="Hour",
                            line_color="white",
                            responsive=True,
                            min_width=350,
                            min_height=250,
                            ylabel="Trips",
                            label="Trips").opts(legend_position='right', hooks=[hooks]) \
                                * data.hvplot(kind="line",
                                            x="time",
                                            y="mean",
                                            responsive=True,
                                            color = accent, 
                                            line_color="white",
                                            label="Mean")
        def view(self):
            plot = hv.DynamicMap(self.create_plot)
            return plot
        
    p = Plot()
    return pn.Column(p.view, sizing_mode="stretch_both", margin=(-20,0))

def create_map(url, title="title"):
    class Map(param.Parameterized):
        
        data = pd.read_csv(url)
        value = param.Integer(default=97, bounds=(min(data["value"]), 300000))
        
        @param.depends('value')
        def create_map(self):
            def hooks(plot, element):
                p = plot.state
                p.toolbar.autohide= True
                p.toolbar.logo = None
            df = self.data.loc[self.data["value"] >= self.value]
            return df.hvplot.points('lon', 'lat',
                                    geo=True, 
                                    tiles=True, 
                                    hover_cols=["station","value"],
                                    xaxis=None, 
                                    yaxis=None, 
                                    color="#303030",
                                    responsive=True).opts(hooks=[hooks], 
                                                          framewise=True)
        @param.depends("value")
        def view(self):
            return hv.DynamicMap(self.create_map)
    map = Map()
    return pn.Column(
        pn.Param(map.param, name=title, show_labels=False, sizing_mode="stretch_both"),
        map.view, sizing_mode="stretch_both")
    
def createChord():
    from bokeh.models import HoverTool
    from bokeh.plotting import ColumnDataSource
    links = chordData[["source_id", "target_id", "value"]]
    
    def hooks(plot, element):
        p = plot.state
        p.toolbar.logo = None
        p.toolbar.autohide=True
  
    nodes = hv.Dataset(pd.DataFrame(
    [{'index': 0,'name': "Hyde Park Corner, Hyde Park"},
    {'index': 1,'name': "Albert Gate, Hyde Park"},
    {'index': 2,'name': "Triangle Car Park, Hyde Park"},
    {'index': 3,'name': "Black Lion Gate, Kensington Gardens"},
    {'index': 4,'name': "Serpentine Car Park, Hyde Park"},
    {'index': 5,'name': "Park Lane , Hyde Park"},
    {'index': 6,'name': "Queen's Gate, Kensington Gardens"},
    {'index': 7,'name': "Palace Gate, Kensington Gardens"},
    {'index': 8,'name': "Bayswater Road, Hyde Park"},
    {'index': 9,'name': "Wellington Arch, Hyde Park"},
    {'index': 10,'name': "Red Lion Street, Holborn"},
    {'index': 11,'name': "Soho Square , Soho"},
    {'index': 12,'name': "Holborn Circus, Holborn"},
    {'index': 13,'name': "Wren Street, Holborn"},
    {'index': 14,'name': "Great Marlborough St, Soho"},
    {'index': 15,'name': "Bayley Street , Bloomsbury"},
    {'index': 16,'name': "Guilford Street , Bloomsbury"},
    {'index': 17,'name': "Newgate Street , St. Paul's"},
    {'index': 18,'name': "Theobald's Road , Holborn"},
    {'index': 19,'name': "British Museum, Bloomsbury"},
    {'index': 20,'name': "Godliman Street, St. Paul's"},
    {'index': 21,'name': "Queen Victoria Street, St. Paul's"},
    {'index': 22,'name': "Queen Street 2, Bank"},
    {'index': 23,'name': "Wormwood Street, Liverpool Street"},
    {'index': 24,'name': "Queen Street 1, Bank"},
    {'index': 25,'name': "Finsbury Circus, Liverpool Street"},
    {'index': 26,'name': "St. Bride Street, Holborn"},
    {'index': 27,'name': "Cheapside, Bank"},
    {'index': 28,'name': "Moorfields, Moorgate"},
    {'index': 29,'name': "Speakers' Corner 1, Hyde Park"},
    {'index': 30,'name': "Exhibition Road, Knightsbridge"},
    {'index': 31,'name': "Hop Exchange, The Borough"},
    {'index': 32,'name': "Bankside Mix, Bankside"},
    {'index': 33,'name': "Storey's Gate, Westminster"},
    {'index': 34,'name': "Craven Street, Strand"},
    {'index': 35,'name': "Green Park Station, Mayfair"},
    {'index': 36,'name': "Stamford Street, South Bank"},
    {'index': 37,'name': "Waterloo Station 1, Waterloo"},
    {'index': 38,'name': "Milroy Walk, South Bank"},
    {'index': 39,'name': "Lavington Street, Bankside"},
    {'index': 40,'name': "Poured Lines, Bankside"},
    {'index': 41,'name': "Baylis Road, Waterloo"},
    {'index': 42,'name': "Waterloo Station 3, Waterloo"},
    {'index': 43,'name': "Duke Street Hill, London Bridge"},
    {'index': 44,'name': "Whitehall Place, Strand"},
    {'index': 45,'name': "Tooley Street, Bermondsey"},
    {'index': 46,'name': "Tate Modern, Bankside"},
    {'index': 47,'name': "Waterloo Station 2, Waterloo"},
    {'index': 48,'name': "Belgrove Street , King's Cross"}]), 'index')
    
    plot = hv.Chord((links,nodes), ).select(value=(5, None)).opts(cmap='Pastel1',
                                                                  edge_cmap='Pastel1',
                                                                  edge_color=dim('source_id').str(),
                                                                  node_color=dim('index').str(),
                                                                  responsive=True, 
                                                                  hooks=[hooks], 
                                                                  title="Most popular stations and their most popular trips",#labels="name",
                                                                  label_text_color="white",
                                                                  legend_position = "right")
    
    return pn.Column(plot, sizing_mode="stretch_both")

def get_app():
    template = FastGridTemplate(
        title="London TFL Bike Journeys Dashboard",
        row_height=55,
        prevent_collision=True,
        save_layout=True,
        accent_base_color=HEADER_ACCENT,
        header_background=HEADER_ACCENT,
        theme=DarkTheme,
        theme_toggle=False,
        sidebar = [pn.pane.Markdown("# **INSTRUCTIONS**\n- All the panels are fully resoponsive. You can move them and resize them and their content adapts to the new size\n\n- Click and drat a panel from the top left corner to move it. \n\n- Collitions as diabled to avoid panels jumping all over the place. Move a panel out of the way before attempting to move another one into that spot. \n\n- Click and drag the bottom right corner to resize a panel.\n\n- If you press the top right corner you can see that panel fullscreen\n\n- Click the hamburger menu in the header to close the sidebar and enjoy the dashboard full size. \n\n- In the right end of the header you have 2 icons. The first one reset the layout and the second one is the activity indicator")]
    )
    template.main[ :8, :6] = create_map("https://raw.githubusercontent.com/elias-abril-f/dashboard-data/main/stations_start.csv", title="Docks and total amount of trips started from them. Move the slider to filter.")
    template.main[:7, 6:12] = _create_barandlinewidget(df2, x="month", main = "#FFD289", accent = "#FACC6B", title="Trips and their average duration by month")
    template.main[7:8, 6:12] = pn.pane.Markdown("      # Total Trips: 76450245",style={"margin-top":"-30px", "padding":"0,0,0,0"}, width=400, height=0, )
    template.main[8:13, 0:12] = _create_barandline(data=df3, main="#78C0E0", accent="#449DD1", title="Trips by time of day")
    template.main[13:19, 0:5] = _create_barandlinewidget(data=df, x="year", main="#EFC3E6", accent="#9C89B8", title="Trips and their average duration by year")
    template.main[19:20,0:5] = pn.Row(pn.pane.Markdown("#    🚴🚴🚴   Over 800 Docks   🚴🚴🚴",style={"margin-top": "-25px"}, width=400, height=10), scroll=False)
    template.main[21:31, 0:12] = pn.Column(pn.pane.Markdown("## Explore a dataset. Change the settings, kind of graph, axis, labels... and see the results live!"),hvplot.explorer(df4))
    template.main[13:21, 5:12] = createChord()
    template.main[40:40, 0:12] = pn.Spacer()
    return template

if __name__.startswith("bokeh"):
    get_app().servable()

