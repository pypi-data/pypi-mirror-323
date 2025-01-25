from ru.travelfood.simple_ui import SimpleUtilites as suClass
from ru.travelfood.simple_ui import ImportUtils as suImport
from pelicandb import Pelican
import android
import time
import json
from android.util import Log

dbdir = suClass.get_simplebase_dir()
pelicans = {}
#print("file pelican.py")
def init(init_str):
    global pelicans

    try:

        databases = json.loads(init_str)
        Log.i("UI_TAG","Pelican initialization")
        for db in databases:
            if "database" in db:
                new_db = Pelican(db.get("database"),path=dbdir,RAM = db.get("RAM",False), singleton=db.get("singleton",False))

                print("Pelican: "+db.get("database"))
                pelicans[db.get("database")] = new_db
                #print("db_insert")
                if db.get("initialize")==True:
                    #print("initialize 1")
                    pelicans[db.get("database")].initialize()
                    #print("initialize 2")
                if "reindex_hash" in db:
                    for ind in db.get("reindex_hash"):
                       for k,v in ind.items():
                        odb =pelicans[db.get("database")]  
                        odb[k].reindex_hash(v)
                        
                        print("Reindex:"+ind)
                if "reindex_text" in db:
                    for ind in db.get("reindex_text"):
                        odb =pelicans[db.get("database")]  
                        odb[k].reindex_text(v)
                       
                        print("Reindex:"+ind)

    except Exception as e:
        print("Pelicans init string is not valid: "+str(e))
        return False

    return True

#context = suClass.getGlobalContext()
#mToast = Toast.makeText(context, "Pelican initializing", Toast.LENGTH_LONG)
#mToast.show()
#mToast.setText(db.get("name") + ": ready")
