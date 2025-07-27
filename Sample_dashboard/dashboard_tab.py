from plotly.graph_objs._figure import Figure
import streamlit.delta_generator
from Backend.backend_codebase import *
import streamlit, pandas, shelve, random
from typing import Generator, Any
import plotly.express as pxs

def dashboard_tab_function() -> None:

    #-------------------------------------------------------
    # Access shelved data and css styles
    #-------------------------------------------------------

    try:
        with shelve.open("shelved_sample_data") as db:
            inventory_report: pandas.DataFrame = db["inventory_report"]
            mdm_report: pandas.DataFrame = db["mdm_report"]
            data_as_of: str = db["data_as_of"]
            try:
                kpi_dashboard_source_data: pandas.DataFrame = db["kpi_dataframe"]
            except KeyError:
                kpi_dashboard_source_data: pandas.DataFrame = pandas.DataFrame()
    except KeyError:
        inventory_report: pandas.DataFrame = pandas.DataFrame()
        mdm_report: pandas.DataFrame = pandas.DataFrame()
        kpi_dashboard_source_data: pandas.DataFrame = pandas.DataFrame()
        data_as_of: str = ""

    # Read CSS file
    with open("styles.css") as file:
        # get classes
        css_styles: str = f"<style>{file.read()}</style>"
        # inject classes into DOM of streamlit frontend
        streamlit.markdown(css_styles, unsafe_allow_html=True)


    #-------------------------------------------------------
    # Functions
    #-------------------------------------------------------

    def create_breakeven_point_graph(sku: Material_SKU) -> Figure:
        if sku.break_even_point_in_units_for_holding_inventory < sku.units_sold_in_period:
            max_units_for_graph: int = round(sku.units_sold_in_period * 1.5)
        else:
            max_units_for_graph: int = round(sku.break_even_point_in_units_for_holding_inventory * 1.5)

        # Generate unit quantities
        unit_quantities_for_profit_line: list = list(range(0, max_units_for_graph))

        # Generate values for plotting each line
        dollar_values_for_cost_line: list = [(sku.avg_monthly_holding_cost_of_inv) + (unit_quantity * 0) for unit_quantity in unit_quantities_for_profit_line]
        dollar_values_for_revenue_line: list = [sku.contribution_per_unit_in_dollars * unit_quantity for unit_quantity in unit_quantities_for_profit_line]

        dataframe: pandas.DataFrame = pandas.DataFrame({
            "Units": unit_quantities_for_profit_line,
            "Holding Cost": dollar_values_for_cost_line,
            "Profit": dollar_values_for_revenue_line,
        })

        # Melt dataframe for Plotly Express
        melted_dataframe: pandas.DataFrame = dataframe.melt(
            id_vars="Units", 
            value_vars=["Holding Cost", "Profit"],
            var_name="Metric", 
            value_name="Amount",
        )

        # Plot
        figure: Figure = pxs.line(
            melted_dataframe,
            x="Units", 
            y="Amount",
            color="Metric",
            color_discrete_map={
                "Total Cost": "#D43356",
                "Total Revenue": "#1336D1"
            },
            labels={"Units": f"Inventory Units ({sku.inventory_uom})", "Amount": "USD ($)"},

        )

        # Sytlize
        figure.update_layout(
            margin=dict(t=30, b=60, l=60, r=60),  # top, bottom, left, right
            legend_title=dict(
                text="METRIC",
            ),
            title=dict(
                text="Break-Even on Holding Cost",
                x=0.5, 
                xanchor="center"
            ),
            # xaxis = dict(range = [0, max_units_for_graph]),

        )
        return figure

    def material_generator(all_skus: set) -> Generator[dict]:
        for sku in all_skus:
            material_sku: Material_SKU = Material_SKU(sku)
            dict_of_kpis: dict = material_sku.get_KPIs_attrs()
            yield dict_of_kpis

    def create_pie_charts_for_metrics(
            name_of_ordered_elements: list,
            values_of_ordered_elements: list,
            title_of_graph: str,
            color_map: dict,
        ) -> Figure:
        data: dict =  {
            "Names": name_of_ordered_elements,
            "values": values_of_ordered_elements,
        }
        dataframe: pandas.DataFrame = pandas.DataFrame(data)
        
        # Create pie chart
        figure: Figure = pxs.pie(
            dataframe,
            names="Names",
            values="values",
            hole=0.5,  # Optional: creates a donut-style chart
            color="Names",  # This tells Plotly to use the color map
            color_discrete_map=color_map,

        )
        
        # Stylize
        figure.update_traces(
            # textposition="inside", 
            textinfo="percent+label",
        )
        
        # Stylize more
        figure.update_layout(
            showlegend=False,
            margin=dict(t=60, b=40, l=20, r=20),  # top, bottom, left, right
            title = {
                "text": title_of_graph,
                "x": 0.5, # center title
                "xanchor": "center", # anchor the title at its center

            },
            )

        return figure


    #-------------------------------------------------------
    # User Interface
    #-------------------------------------------------------
    streamlit.title("Inventory Planning Performance Dashboard", anchor=False)

    overview_tab, sku_tab = streamlit.tabs(["KPI Oversight - Prior Month","Plan Performance by SKU - Prior Month"])

    with overview_tab:
        overview_tab_row_1_column_1, overview_tab_row_1_column_2, overview_tab_row_1_column_3 = streamlit.columns([1,1,1])
        overview_tab_row_2_column_1, overview_tab_row_2_column_2, overview_tab_row_2_column_3 = streamlit.columns([1,1,1])
        overview_tab_row_3_column_1, overview_tab_row_3_column_2,overview_tab_row_3_column_3 = streamlit.columns([1,100,1])
        overview_tab_row_4_column_1, overview_tab_row_4_column_2, overview_tab_row_4_column_3 = streamlit.columns([1,1,1])

        if overview_tab_row_1_column_3.button("Recalculate KPIs"):
            set_of_all_skus:set = set(mdm_report["Product ID"])
            # Calulate and yield results into a dataframe 
            kpi_dataframe: pandas.DataFrame = pandas.DataFrame(material_generator(set_of_all_skus))
            # Store locally
            with shelve.open("shelved_sample_data") as db:
                db["kpi_dataframe"] = kpi_dataframe
            overview_tab_row_1_column_3.success("Calculations are complete. Please reload the page.")
        if kpi_dashboard_source_data.empty:
            overview_tab_row_1_column_3.info("Click me! :point_up_2:")
        else:    
            number_of_rows_in_data: int = len(kpi_dashboard_source_data.index)
            dataframe_of_haz_materials: pandas.DataFrame = kpi_dashboard_source_data.loc[kpi_dashboard_source_data["Is Hazardous?"] == True]
            sum_turnover: float = kpi_dashboard_source_data["Inventory Turnover Ratio"].sum()
            avg_inventory_turnover: float = round(sum_turnover / number_of_rows_in_data, 2)
            total_profit_in_period: float = round(kpi_dashboard_source_data["Profit Contribution During the Period ($)"].sum(), 2)
            total_revenue_in_period: float = round(kpi_dashboard_source_data["Total Revenue by SKU in Period ($)"].sum(), 2)
            pre_tax_profit_margin_in_period_as_percentage: float = round((total_profit_in_period / total_revenue_in_period) * 100, 2)
            with overview_tab_row_1_column_1.container(border=True):
                streamlit.subheader(f"Inventory Turnover Ratio: :green[{avg_inventory_turnover} turns per year]", anchor=False)
            with overview_tab_row_1_column_2.container(border=True):
                streamlit.subheader(f"Total Profit (Pre-tax): :green[${total_profit_in_period:,}] (Margin: :green[{pre_tax_profit_margin_in_period_as_percentage}%])", anchor=False)

            with overview_tab_row_2_column_1.container(border=True):
                number_of_hazardous_materials: int = len(dataframe_of_haz_materials.index)
                number_of_nonhazardous_materials: int = number_of_rows_in_data - number_of_hazardous_materials
                name_of_ordered_haz_elements: list = ["Non-Hazardous Materials", "Hazardous Materials"]
                values_of_ordered_haz_elements: list = [number_of_nonhazardous_materials, number_of_hazardous_materials]
                color_map_of_haz_elements: dict = {
                    "Non-Hazardous Materials": "#575757",
                    "Hazardous Materials": "#E2E2E2"
                }
                haz_figure_for_plotting: Figure = create_pie_charts_for_metrics(
                    name_of_ordered_haz_elements,
                    values_of_ordered_haz_elements,
                    "Hazardous vs Non-Hazardous",
                    color_map_of_haz_elements
                )
                streamlit.plotly_chart(haz_figure_for_plotting, use_container_width=True)
            with overview_tab_row_2_column_2.container(border=True):
                total_cubic_feet_utilized: float = round(kpi_dashboard_source_data["AVG Cubic Feet Utilized During the Period"].sum(), 3)
                cubic_feet_utilized_for_haz_materials: float = round(dataframe_of_haz_materials["AVG Cubic Feet Utilized During the Period"].sum(), 1)
                cubic_feet_utilized_for_nonhaz_materials: float = round(total_cubic_feet_utilized - cubic_feet_utilized_for_haz_materials, 1)
                name_of_ordered_haz_storage_elements: list = ["Cubic Feet Non-Hazardous Storage", "Cubic Feet Hazardous Storage"]
                values_of_ordered_haz_storage_elements: list = [cubic_feet_utilized_for_nonhaz_materials, cubic_feet_utilized_for_haz_materials]
                color_map_of_haz_storage_elements: dict = {
                    "Cubic Feet Non-Hazardous Storage": "#575757",
                    "Cubic Feet Hazardous Storage": "#E2E2E2"
                }
                haz_storage_figure_for_plotting: Figure = create_pie_charts_for_metrics(
                    name_of_ordered_haz_storage_elements,
                    values_of_ordered_haz_storage_elements,
                    "Cubic Feet of Hazardous Storage",
                    color_map_of_haz_storage_elements
                )
                streamlit.plotly_chart(haz_storage_figure_for_plotting, use_container_width=True)
            with overview_tab_row_2_column_3.container(border=True):
                number_of_materials_at_risk_of_expiry: int = len(kpi_dashboard_source_data.loc[kpi_dashboard_source_data["High Risk of Stock Expiry"] == True].index)
                number_of_materials_not_at_risk_of_expiry: int = number_of_rows_in_data - number_of_materials_at_risk_of_expiry
                name_of_ordered_expiry_elements: list = ["Non-expiring Materials", "Expiring Materials"]
                values_of_ordered_expiry_elements: list = [number_of_materials_not_at_risk_of_expiry, number_of_materials_at_risk_of_expiry]
                color_map_of_expiry_elements: dict = {
                    "Non-expiring Materials": "#575757",
                    "Expiring Materials": "#E2E2E2"
                }
                expiry_figure_for_plotting: Figure = create_pie_charts_for_metrics(
                    name_of_ordered_expiry_elements,
                    values_of_ordered_expiry_elements,
                    "Materials at Risk of Expiry",
                    color_map_of_expiry_elements
                )
                streamlit.plotly_chart(expiry_figure_for_plotting, use_container_width=True)
            with overview_tab_row_3_column_2.container(border=True):
                streamlit.markdown("<p style='text-align: center; color: orange; font-size: 36px; font-weight: bold;'> Materials Spotlight </p>", unsafe_allow_html=True)
            with overview_tab_row_4_column_1.container(border=True):
                streamlit.markdown("<p style='text-align: center; color: #009C0D; font-size: 28px; font-weight: bold;'> Top Performers </p>", unsafe_allow_html=True)
                #----------------------------------------
                # HIGHEST NOMINAL PROFIT
                #----------------------------------------
                highest_nominal_profit: int = kpi_dashboard_source_data["Profit Contribution During the Period ($)"].max()
                df_for_highest_nom_profit: pandas.DataFrame = kpi_dashboard_source_data.loc[kpi_dashboard_source_data["Profit Contribution During the Period ($)"] == highest_nominal_profit]
                prod_descr_of_highest_nom_prof: str = set(df_for_highest_nom_profit["Material Description"]).pop()
                prod_id_of_highest_nom_prof: str = set(df_for_highest_nom_profit["Material ID"]).pop()
                #----------------------------------------
                # HIGHEST (PRETAX) PROFIT MARGIN
                #----------------------------------------
                highest_profit_margin: int = kpi_dashboard_source_data["Profit Margin by SKU as Percentage"].max()
                df_for_highest_profit_margin: pandas.DataFrame = kpi_dashboard_source_data.loc[kpi_dashboard_source_data["Profit Margin by SKU as Percentage"] == highest_profit_margin]
                prod_descr_of_highest_prof_margin: str = set(df_for_highest_profit_margin["Material Description"]).pop()
                prod_id_of_highest_prof_margin: str = set(df_for_highest_profit_margin["Material ID"]).pop()
                #----------------------------------------
                # HIGHEST INVENTORY TURNOVER (i.e. FASTEST MOVER)
                #----------------------------------------
                highest_inv_turnover: int = kpi_dashboard_source_data["Inventory Turnover Ratio"].max()
                df_for_highest_inv_turnover: pandas.DataFrame = kpi_dashboard_source_data.loc[kpi_dashboard_source_data["Inventory Turnover Ratio"] == highest_inv_turnover]
                prod_descr_of_highest_inv_turnover: str = set(df_for_highest_inv_turnover["Material Description"]).pop()
                prod_id_of_highest_inv_turnover: str = set(df_for_highest_inv_turnover["Material ID"]).pop()

                streamlit.markdown(f"**HIGHEST NOMINAL PROFIT: (:blue[{prod_id_of_highest_nom_prof}]) :blue[{prod_descr_of_highest_nom_prof}] (:orange[${highest_nominal_profit}])**")
                streamlit.markdown(f"**HIGHEST (PRETAX) PROFIT MARGIN:  (:blue[{prod_id_of_highest_prof_margin}]) :blue[{prod_descr_of_highest_prof_margin}] (:orange[{highest_profit_margin}%])**")
                streamlit.markdown(f"**FASTEST MOVER: (:blue[{prod_id_of_highest_inv_turnover}]) :blue[{prod_descr_of_highest_inv_turnover}] (Rate of :orange[{highest_inv_turnover} turns per year])**")
            
            with overview_tab_row_4_column_2.container(border=True):
                streamlit.markdown("<p style='text-align: center; font-size: 28px;'> Recommended for Promotion </p>", unsafe_allow_html=True)
                dataframe_of_promo_recommendations: pandas.DataFrame = kpi_dashboard_source_data.loc[kpi_dashboard_source_data["High Risk of Stock Expiry"] == True]
                parts_recommended_for_promo: tuple = tuple(dataframe_of_promo_recommendations["Material ID"])
                descriptions_of_parts_recommended_for_promo: tuple = tuple(dataframe_of_promo_recommendations["Material Description"])
                for index in range(len(parts_recommended_for_promo)):
                    streamlit.markdown(f"<p style='text-align: center; font-size: 20px;'> ({parts_recommended_for_promo[index]}) {descriptions_of_parts_recommended_for_promo[index]} </p>", unsafe_allow_html=True)

            with overview_tab_row_4_column_3.container(border=True):
                streamlit.markdown("<p style='text-align: center; color: #CCC92B; font-size: 28px; font-weight: bold;'> Lowest Performers </p>", unsafe_allow_html=True)
                #----------------------------------------
                # LOWEST NOMINAL PROFIT
                #----------------------------------------
                lowest_nominal_profit: int = kpi_dashboard_source_data["Profit Contribution During the Period ($)"].min()
                df_for_lowest_nom_profit: pandas.DataFrame = kpi_dashboard_source_data.loc[kpi_dashboard_source_data["Profit Contribution During the Period ($)"] == lowest_nominal_profit]
                prod_descr_of_lowest_nom_prof: str = set(df_for_lowest_nom_profit["Material Description"]).pop()
                prod_id_of_lowest_nom_prof: str = set(df_for_lowest_nom_profit["Material ID"]).pop()
                #----------------------------------------
                # LOWEST (PRETAX) PROFIT MARGIN
                #----------------------------------------
                lowest_profit_margin: int = kpi_dashboard_source_data["Profit Margin by SKU as Percentage"].min()
                df_for_lowest_profit_margin: pandas.DataFrame = kpi_dashboard_source_data.loc[kpi_dashboard_source_data["Profit Margin by SKU as Percentage"] == lowest_profit_margin]
                prod_descr_of_lowest_prof_margin: str = set(df_for_lowest_profit_margin["Material Description"]).pop()
                prod_id_of_lowest_prof_margin: str = set(df_for_lowest_profit_margin["Material ID"]).pop()
                #----------------------------------------
                # LOWEST INVENTORY TURNOVER (i.e. FASTEST MOVER)
                #----------------------------------------
                lowest_inv_turnover: int = kpi_dashboard_source_data["Inventory Turnover Ratio"].min()
                df_for_lowest_inv_turnover: pandas.DataFrame = kpi_dashboard_source_data.loc[kpi_dashboard_source_data["Inventory Turnover Ratio"] == lowest_inv_turnover]
                prod_descr_of_lowest_inv_turnover: str = set(df_for_lowest_inv_turnover["Material Description"]).pop()
                prod_id_of_lowest_inv_turnover: str = set(df_for_lowest_inv_turnover["Material ID"]).pop()

                streamlit.markdown(f"**LOWEST NOMINAL PROFIT: (:blue[{prod_id_of_lowest_nom_prof}]) :blue[{prod_descr_of_lowest_nom_prof}] (:orange[${lowest_nominal_profit}])**")
                streamlit.markdown(f"**LOWEST (PRETAX) PROFIT MARGIN:  (:blue[{prod_id_of_lowest_prof_margin}]) :blue[{prod_descr_of_lowest_prof_margin}] (:orange[{lowest_profit_margin}%])**")
                streamlit.markdown(f"**SLOWEST MOVER: (:blue[{prod_id_of_lowest_inv_turnover}]) :blue[{prod_descr_of_lowest_inv_turnover}] (Rate of :orange[{lowest_inv_turnover} turns per year])**")
            with streamlit.container(border=True):
                streamlit.markdown("<p style='text-align: center; color: orange; font-size: 36px; font-weight: bold;'> Raw KPI Data </p>", unsafe_allow_html=True)
            streamlit.dataframe(kpi_dashboard_source_data)





    with sku_tab:

        sku_tab_row_1_column_1, sku_tab_row_1_column_2 = streamlit.columns([15,100])
        sku_tab_row_2_column_1, sku_tab_row_2_column_2, sku_tab_row_2_column_3 = streamlit.columns([1,1,1])
        sku_tab_row_3_column_1, sku_tab_row_3_column_2 = streamlit.columns([1,1])
        sku_tab_row_4_column_1, sku_tab_row_4_column_2, sku_tab_row_4_column_3 = streamlit.columns([1,1,1])

        sku_list: tuple[str] = tuple(set(inventory_report["Product ID"]))

        if sku_tab_row_1_column_1.container(border=False, height=65).button("Load SKU"):
            if sku_list:
                sku_selection: str = random.choice(sku_list)
            else:
                sku_selection: str = ""
            
            if sku_selection:
                sku_classed: Material_SKU = Material_SKU(sku_selection)
                if sku_classed.is_hazardous:
                    with sku_tab_row_1_column_2.container(border=False, height=65):
                        streamlit.warning(f"**Hazardous Classification:** :blue[**{sku_classed.hazardous_classification}**]")

                with sku_tab_row_2_column_1.container(border=True):
                    streamlit.subheader("*:green[Product Identity]*", anchor=False)
                    streamlit.markdown(f"**Material ID: :blue[{sku_classed.sku}]**")
                    streamlit.markdown(f"**Material Description: :orange[{sku_classed.material_description}]**")
                    streamlit.markdown(f"**Manufacturer: :blue[{sku_classed.manufacturer}]**")
                    streamlit.markdown(f"**Manufacturer Part Number: :blue[{sku_classed.manufacturer_part_number}]**")
                
                with sku_tab_row_2_column_2.container(border=True):
                    if (
                        sku_classed.inv_turnover_ratio
                        and sku_classed.days_of_supply
                        and sku_classed.years_of_supply
                    ):
                        streamlit.subheader("*:green[Inventory Efficiency]*", anchor=False)
                        streamlit.markdown(f"**Inventory Turnover Ratio: :blue[{sku_classed.inv_turnover_ratio}] turns per year**")
                        streamlit.markdown(f"**Years of Supply: :blue[{sku_classed.years_of_supply} years]** | :grey[({sku_classed.days_of_supply} days of supply)]")
                        streamlit.markdown(f"**AVG remaining shelf life of product when sold: :blue[{(round(sku_classed.shelf_life - sku_classed.years_of_supply, 1))} years]**")
                        streamlit.markdown(f"**AVG Holding Cost of INV Per Month: :blue[${sku_classed.avg_monthly_holding_cost_of_inv}]**")
                
                with sku_tab_row_2_column_3.container(border=True):
                    streamlit.subheader("*:green[Change From Prior Month]*", anchor=False)
                    streamlit.markdown(f"**Net change in total stock level:** :blue[**{sku_classed.net_change_in_inv_qty_over_period} {sku_classed.inventory_uom}**]")
                    percentage_change_in_inv: float = round((sku_classed.net_change_in_inv_qty_over_period / sku_classed.beginning_inv_qty)* 100, 1)
                    if percentage_change_in_inv > 0:
                        status: str = "increased"
                    elif percentage_change_in_inv == 0:
                        status: str = "changed"
                    else:
                        status: str = "decreased"

                    streamlit.markdown(f"**Net stock level :blue[{status} {abs(percentage_change_in_inv)}%] over the period**")
                        
                with sku_tab_row_3_column_1.container(border=True):
                    break_even_container_row_1_column_1, break_even_container_row_1_column_2 = streamlit.columns([1,1])
                    breakeven_graph: Figure = create_breakeven_point_graph(sku_classed)
                    break_even_container_row_1_column_1.markdown(f"**Break-even point for the month: :blue[{sku_classed.break_even_point_in_units_for_holding_inventory} {sku_classed.inventory_uom}]**")
                    break_even_container_row_1_column_1.markdown(f"**Units sold in the month: :blue[{sku_classed.units_sold_in_period} {sku_classed.inventory_uom}]**")
                    break_even_container_row_1_column_2.markdown(f"**Beginning Stock: :blue[{sku_classed.beginning_inv_qty} {sku_classed.inventory_uom}]**")
                    break_even_container_row_1_column_2.markdown(f"**Ending Stock: :blue[{sku_classed.ending_inv_qty} {sku_classed.inventory_uom}]**")
                    streamlit.plotly_chart(breakeven_graph, use_container_width=True)

                with sku_tab_row_3_column_2.container(border=True):
                    if sku_classed.stock_expiry_is_a_high_risk:
                        streamlit.info("**Promotion is recommended due to aging inventory**")
                    streamlit.subheader(f"Total Profit Contribution Last Month: :orange[${sku_classed.total_profit_contribution_in_period}]", anchor=False)
                    streamlit.subheader(f"Pre-tax margin: :orange[{sku_classed.pretax_profit_margin_as_percentage}%]")


