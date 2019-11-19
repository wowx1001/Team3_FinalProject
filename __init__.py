#!/usr/bin/env python
# coding: utf-8

# In[1]:


from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import pymysql
app = Flask(__name__)

@app.route('/')
def student():
    return render_template('firstpage.html')

@app.route('/result',methods = ['POST', 'GET'])
def result():
    if request.method == 'POST':
        db = pymysql.connect(host='127.0.0.1', port=3306, user='root',
                     passwd='1111', db='flower_db', charset='utf8',
                    cursorclass=pymysql.cursors.DictCursor)
        cursor = db.cursor()
        sql = 'select * from flower_tb limit 15;'
        cursor.execute(sql)
        table = cursor.fetchall()
        result = pd.DataFrame(table)
        f_count = result[result['f_type']==1]['f_num'].reset_index(drop=True)
        g_count = result[result['f_type']==0]['f_num'].reset_index(drop=True)
        arr_result=[]
        if len(g_count)>1:
            for i in range(15):
                if (i>=len(g_count)):
                    arr_result.append(f_count[i%len(f_count)])
                else:
                    arr_result.append(g_count[i])
        elif (len(g_count)==1):
            for i in range(15):
                if (i>=4):
                    arr_result.append(f_count[i%len(f_count)])
                else:
                    arr_result.append(g_count[0])        
        else:
            for i in range(15):
                arr_result.append(f_count[i%len(f_count)])
        db.commit()
        db.close()
#         result = request.form
        return render_template("secondpage.html", result=table, result2 = arr_result)
if __name__ == '__main__':
    app.run(debug = True)


# In[ ]:




