select "Item Code" as article_id, "Item Name" as article_name, "Company" as company,  
"Active NO" as active_no, "Active Web NO" as active_web_no, "Role Coordinator" as product_coordinator, 
"Life Cycle Status" as life_cycle_status, "Assortment Type" as assortment_type, CURRENT_DATE AS date, "Retail Price" as retail_price,
"Actual Price" as actual_price, "Department" as department, "Sales Area" as sales_area
 from rusta_dw.public."Item" 
 where 
    "Company" = 20 
and
    ("Active Web NO" = 'Yes' or
    ("Item Enable Ecom NO" = 'True' and "Item Ecom Status NO" = 'Active' or
    "Item Enable Ecom NO" = 'True' and "Item Ecom Status NO" = 'Expiring')) 
and "Life Cycle Status" = 'Active'  and
    "Assortment Type" not in ('SD,SP,AT')

