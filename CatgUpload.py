import glob

import openpyxl as xl

import DbConfig
import ImageProcessing_catg


def loaddata_from_excel(loc):
    filenames = glob.glob(loc + "/*.xlsx")
    for file in filenames:
        print('processing files now :' + str(file))
        workbook = xl.load_workbook(file, data_only=True)
        for sheet in workbook.sheetnames:
            if sheet.strip() == 'catg_mstr':
                workbook.active = workbook['catg_mstr']
                sh = workbook.active
                processData(sh)

    return

def processData(sh):
    l1_name_idx = 0
    l2_name_idx = 0
    l3_name_idx = 0
    l1_code_idx = 0
    l2_code_idx = 0
    l3_code_idx = 0
    catg_code_idx = 0
    l1_disp_idx = 0
    l2_disp_idx = 0
    l3_disp_idx = 0
    l2_icon_idx = 0
    l3_icon_idx = 0

    for col_idx in range(1, sh.max_column + 1):
        col_name = sh.cell(1,col_idx).value

        if str(col_name).strip() == 'Category L1 Name':
            l1_name_idx = col_idx
        elif str(col_name).strip() == 'Category L1 Code (unique)':
            l1_code_idx = col_idx
        elif str(col_name).strip() == 'Category L2 Name':
            l2_name_idx = col_idx
        elif str(col_name).strip() == 'Category L2 Code (unique)':
            l2_code_idx = col_idx
        elif str(col_name).strip() == 'Category L3 Name':
            l3_name_idx = col_idx
        elif str(col_name).strip() == 'Category L3 Code (unique)':
            l3_code_idx = col_idx
        elif str(col_name).strip() == 'Unique Category Code':
            catg_code_idx = col_idx
        elif str(col_name).strip() == 'Cat L1 display name':
            l1_disp_idx = col_idx
        elif str(col_name).strip() == 'Cat L2 display name':
            l2_disp_idx = col_idx
        elif str(col_name).strip() == 'Cat L3 display name':
            l3_disp_idx = col_idx
        elif str(col_name).strip() == 'Category L2 icon':
            l2_icon_idx = col_idx
        elif str(col_name).strip() == 'Category L3 icon':
            l3_icon_idx = col_idx

    count =0
    insert_catg_sql = ''' INSERT INTO product.CATG_DTL(CATG_ID, CATG_L1,CATG_L2, CATG_L3, IS_ACTV,L1_CODE,L2_CODE,L3_CODE,l2_img,l3_img,l1_disp_nme,l2_disp_nme,l3_disp_nme) VALUES (%s,%s,%s, %s, true,%s,%s,%s,%s,%s,%s,%s,%s); '''
    con = DbConfig.db_conn()
    cur = con.cursor()



    for row in range(2, sh.max_row+1):
        ctg_code = sh.cell(row,catg_code_idx).value

        img_name = 'L2-' + str(ctg_code).strip() + '.jpg'
        data_l2 = sh.cell(row,l2_icon_idx).value
        l2_img_url = ImageProcessing_catg.image_processing(str(data_l2).strip(), img_name)

        img_name = 'L3-' + str(ctg_code).strip() + '.jpg'
        data_l3 = sh.cell(row, l3_icon_idx).value
        l3_img_url = ImageProcessing_catg.image_processing(str(data_l3).strip(), img_name)


        values = (sh.cell(row,catg_code_idx).value,sh.cell(row,l1_name_idx).value,sh.cell(row,l2_name_idx).value,sh.cell(row,l3_name_idx).value,sh.cell(row,l1_code_idx).value,sh.cell(row,l2_code_idx).value,sh.cell(row,l3_code_idx).value,l2_img_url,l3_img_url,sh.cell(row,l1_disp_idx).value,sh.cell(row,l2_disp_idx).value,sh.cell(row,l3_disp_idx).value)
        print(values)
        cur.execute(insert_catg_sql,values)
        count = count + 1

    con.commit()
    print(count)


if __name__=='__main__':
    paths = [
        r'C:\Users\USER\Desktop\d drive\Rhokart\Listing_2025_02_22\Category SKU Master Sheets - System format'
        # r'D:\Rhokart\listing\Listing Sheets - System format\Electrical & Wiring Accessories',
        # r'D:\Rhokart\listing\Listing Sheets - System format\LED Lighting'
        # r'D:\Rhokart\listing\Listing Sheets - System format - loaded\LED Lighting'
    ]
    for loc in paths:
        loaddata_from_excel(loc)