import shelve, pandas, datetime, random

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Access shelved data
try:
    with shelve.open("shelved_sample_data") as db:
        inventory_report: pandas.DataFrame = db["inventory_report"]
        mdm_report: pandas.DataFrame = db["mdm_report"]
        data_as_of: str = db["data_as_of"]
except KeyError:
    inventory_report: pandas.DataFrame = pandas.DataFrame()
    mdm_report: pandas.DataFrame = pandas.DataFrame()
    data_as_of: str = ""

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Material_SKU():
    """
    This class manages the various data attributes and functions required to analyze SKU-level insights in the Sample Dashboard.

    ### The following attributes are available in this class:
        
        self.sku: str
        self.material_description: str
        self.manufacturer: str
        self.manufacturer_part_number: str
        self.supplier: str
        self.supplier_part_number: str
        self.inventory_uom: str
        self.hazardous_classification: str
        self.shelf_life: int
        self.dim_weight: float
        self.dim_length: float
        self.dim_width: float
        self.dim_height: float
        self.material_creation_date: datetime.date|None
        self.is_hazardous: bool|None
        self.beginning_inv_value: float
        self.ending_inv_value: float
        self.inv_value_per_unit: float
        self.units_sold_in_period: int
        self.units_received_in_period: int
        self.beginning_inv_qty: int
        self.ending_inv_qty: int
        self.avg_inventory_qty_in_period: float
        self.inv_turnover_ratio: float|None
        self.days_of_supply: int|None
        self.years_of_supply: float|None
        self.cubic_feet_required_per_unit: float
        self.avg_cubic_feet_utilized_in_period: float
        self.avg_monthly_holding_cost_of_inv: float
        self.sales_price_per_unit: float
        self.break_even_point_in_units_for_holding_inventory: float
        self.avg_remaining_shelf_life_of_prod_when_sold: float|None
        self.stock_expiry_is_a_high_risk: bool|None
        self.total_profit_contribution_in_period: int

    """

    def __init__(self, sku: str) -> None:
        self.sku: str = sku
        self.set_mdm_attrs()
        self.retrieve_inv_attrs()
        self.get_inv_turnover()

    def __repr__(self) -> str:
        attrs: str = f"""
        sku: str..............................................{self.sku}\n
        material_description: str.............................{self.material_description}\n
        manufacturer: str.....................................{self.manufacturer}\n
        manufacturer_part_number: str.........................{self.manufacturer_part_number}\n
        supplier: str.........................................{self.supplier}\n
        supplier_part_number: str.............................{self.supplier_part_number}\n
        inventory_uom: str....................................{self.inventory_uom}\n
        hazardous_classification: str.........................{self.hazardous_classification}\n
        shelf_life: int.......................................{self.shelf_life}\n
        dim_weight: float.....................................{self.dim_weight}\n
        dim_length: float.....................................{self.dim_length}\n
        dim_width: float......................................{self.dim_width}\n
        dim_height: float.....................................{self.dim_height}\n
        material_creation_date: datetime.date|None............{self.material_creation_date}\n
        is_hazardous: bool|None: bool|None....................{self.is_hazardous}\n
        inv_turnover_ratio: float|None........................{self.inv_turnover_ratio}\n
        days_of_supply: int|None..............................{self.days_of_supply}\n
        years_of_supply: float|None...........................{self.years_of_supply}\n
        beginning_inv_value: float............................{self.beginning_inv_value}\n
        ending_inv_value: float...............................{self.ending_inv_value}\n
        inv_value_per_unit: float.............................{self.inv_value_per_unit}\n
        units_sold_in_period: float...........................{self.units_sold_in_period}\n
        units_received_in_period: float.......................{self.units_received_in_period}\n
        beginning_inv_qty: float..............................{self.beginning_inv_qty}\n
        ending_inv_qty: float.................................{self.ending_inv_qty}\n
        avg_inventory_qty_in_period: int......................{self.avg_inventory_qty_in_period}\n
        net_change_in_inv_qty_over_period: float..............{self.net_change_in_inv_qty_over_period}\n
        cubic_feet_required_per_unit: float...................{self.cubic_feet_required_per_unit}\n
        avg_cubic_feet_utilized_in_period: float..............{self.avg_cubic_feet_utilized_in_period}\n
        avg_monthly_holding_cost_of_inv: float................{self.avg_monthly_holding_cost_of_inv}\n
        sales_price_per_unit: float...........................{self.sales_price_per_unit}\n
        break_even_point_in_units_for_holding_inventory: float{self.break_even_point_in_units_for_holding_inventory}\n
        avg_remaining_shelf_life_of_prod_when_sold:float|None.{self.avg_remaining_shelf_life_of_prod_when_sold}\n
        stock_expiry_is_a_high_risk: bool|None................{self.stock_expiry_is_a_high_risk}\n
        total_profit_contribution_in_period: int..............{self.total_profit_contribution_in_period}\n

        """
        return attrs
    
    def get_KPIs_attrs(self) -> dict:
        """
        This method is intended to be called within a generator.\n
        After a new instance of this class is instantiated, this methods can be called to retrive KPIs in dictionary format which can then be added as a new row into a pandas.DataFrame.
        """
        dict_of_kpis: dict = {
            "Material ID": self.sku,
            "Material Description": self.material_description,
            "Break-Even against Holding costs (in units)": self.break_even_point_in_units_for_holding_inventory,
            "Profit Contribution During the Period": self.total_profit_contribution_in_period,
            "AVG Cubic Feet Utilized During the Period":  self.avg_cubic_feet_utilized_in_period,
            "(Averaged) Holding Cost of Inventory During the Period": self.avg_monthly_holding_cost_of_inv,
            "Is Hazardous?":  self.is_hazardous,
            "Inventory Turnover Ratio": self.inv_turnover_ratio,
            "High Risk of Stock Expiry": self.stock_expiry_is_a_high_risk,

        }
        return dict_of_kpis

    
    def set_mdm_attrs(self) -> None:
        """
        Collect basic attributes of the material.\n

        ### The following attributes are defined in this method:\n

            self.material_description: str
            self.manufacturer: str
            self.manufacturer_part_number: str
            self.supplier: str
            self.supplier_part_number: str
            self.inventory_uom: str
            self.hazardous_classification: str
            self.shelf_life: int
            self.dim_weight: float
            self.dim_length: float
            self.dim_width: float
            self.dim_height: float
            self.material_creation_date: datetime.date|None
            self.is_hazardous: bool|None
            
        """
        # Filter report
        filtered_inv_dataframe: pandas.DataFrame = inventory_report.loc[inventory_report["Product ID"] == self.sku]
        filtered_mdm_dataframe: pandas.DataFrame = mdm_report.loc[mdm_report["Product ID"] == self.sku]
        
        if filtered_inv_dataframe.empty or filtered_mdm_dataframe.empty:
            self.material_description: str = ""
            self.manufacturer: str = ""
            self.manufacturer_part_number: str = ""
            self.supplier: str = ""
            self.supplier_part_number: str = ""
            self.inventory_uom: str = ""
            self.hazardous_classification: str = ""
            self.shelf_life: int = 0
            self.dim_weight: float = 0
            self.dim_length: float = 0
            self.dim_width: float = 0
            self.dim_height: float = 0
            self.material_creation_date: datetime.date|None = None
            self.is_hazardous: bool|None = None
        else:
            self.material_description: str = set(filtered_mdm_dataframe["Product Name"]).pop()
            self.manufacturer: str = set(filtered_mdm_dataframe["Manufacturer"]).pop()
            self.manufacturer_part_number: str = set(filtered_mdm_dataframe["Manufacturer Part Number"]).pop()
            self.supplier: str = set(filtered_mdm_dataframe["Supplier"]).pop()
            self.supplier_part_number: str = set(filtered_mdm_dataframe["Supplier Part Number"]).pop()
            self.inventory_uom: str = set(filtered_mdm_dataframe["Inventory UOM"]).pop()
            self.hazardous_classification: str = set(filtered_mdm_dataframe["Hazardous Classification"]).pop()
            self.shelf_life: int = set(filtered_mdm_dataframe["Shelf Life (Years)"]).pop()
            self.dim_weight: float = set(filtered_mdm_dataframe["Dimension: Weight (lbs)"]).pop()
            self.dim_length: float = set(filtered_mdm_dataframe["Dimension: Length (in)"]).pop()
            self.dim_width: float = set(filtered_mdm_dataframe["Dimension: Width (in)"]).pop()
            self.dim_height: float = set(filtered_mdm_dataframe["Dimension: Height (in)"]).pop()
            self.material_creation_date: datetime.date|None = set(filtered_mdm_dataframe["Product Creation Date"]).pop()
            if "non-hazardous" in self.hazardous_classification.lower():
                self.is_hazardous: bool|None = False
            else:
                self.is_hazardous: bool|None = True

    def retrieve_inv_attrs(self) -> None:
        """
        Pulls inventory-related attributes.\n

        ### The following attributes are defined in this method:\n

            self.beginning_inv_value: float
            self.ending_inv_value: float
            self.inv_value_per_unit: float
            self.units_sold_in_period: int
            self.units_received_in_period: int
            self.beginning_inv_qty: int
            self.ending_inv_qty: int
            self.avg_inventory_qty_in_period: float
            self.net_change_in_inv_qty_over_period: int
            self.cubic_feet_required_per_unit: float
            self.avg_cubic_feet_utilized_in_period: float
            self.avg_monthly_holding_cost_of_inv: float
            self.sales_price_per_unit: float
            self.break_even_point_in_units_for_holding_inventory: float
            self.total_profit_contribution_in_period: int
              
        """
        # Filter report
        filtered_inv_dataframe: pandas.DataFrame = inventory_report.loc[inventory_report["Product ID"] == self.sku]

        if filtered_inv_dataframe.empty:
            self.beginning_inv_value: float = 0
            self.ending_inv_value: float = 0
            self.inv_value_per_unit: float = 0
            self.units_sold_in_period: int = 0
            self.units_received_in_period: int = 0
            self.beginning_inv_qty: int = 0
            self.ending_inv_qty: int = 0
            self.avg_inventory_qty_in_period: float = 0
            self.net_change_in_inv_qty_over_period: int = 0
            self.cubic_feet_required_per_unit: float = 0
            self.avg_cubic_feet_utilized_in_period: float = 0
            self.avg_monthly_holding_cost_of_inv: float = 0
            self.sales_price_per_unit: float = 0
            self.break_even_point_in_units_for_holding_inventory: float = 0
            self.total_profit_contribution_in_period: int = 0
        else:
            # Extract data from report
            self.beginning_inv_value: float = set(filtered_inv_dataframe["Total Value - Opening Stock (USD)"]).pop()
            self.ending_inv_value: float = set(filtered_inv_dataframe["Total Value - Closing Stock (USD)"]).pop()
            self.inv_value_per_unit: float = set(filtered_inv_dataframe["Inventory Value Per Unit (USD)"]).pop()
            self.units_sold_in_period: int = set(filtered_inv_dataframe["Units Sold Last Month"]).pop()
            self.units_received_in_period: int = set(filtered_inv_dataframe["Units Received Last Month"]).pop()
            self.beginning_inv_qty: int = set(filtered_inv_dataframe["Opening Stock"]).pop()
            self.ending_inv_qty: int = set(filtered_inv_dataframe["Closing Stock"]).pop()

            # Calculate additional attributes
            self.avg_inventory_qty_in_period: float = round((self.beginning_inv_qty + self.ending_inv_qty) / 2, 1)
            self.net_change_in_inv_qty_over_period: int = round(self.ending_inv_qty - self.beginning_inv_qty)
            self.cubic_feet_required_per_unit: float = round(((self.dim_length / 12) * (self.dim_width / 12) * (self.dim_height / 12)) , 5)
            self.avg_cubic_feet_utilized_in_period: float = round(self.cubic_feet_required_per_unit * self.avg_inventory_qty_in_period, 1)
            
            cost_per_cubic_ft_of_inv_per_month: float = 0.5  # $ 0.5 per cubic foot of warehouse space is the  US national average cost per month
            
            self.avg_monthly_holding_cost_of_inv: float = round(self.avg_cubic_feet_utilized_in_period * cost_per_cubic_ft_of_inv_per_month)
            self.sales_price_per_unit: float = self.inv_value_per_unit * 1.35  # 20% markup + 15% overhead
            self.contribution_per_unit_in_dollars: float = round(self.sales_price_per_unit  - self.inv_value_per_unit, 2)
            self.break_even_point_in_units_for_holding_inventory: float = round(self.avg_monthly_holding_cost_of_inv / self.contribution_per_unit_in_dollars, 2)
            self.units_sold_over_break_even: float = self.units_sold_in_period - self.break_even_point_in_units_for_holding_inventory
            self.total_profit_contribution_in_period: int = round(self.units_sold_over_break_even * self.contribution_per_unit_in_dollars)


    def get_inv_turnover(self) -> None:
        """
        Calculates Inventory Turnover and days of supply by SKU.\n

         - **Days of supply = 365 / Inventory Turnover**

         - **Inventory Turnover Ratio = Cost of Goods Sold / Average Inventory ($)**

         - **Average Inventory = *(Beginning Inventory ($) + Ending Inventory ($))* / 2**

        ### The following attributes are defined in this method:\n

            self.inv_turnover_ratio: float|None
            self.days_of_supply: int|None
            self.years_of_supply: float|None
            self.avg_remaining_shelf_life_of_prod_when_sold: float|None
            self.stock_expiry_is_a_high_risk: bool|None

        """
        if (
            self.beginning_inv_value
            and self.ending_inv_value
            and self.inv_value_per_unit
            and self.units_sold_in_period
        ):
            # Calculate
            avg_inventory_value_in_period: float = (self.beginning_inv_value + self.ending_inv_value) / 2
            cogs_in_month: float = self.inv_value_per_unit * self.units_sold_in_period
            self.inv_turnover_ratio: float|None = round( (cogs_in_month * 12 ) / avg_inventory_value_in_period, 2)
            self.days_of_supply: int|None = round( 365 / self.inv_turnover_ratio )
            self.years_of_supply: float|None = round( self.days_of_supply / 365 , 1)

            self.avg_remaining_shelf_life_of_prod_when_sold: float|None = round(self.shelf_life - self.years_of_supply, 1)
            if self.avg_remaining_shelf_life_of_prod_when_sold < (self.shelf_life * 0.4): 
                self.stock_expiry_is_a_high_risk: bool|None = True
            else:
                self.stock_expiry_is_a_high_risk: bool|None = False

        else:
            self.inv_turnover_ratio: float|None = None
            self.days_of_supply: int|None = None
            self.years_of_supply: float|None = None
            self.avg_remaining_shelf_life_of_prod_when_sold: float|None = None
            self.stock_expiry_is_a_high_risk: bool|None = None

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------
