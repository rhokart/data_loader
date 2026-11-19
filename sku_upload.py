import openpyxl as xl
import DbConfig
import MongoConfig
import glob
import ImageProcessing

db_con = MongoConfig.MongoConn()
sku_collection = db_con['sku_dtl']
db_conn = MongoConfig.MongoConn()
lst_collection = db_conn['listing_details']
image_key_list = ['Image - 1','Image - 2','Image - 3','Image - 4','Image - 5','Image - 6','Image - 7','Image - 8','Image - 9','Image - 10',
                  'Product Image - 1','Product Image - 2','Product Image - 3','Product Image - 4','Product Image - 5','Product Image - 6','Product Image - 7','Product Image - 8','Product Image - 9','Product Image - 10']

def read_skus_from_xls(loc):
    filenames = glob.glob(loc + "/*.xlsx")
    print(filenames)

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
    listheader_dict = {}
    skuheader_dict = {}
    catg_cde_idx = 0
    parent_lst_idx = 0
    child_lst_idx = 0
    hsn_idx = 0
    sku_lst_idx = 0
## Header data processing...#####
### 0  and 1 th index for header processing...#####

    for col_idx in range(1,sh.max_column +1):    ###  ---> ROW-1 is for filter details.
        tag = sh.cell(2,col_idx).value           ### --> ROW-1 with tagging details.
        col_name = sh.cell(3,col_idx).value      ### --> ROW-2 with tagging details.

        if  str(col_name).strip() == 'Parent Listing':
            parent_lst_idx = col_idx
        elif str(col_name).strip() == 'Child listing':
            child_lst_idx = col_idx
        elif str(col_name).strip() == 'HSN Code':
            hsn_idx = col_idx
        elif str(col_name).strip() == 'SKU Listing':
            sku_lst_idx = col_idx
        elif str(col_name).strip() == 'Unique Category Code':
            catg_cde_idx = col_idx


        ### depending on tagging sku and listing dictionary creations.

        if str(tag).strip() == 'Listing':
            listheader_dict.update({str(col_name):col_idx})

        if str(tag).strip() == 'SKU':
            skuheader_dict.update({str(col_name):col_idx})

    process_core_data(sh,parent_lst_idx,child_lst_idx,sku_lst_idx,listheader_dict,skuheader_dict,catg_cde_idx, hsn_idx)
    return



def process_core_data(sh,parent_lst_idx,child_lst_idx,sku_lst_idx,listheader_dict,skuheader_dict,catg_cde_idx, hsn_idx):
    ### processing records from 3rd for core data processing....
    print('Test-1')
    row_count = 0
    current_parent_listing = ''
    prev_parent_listing = ''

    for row in range(4, sh.max_row+1):
        row_count = row_count + 1
        if row_count == 1:
            current_parent_listing = sh.cell(row,parent_lst_idx).value
            prev_parent_listing = current_parent_listing
            catg_code = process_listing_data(row, sh, parent_lst_idx, listheader_dict, catg_cde_idx)
            if catg_code != 0:
                process_sku_data(row, sh, sku_lst_idx,child_lst_idx, parent_lst_idx,skuheader_dict,hsn_idx)
        else:
            if current_parent_listing == prev_parent_listing:
                process_sku_data(row, sh, sku_lst_idx,child_lst_idx, parent_lst_idx,skuheader_dict,hsn_idx)
                current_parent_listing = sh.cell(row,parent_lst_idx).value

            if current_parent_listing != prev_parent_listing:
                prev_parent_listing = current_parent_listing
                current_parent_listing = sh.cell(row, parent_lst_idx).value
                catg_code = process_listing_data(row, sh, parent_lst_idx, listheader_dict, catg_cde_idx)
                if catg_code != 0:
                    process_sku_data(row, sh, sku_lst_idx,child_lst_idx, parent_lst_idx,skuheader_dict,hsn_idx)

    return


def process_listing_data(row, sh, parent_lst_idx, listheader_dict, catg_cde_idx):
    catg_unq_cde = sh.cell(row, catg_cde_idx).value

    catg_id = store_category_data(catg_unq_cde)   ## category table entry....
    if catg_id != 0:
        parent_lst_name = sh.cell(row,parent_lst_idx).value
        catg_initial = str(catg_id)
        store_listing_data(row,sh, listheader_dict, catg_id, parent_lst_name, catg_initial)
        return catg_id

    return 0
    ### iterating through all columns for getting the required results

