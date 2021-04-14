import os

#Create a dictionnary of entities
def createDictionnaryEntities(pathToFolder="./TxtAppendix/Entities/"):
    entities= {}
    for root, dirs, files in os.walk(pathToFolder, topdown=False):
       for name in files:
           fr=open(root+name,"r")
           entity=name.rsplit('.', 1)[0]
           entities[entity]=[]
           for x in fr:
               x=x.replace('\n', '')
               entities[entity].append(x)
           fr.close()
    return entities


#Create nlu file
def createNluFile(entities,pathToFolder="./TxtAppendix/Intents/",name="nlu1.yml"):
    fw=open(name,"w")
    fw.write('version: "2.0"\n\n')
    fw.write("nlu:\n")
    
    for root, dirs, files in os.walk(pathToFolder, topdown=False):
       for name in files:
          fr=open(root+name,"r")
          intent=name.rsplit('.', 1)[0]
          fw.write("- intent: "+intent+"\n  examples: |\n")
          for x in fr:
              if "[]" in x:
                  start=x.index("(")
                  end=x.index(")")
                  entitieDic=x[start+1:end]
                  for entity in entities[entitieDic]:
                      y=x.replace("[]", "["+entity+"]")
                      fw.write("    - "+y) 
              else:
                  fw.write("    - "+x)
          fr.close()
          fw.write("\n\n")
    fw.close()

entities=createDictionnaryEntities()
createNluFile(entities,name="nlutest.yml")
