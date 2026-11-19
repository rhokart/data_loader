import DbConfig
import MongoConfig

def update_sku_dtl_by_lstid():
    db_con = MongoConfig.MongoConn()
    skudtl_collection = db_con['sku_dtl']
    newsku_dtl = db_con['sku_detail']

    con = DbConfig.db_conn()
    cursor = con.cursor()
    select_skus = "SELECT lst_id, sku_id, sku_nme, child_lst_nme FROM product.sku_dtl;"
    cursor.execute(select_skus)
    res = cursor.fetchall()
    count = 0
    for r in res:
        qry = {'_id': str(r[1]).strip()}
        document = skudtl_collection.find_one(qry)
        if document:
            count = count + 1
            document.update({'lst_id':str(r[0]).strip()})
          #  skudtl_collection.update_one(qry, {"$set": document})
            newsku_dtl.insert_one(document)
            print(document)

        if count % 200 == 0:
            print('records commited:'+str(count))
            con.commit()

    con.commit()
    return

if __name__ == '__main__':
    update_sku_dtl_by_lstid()