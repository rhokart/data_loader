import openpyxl as xl
import MongoConfig
import glob

db_con = MongoConfig.MongoConn()
filter_collection = db_con['filter_dtl']

def read_skus_from_xls(loc):
    filenames = glob.glob(loc + "/*.xlsx")
    for file in filenames:
        print('processing files now :'+str(file))
        workbook = xl.load_workbook(file,data_only=True)
        for sheet in workbook.sheetnames:
            if sheet.strip() == 'Listings & SKUs':
                workbook.active = workbook['Listings & SKUs']
                sh=workbook.active
                data_process_by_sheet(sh)

    return

def data_process_by_sheet(sh):
    listing_filter = []
    sku_filter = []
    catg_cde_idx = 0

## Header data processing...#####
### 0  and 1 th index for header processing...#####

    for col_idx in range(1,sh.max_column +1): ###  ---> ROW-1 is for filter details.
        filter = sh.cell(1,col_idx).value;
        tag = sh.cell(2,col_idx).value           ### --> ROW-1 with tagging details.
        col_name = sh.cell(3,col_idx).value      ### --> ROW-2 with tagging details.
        if str(col_name).strip() == 'Unique Category Code':
            catg_cde_idx = col_idx
        ### depending on tagging sku and listing dictionary creations.

        if str(filter).strip() == 'Filter':
            if str(tag).strip() == 'Listing':
                if str(col_name) == 'Company Name / Brand Name':
                    listing_filter.append('brandName')
                else:
                    listing_filter.append(str(col_name))

            if str(tag).strip() == 'SKU':
                sku_filter.append(str(col_name))

    process_core_data(sh,listing_filter,sku_filter,catg_cde_idx)
    return



def process_core_data(sh,listing_filter,sku_filter,catg_cde_idx):
    ### processing records from 3rd for core data processing....
    row_count = 0
    catg_filter = {}
    for row in range(4, sh.max_row+1):
        row_count = row_count + 1
        if row_count == 1:
            catg_Id = sh.cell(row,catg_cde_idx).value
            catg_filter.update({"catgId":catg_Id})
            catg_filter.update({"listing":listing_filter})
            catg_filter.update({"sku":sku_filter})
            document = filter_collection.find_one({'catgId': catg_Id})
            print('sku update dtl :', catg_filter)
            if document:
                qry = {'catgId': catg_Id}
                res = filter_collection.update_one(qry, {"$set": catg_filter})
            else:
                res = filter_collection.insert_one(catg_filter)

            print("collections is created :"+str(res))
            return


if __name__=="__main__":
    paths =  [
        r'D:\Rhokart\Listing_2025_05_27\loaded'
        # r'D:\Rhokart\filter\Category SKU Master Sheets - System format\L1 - Electricals\LED Lighting',
        # r'D:\Rhokart\filter\Category SKU Master Sheets - System format\L1 - Electricals\Modular Switches & Modules',
        # r'D:\Rhokart\filter\Category SKU Master Sheets - System format\L1 - Electricals\Wires & Cables'
       ]
    for loc in paths:
        read_skus_from_xls(loc)
