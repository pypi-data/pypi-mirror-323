select "Item Code" as article_id, "Item Name" as article_name, "Company" as company,  
"Active DE" as active_de, "Active Web DE" as active_web_de,  "Item Enable Ecom DE" as item_enable_ecom_de, 
 "Item Ecom Status DE" as item_ecom_status_de,
"Role Coordinator" as product_coordinator, 
"Life Cycle Status" as life_cycle_status, "Assortment Type" as assortment_type, CURRENT_DATE AS date, "Retail Price" as retail_price, 
"Actual Price" as actual_price, "Department" as department, "Sales Area" as sales_area
 from rusta_dw.public."Item" 
 where 
    "Company" = 22 
and
    ("Active Web DE" = 'Yes' or
    ("Item Enable Ecom DE" = 'True' and "Item Ecom Status DE" = 'Active' or
    "Item Enable Ecom DE" = 'True' and "Item Ecom Status DE" = 'Expiring')) 
and "Life Cycle Status" = 'Active'  and
    "Assortment Type" not in ('SD,SP,AT')
