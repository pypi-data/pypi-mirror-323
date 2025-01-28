select "Item Code" as article_id, "Item Name" as article_name, "Company" as company,  
    "Active FI" as active_fi, "Active Web FI" as active_web_fi ,
    "Item Enable Ecom FI" as item_enable_ecom_de, 
    "Item Ecom Status FI" as item_ecom_status_de,
    "Role Coordinator" as product_coordinator,
    "Life Cycle Status" as life_cycle_status, "Assortment Type" as assortment_type, 
    CURRENT_DATE AS date, "Retail Price" as retail_price, 
    "Actual Price" as actual_price, "Department" as department, 
    "Sales Area" as sales_area    
from rusta_dw.public."Item"  where 
    "Company" = 23 
and
    ("Active Web FI" = 'Yes' or
    ("Item Enable Ecom FI" = 'True' and "Item Ecom Status FI" = 'Active' or
    "Item Enable Ecom FI" = 'True' and "Item Ecom Status FI" = 'Expiring')) 
and "Life Cycle Status" = 'Active'  and
    "Assortment Type" not in ('SD,SP,AT')