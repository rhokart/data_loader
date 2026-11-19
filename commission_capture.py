import DbConfig
import openpyxl as xl
import glob

def read_commission_excel(loc):
   
   workbook = xl.load_workbook(loc, data_only=True)
   
   for sheet in workbook.sheetnames:
       if sheet.strip() == 'Brand tier config. output':
          workbook.active = workbook['Brand tier config. output']
          sh = workbook.active
          band_tier_config_data(sh)

       if sheet.strip() == 'Categories & Commercials':
          workbook.active = workbook['Categories & Commercials']
          sh = workbook.active
          catg_commercials_config_data(sh)

   return

def catg_commercials_config_data(sh):
    con = DbConfig.db_conn()
    cursor = con.cursor()
    insert_commission = "INSERT INTO product.commission_structure (catg_id, band_tier, commission, insert_by, insert_tmstp, update_by, update_tmstp, partner_commission) values (%s, %s, %s, 'system'::character varying, CURRENT_TIMESTAMP, 'system'::character varying, CURRENT_TIMESTAMP,%s);"
    for row in range(3,sh.max_row +1 ):
        tier1_commision = sh.cell(row,10).value * 100
        tier2_commision = sh.cell(row,11).value * 100
        tier3_commision = sh.cell(row,12).value * 100 
        tier1_partnercomm = sh.cell(row,13).value * 100
        tier2_partnercomm = sh.cell(row,13).value * 100
        tier3_partnercomm = sh.cell(row,13).value * 100 
        catg_id = int(sh.cell(row,1).value)
        
        value1 = (catg_id,1,tier1_commision,tier1_partnercomm)   # tier-1 commission
        value2 = (catg_id,2,tier2_commision,tier2_partnercomm)   # tier-2 commission
        value3 = (catg_id,3,tier3_commision,tier3_partnercomm)   # tier-3 commission

       
        cursor.execute(insert_commission,value1)
        cursor.execute(insert_commission,value2)
        cursor.execute(insert_commission,value3)
 
    con.commit()

def band_tier_config_data(sh):
    catg_dict = {}
    con = DbConfig.db_conn()
    cursor = con.cursor()
    insert_query = "INSERT INTO product.band_tier_config(catg_id,comp_nme,band_nme,band_tier,insert_by,insert_tmstp,update_by,update_tmstp) VALUES (%s,%s,%s,%s,'SYSTEM',CURRENT_TIMESTAMP,'SYSTEM',CURRENT_TIMESTAMP);"
    values = []
    for col in range(1,sh.max_column +1):   ###  ---> ROW-1 is for filter details.
        for row in range(1, sh.max_row + 1):
            if row == 4 and col > 2:
                catg_dict.update({sh.cell(row,col).value:col})

            if row > 4 :  ### processing for gater than 4 rows
                brand_name = sh.cell(row,2).value
                company_name = sh.cell(row,1).value
                for key,val in catg_dict.items():
                    tier = 0
                    if sh.cell(row,val).value == 'Tier-1':
                        tier = 1
                    if sh.cell(row,val).value == 'Tier-2':
                        tier = 2
                    if sh.cell(row,val).value == 'Tier-3':
                        tier = 3
                    
                    value = (key,company_name,brand_name,tier)
                    if value not in values:
                        values.append(value)
                 #   cursor.execute(insert_query,values)
    
    cursor.executemany(insert_query,values)
    con.commit()    


if __name__ == '__main__':
    path = r"C:\Users\USER\Desktop\d drive\Rhokart\docs\Categories & Commercials.xlsx"
    read_commission_excel(path)
