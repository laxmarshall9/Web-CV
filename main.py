from plotly.graph_objs._figure import Figure
import streamlit, sys, base64
import plotly.express as pxs
from streamlit import runtime
from streamlit.web import cli as stcli
from streamlit.navigation.page import StreamlitPage
from streamlit_timeline import timeline
from Intro_tab.intro_tab import intro_tab_function as intro_tab_func

def main_func() -> None:
    # Reduce left and right margins of the page
    streamlit.set_page_config(layout="wide")
    streamlit.title("James Marshall, CSCP", anchor = False)

    def introduction() -> None:
        intro_tab_func()

    def professional_history() -> None:        
        # get data
        with open('resume_source.json', "r") as file:
            data: str = file.read()

        # render timeline
        timeline(data, height=600)

    # Create tabs and link each to their respective function
    all_pages: StreamlitPage = streamlit.navigation([
        streamlit.Page(introduction, title="Introduction"), 
        streamlit.Page(professional_history, title="Career Timeline")])

    all_pages.run()

    #-----------------------------------------------------------------------------------------

    skills: list[str] = ["Data Analysis", "Excel", "ERP Systems", "Python", "E2E Supply Chain" ]
    proficiency: list[int] = [90, 90, 80, 65, 80]

    figure: Figure = pxs.bar(
        x=proficiency, y=skills, orientation="h",
        labels={"x": "Proficiency (%)", "y": ""},
        text=proficiency, color=proficiency,
        color_continuous_scale="ice" # color options -> https://plotly.com/python/builtin-colorscales/

    )
    figure.update_layout( 
        # Font options and formatting. Reference: https://plotly.com/python/figure-labels/ 
        # "Arial"
        # "Arial Black"
        # "Verdana"
        # "Tahoma"
        # "Trebuchet MS"
        # "Georgia"
        # "Times New Roman"
        # "Courier New"
        # "Lucida Console"
        # "Comic Sans MS"
        # "Helvetica" (Mac-friendly)
        # "Open Sans" (Plotly’s default, if installed)
        showlegend=False, 
        coloraxis_showscale=False,
        yaxis=dict(tickfont=dict(family="Tahoma", size=14)), # Font for y-axis label
        xaxis=dict( 
            showticklabels=False,
            showgrid=False,
            title_font=dict(family="Tahoma", size=14) # Font for x-axis label
        ),
        font=dict(   # For the integer values within the bar chart
            family="Tahoma",
            size=12
        )

        )

    figure.update_traces(
        hoverinfo = "skip",
        hovertemplate=None

    ) 

    streamlit.sidebar.subheader(":orange[SKILLS]", anchor=False)
    streamlit.sidebar.plotly_chart(
        figure, 
        use_container_width=True,
        config={"displayModeBar": False}
        
    )

    def get_image_as_base64(path: str) -> str:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode() # Encode into Bytes object then convert into UTF-8 string

    with streamlit.sidebar:
        linked_in_logo_base64: str = get_image_as_base64("InLogoWhite.png") 
        streamlit_logo_base64: str = get_image_as_base64("streamlit-logo-primary-lightmark-lighttext.png") 

        streamlit.markdown(f"""App created using: 
            <a href="https://streamlit.io/" target="_blank">
                <img src="data:image/png;base64,{streamlit_logo_base64}" width="100" />
            </a>
            """,
            unsafe_allow_html=True
        )
        streamlit.markdown(f"""View my LinkedIn Profile: 
            <a href="https://www.linkedin.com/in/james-marshall-cscp-6107bb188/" target="_blank">
                <img src="data:image/png;base64,{linked_in_logo_base64}" width="25" />
            </a>
            """,
            unsafe_allow_html=True
        )

                           

                           
    streamlit.logo(
    "https://streamlit.io/images/brand/streamlit-mark-light.png",
    link="https://streamlit.io",
    size="small"
)


if __name__ == "__main__":
    if runtime.exists():
        main_func()
    else:
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())







