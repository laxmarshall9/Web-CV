from plotly.graph_objs._figure import Figure
import streamlit.delta_generator
from Backend.backend_codebase import *
import streamlit, pandas, shelve, random
from typing import Generator, Any
import plotly.express as pxs

def dashboard_tab_function() -> None:

    #-------------------------------------------------------
    # Access shelved data
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





    #-------------------------------------------------------
    # User Interface
    #-------------------------------------------------------
    streamlit.title("Planning Dashboard", anchor=False)

    overview_tab, sku_tab = streamlit.tabs(["KPI Oversight","Plan Performance by SKU"])

    with overview_tab:
        overview_tab_row_1_column_1, overview_tab_row_1_column_2, overview_tab_row_1_column_3 = streamlit.columns([1,1,1])
        overview_tab_row_2_column_1, overview_tab_row_2_column_2, overview_tab_row_2_column_3 = streamlit.columns([1,1,1])
        overview_tab_row_3_column_1, overview_tab_row_3_column_2, overview_tab_row_3_column_3 = streamlit.columns([1,1,1])

        if overview_tab_row_1_column_3.button("Recalculate KPIs"):
            set_of_all_skus:set = set(mdm_report["Product ID"])
            # Calulate and yield results into a dataframe 
            kpi_dataframe: pandas.DataFrame = pandas.DataFrame(material_generator(set_of_all_skus))
            # Store locally
            with shelve.open("shelved_sample_data") as db:
                db["kpi_dataframe"] = kpi_dataframe
            streamlit.success("Calculations are complete. Please reload the page.")
        if kpi_dashboard_source_data.empty:
            overview_tab_row_1_column_3.info("Click me! :point_up_2:")
        else:    
            
            
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
                    streamlit.subheader("*:green[Change Over Prior Month]*", anchor=False)
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


