select CAMPAIGN_ID AS CAMPAIGN_ID, CAMPAIGN_DESCRIPTION as CAMPAIGN_DESCRIPTION, SALES_START as SALES_START, 
                       SALES_END AS SALES_END, DEPARTMENT as DEPARTMENT, SALESGROUP as SALESGROUP, PROMOTION_DESC AS PROMOTION_DESC, 
                       CATALOG_NO AS ARTICLE_ID, ITEM_NAME AS ITEM_NAME, COMPANY as COMPANY, LIFE_CYCLE_STATUS as LIFE_CYCLE_STATUS, 
                       PROMOTION_TYPE as PROMOTION_TYPE, "Active Web SE" as "ACTIVE_WEB_SE",
                       "Active Web DE" as "ACTIVE_WEB_DE", "Active Web FI" as "ACTIVE_WEB_FI", 
                       "Active Web NO" as "ACTIVE_WEB_NO", "Role Coordinator" as PRODUCT_COORDINATOR, 
                        item."Role Campaign Coordinator" as CAMPAIGN_COORDINATOR,
                        CASE 
                        WHEN COMPANY = '10' THEN  item."Active Web SE"
                            WHEN COMPANY = '22' THEN  item."Active Web DE"
                            WHEN COMPANY = '20' THEN  item."Active Web NO"
                            WHEN COMPANY = '23' THEN  item."Active Web FI"
                            END as "ACTIVE_WEB",
                        CASE
                        WHEN COMPANY = '10' THEN  'SE-10'
                          WHEN COMPANY = '22' THEN  'DE-22'
                          WHEN COMPANY = '20' THEN  'NO-20'
                          WHEN COMPANY = '23' THEN  'FI-23'
                          END as "COMPANY_NAME",
                       from RUSTA_DW.CAMPAIGN_VERIFICATION.PROMOTION_PRICE_CHECK as camp
                        inner join RUSTA_DW.PUBLIC."Item" as item on camp."CATALOG_NO" = item."Item Code" 
                        and camp."COMPANY" = item."Company" and camp.life_cycle_status = 'Active'
                        where
                          contains(CAMPAIGN_DESCRIPTION, CONCAT((SUBSTR( DATE_PART('yr', CURRENT_DATE), 3, 4)), LPAD(CAST(DATE_PART('w', CURRENT_DATE) AS VARCHAR), 2, '0') )) 
                          and 
                          (sales_start <= DATE_TRUNC('WEEK', CURRENT_DATE) 
                          or sales_start >= DATE_TRUNC('WEEK', CURRENT_DATE)) 
                          and sales_end >= DATE_TRUNC('WEEK', CURRENT_DATE)
                        AND promotion_type IN ('Combo', 'Multi') and life_cycle_status = 'Active'

                        order by company;


