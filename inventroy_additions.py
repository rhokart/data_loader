from psycopg2 import IntegrityError

import DbConfig


def process_inventory_by_sku():
    con = DbConfig.db_conn()
    cursor = con.cursor()
    select_skus = "SELECT lst_id, sku_id, REPLACE(sku_nme, ',', '-') as sku_nme, child_lst_nme FROM product.sku_dtl;"
    insert_inventory = "INSERT INTO product.inventory_dtl(sku_id, sku_nme, seller_id, seller_nme, units, gst_pct, is_actv, unit_price_with_gst, unit_price_wo_gst,currency)VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,%s);"
    cursor.execute(select_skus)
    res = cursor.fetchall()
    count = 0
    for r in res:
        count = count + 1
        values = (r[1].strip(),r[2].strip(),'9','Spencer Retails Limited',10000,18,True,1.18,1,'INR')
        try:
        #    print(values)
            cursor.execute(insert_inventory,values)
        except IntegrityError:
            con.rollback()
        #    print("Integrity error occurs"+r[1])
        # count = count + 1
        # values = (r[1], r[2], '5', 'Anup Traders Limited', 50, 18, True, 55600, 6700,'INR')
        # cursor.execute(insert_inventory,values)
        # values = (r[1], r[2], '6', 'Sanjay Electrical Limited', 99, 18, True, 32900, 5400, 'INR')
        # cursor.execute(insert_inventory, values)


        if count % 200 == 0:
            print('records commited:'+str(count))
            con.commit()

    con.commit()
    return

if __name__ == '__main__':
    process_inventory_by_sku()