def process_sku_data(row, sh, sku_lst_idx,child_lst_idx,  parent_lst_idx, skuheader_dict, hsn_idx):
    con = DbConfig.db_conn()
    cursor = con.cursor()
    max_sku_id_sql = ''' SELECT sku_nbr FROM product.ref_sku_num where lst_id = %s;'''
    update_sku_nbr_sql = '''UPDATE product.ref_sku_num SET  sku_nbr= %s WHERE lst_id = %s;'''
    insert_sku_nbr_sql = ''' INSERT INTO product.ref_sku_num(lst_id, sku_nbr) VALUES (%s, %s); '''
    select_lst_id_sql = '''select lst_id from product.lst_dtl where prnt_lst_name = %s ; '''
    insert_sku_data_sql = '''INSERT INTO product.sku_dtl(lst_id, sku_id, sku_nme,child_lst_nme, hsn_cde) VALUES (%s, %s, %s, %s, %s);'''
    select_sku_data_sql = ''' SELECT count(*) FROM product.sku_dtl where sku_nme = %s; '''
    sku_name = sh.cell(row,sku_lst_idx).value
    lst_name = sh.cell(row,parent_lst_idx).value
    child_lst_nme = sh.cell(row,child_lst_idx).value
    hsn_code = sh.cell(row,hsn_idx).value
    cursor.execute(select_lst_id_sql,(lst_name,))
    lst_value = cursor.fetchone()

    if lst_value is None:
        print("Listing is not created yet.. first create listing before SKUs")
        return

    lst_id = lst_value[0]
    cursor.execute(max_sku_id_sql,(lst_id,))
    sku_nbr = cursor.fetchone()
    if sku_nbr is None:
        sku_gen_no = 100
        cursor.execute(insert_sku_nbr_sql,(lst_id,sku_gen_no))
    else:
        sku_gen_no = sku_nbr[0] + 1
        cursor.execute(update_sku_nbr_sql,(sku_gen_no,lst_id))

    con.commit()
    sku_id = str(lst_id).strip() + 'SKU' +str(sku_gen_no)
    ### insert data into SKU_DTL table with values is sku does not present else update the records.
    cursor.execute(select_sku_data_sql,(sku_name,))
    result = cursor.fetchone()
    if result[0] == 0:
        sku_values = (lst_id,sku_id,sku_name,child_lst_nme,hsn_code)
        cursor.execute(insert_sku_data_sql,sku_values)
    else:
        print('update sku values only.')
        store_sku_attributes(sh, row, skuheader_dict, sku_id,lst_id)

    store_sku_attributes(sh, row, skuheader_dict, sku_id,lst_id)

    con.commit()
    ### Update attribute list
    return


def store_sku_attributes(sh,row,skuheader_dict,sku_id,lst_id):
    sku_dict = {}
    sku_dict.update({'_id':sku_id})
    sku_dict.update({'lst_id': lst_id})
    for key, val in skuheader_dict.items():
        dt = sh.cell(row,val).value
        sku_dict.update({key:dt})

    document = sku_collection.find_one({'_id':sku_id})
    print('sku update dtl :',sku_dict)
    if document:
        qry = {'_id':sku_id}
        res = sku_collection.update_one(qry, {"$set":sku_dict})
    else:
        res = sku_collection.insert_one(sku_dict)

    print("sku attr created:"+str(res))

    return


