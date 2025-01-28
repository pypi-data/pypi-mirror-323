
-- select distinct catalog_no, campaign_id, company as company, promotion_type as promotion_type, sales_start as sales_start,
--      sales_end as sales_end
-- from RUSTA_DW.CAMPAIGN_VERIFICATION.PROMOTION_PRICE_CHECK as main
        
--  where  promotion_type = 'Packet Price' and sales_end >= CURRENT_DATE
--  order by company, campaign_id;

--  select "Item Code" as article_id, CAMPAIGN_ID as campaign_id, "Item Name" as ITEM_NAME, "Company" as company, "Assortment Type" as assortment_typ,
--     "Role Coordinator" as product_coordinator, promotion_type as promotion_type, sales_start as sales_start, sales_end as sales_end, 
--     "Life Cycle Status" as life_cycle_status, "Assortment Type" as assortment_type,
--     "Active Web SE", "Active Web DE", "Active Web FI", "Active Web NO"
-- from (select distinct catalog_no, campaign_id, company as company, promotion_type as promotion_type, sales_start as sales_start,
--                 sales_end as sales_end, life_cycle_status as life_cycle_status
--             from RUSTA_DW.CAMPAIGN_VERIFICATION.PROMOTION_PRICE_CHECK as main
                    
--             where  promotion_type = 'Packet Price' and sales_end >= CURRENT_DATE
--             order by company, campaign_id) as camp

--     inner join RUSTA_DW.PUBLIC."Item" as item on camp."CATALOG_NO" = item."Item Code" 
--         and camp."COMPANY" = item."Company" and camp.life_cycle_status = 'Active'
--         and "Assortment Type" not in ('SD,SP,AT')
--         where sales_end >= CURRENT_DATE and promotion_type = 'Packet Price'
--         and not (company = '10' and "Active Web SE" = 'No')
--         and not (company = '20' and "Active Web NO" = 'No')
--         and not (company = '23' and "Active Web FI" = 'No')
--         and not (company = '22' and "Active Web DE" = 'No')
-- order by "Company", campaign_id;

-- select *from RUSTA_DW.CAMPAIGN_VERIFICATION.PROMOTION_PRICE_CHECK where  
--  COMPANY = '10' and PROMOTION_TYPE = 'Packet Price' and SALES_END >= CURRENT_DATE
--  order by COMPANY, catalog_no, CAMPAIGN_ID;


select * from RUSTA_DW.PUBLIC."Item" where "Item Code" = '109101510101' and "Company" = '10';


 select "Item Code" as article_id, CAMPAIGN_ID as campaign_id, promotion_desc as promotion_desc,"Item Name" as ITEM_NAME, "Company" as company, "Assortment Type" as assortment_typ,
    "Role Coordinator" as product_coordinator, promotion_type as promotion_type, sales_start as sales_start, sales_end as sales_end, 
    "Life Cycle Status" as life_cycle_status, "Assortment Type" as assortment_type, 
    "Active Web SE", "Active Web DE", "Active Web FI", "Active Web NO"
from  RUSTA_DW.CAMPAIGN_VERIFICATION.PROMOTION_PRICE_CHECK as camp
    inner join RUSTA_DW.PUBLIC."Item" as item on camp."CATALOG_NO" = item."Item Code" 
        and camp."COMPANY" = item."Company" and camp.life_cycle_status = 'Active'
        and "Assortment Type" not in ('SD,SP,AT')
        where sales_end >= CURRENT_DATE and promotion_type = 'Packet Price'
        and not (company = '10' and "Active Web SE" = 'No')
        and not (company = '20' and "Active Web NO" = 'No')
        and not (company = '23' and "Active Web FI" = 'No')
        and not (company = '22' and "Active Web DE" = 'No')
order by "Company", campaign_id;