def store_listing_data(row, sh, listheader_dict, catg_id,listing_name, catg_initial):
    con =  DbConfig.db_conn()
    cur = con.cursor()
    select_listing_sql = ''' select lst_id FROM product.lst_dtl where prnt_lst_name = %s;'''
    max_listing_sql = ''' select lst_nbr from product.ref_nbr where catg_initial = %s ; '''
    update_listing_nbr_sql = '''UPDATE product.ref_nbr SET  lst_nbr= %s WHERE catg_initial = %s ;'''
    insert_listing_nbr_sql = '''INSERT INTO product.ref_nbr(catg_initial, lst_nbr, sku_nbr) VALUES (%s, %s, %s );'''
    insert_listing_sql = ''' INSERT INTO product.lst_dtl(catg_id, lst_id, prnt_lst_name) VALUES (%s, %s, %s); '''
    cur.execute(select_listing_sql,(listing_name,))
    res = cur.fetchone()
    if res  is None :
        cur.execute(max_listing_sql,(catg_initial,))
        max_val = cur.fetchone()
        if max_val is None:
            lst_nbr = 100000
            sku_nbr = 0 ### no sku is created till now.
            cur.execute(insert_listing_nbr_sql,(catg_initial,lst_nbr,sku_nbr))
        else:
            lst_nbr = max_val[0]+1
            cur.execute(update_listing_nbr_sql,(lst_nbr,catg_initial))

        lst_id = str(catg_initial).lstrip().rstrip()+str(lst_nbr).rstrip().lstrip();

        lst_values = (catg_id,lst_id,listing_name)
        cur.execute(insert_listing_sql,lst_values)
        con.commit()
        store_listing_attributes(sh, row, listheader_dict,lst_id,catg_id,listing_name)
    else:
        lst_id = res[0]
        store_listing_attributes(sh, row, listheader_dict, lst_id,catg_id,listing_name)

    return 0

def store_listing_attributes(sh,row, listheader_dict, lst_id,catg_id,listing_name):
    list_dict  = {}
    attribute_dict = {}
    list_dict.update({'_id':lst_id})  ### insert the id values for listing....

    for key, values in listheader_dict.items():
        data = sh.cell(row,values).value
        #### logic for image processing...
        if str(key) in image_key_list:
            if data is not None:
                if str(data) != ' ' and str(data) != '-':
                    img_name = str(lst_id).strip() + '-'+str(key).strip()+'.jpg'
                    img_url = ImageProcessing.image_processing(str(data).strip(),img_name)
                 #   img_url = str(data).strip()
                    attribute_dict.update({key:img_url})

                    if key == 'Image - 1':
                        list_dict.update({'lst_image':img_url})

                    if key == 'Product Image - 1':
                        list_dict.update({'lst_image':img_url})
        else:
            if key == 'Company Name / Brand Name':
                list_dict.update({'brandName':data})
            else:
                attribute_dict.update({key:data})

    list_dict.update({'attributes':attribute_dict})
    list_dict.update({'catg_id': catg_id})
    list_dict.update({'listing_name': listing_name})
    print('listing-dict:',list_dict)
    docs = lst_collection.find_one({'_id':lst_id})
    if docs:
        query = {'_id':lst_id}
        result = lst_collection.update_one(query, {"$set":list_dict})
    else:
        result = lst_collection.insert_one(list_dict)

    print('list attributes created :'+str(result))

    return

def store_category_data( catg_unq_cde):
    con = DbConfig.db_conn()
    cur = con.cursor()
    get_catg_sql = ''' select CATG_ID from product.CATG_DTL where CATG_ID = %s and IS_ACTV = true ;'''
#    get_max_catg_id = ''' select max(CATG_ID) from product.CATG_DTL ;'''
    values = (catg_unq_cde,)
    cur.execute(get_catg_sql, values)
    result = cur.fetchone()

    if result is None:
       # new_catg_id = catg_unq_cde ### starting point of catg id table , we can set to any value here, we are staring from 100 only.
       # catg_val =  (new_catg_id, catg_l1, catg_l2, catg_l3, l1_code, l2_code, l3_code)
       # cur.execute(insert_catg_sql,catg_val)
       # con.commit()
        return 0

    return result[0]


if __name__=="__main__":
    paths =  [
        # r'D:\Rhokart\Listing_2025_05_27\loading'
        r'C:\Users\USER\Desktop\d drive\Rhokart\Listing_2025_05_27\loading\Modular Switches & Modules'
      #  r'C:\Users\USER\Desktop\d drive\Rhokart\Listing_2025_02_22\Category SKU Master Sheets - System format\L1 - Electricals\Modular Switches & Modules',
      #  r'D:\Rhokart\Listing_2025_02_22\Category SKU Master Sheets - System format\L1 - Electricals\LED Lighting'
        # r'D:\Rhokart\listing\Listing Sheets - System format - loaded\LED Lighting'
       ]
    for loc in paths:
        print(loc)
        read_skus_from_xls(loc)
