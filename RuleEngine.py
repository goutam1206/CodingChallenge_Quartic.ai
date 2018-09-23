import json
import re
from pprint import pprint

def createRule(sigType,column,operator,value,dataType):
    # Below three if conditions are for error handling. In case of error, returning -1, -2 or -3
    # -1 for invalid operator, -2 for invalid datatype, -3 for conditional failure of operator in case of datatype string
    if(operator != ">" and operator != "<" and operator != "=" and operator != "!=" and operator != ">=" and operator != "<="):
        return "-1"
    if (dataType.lower() != "integer" and dataType.lower() != "string" and dataType.lower() != "datetime"):
        return "-2"
    if (dataType.lower() == "string"):
        if (operator == ">" or operator == "<" or operator == ">=" or operator == "<="):
            return "-3"
    # Below is the rule format, returned from this method
    RULE = sigType+","+column + operator + value + "#" + dataType
    return RULE

def executeRule(currentRule,jsondata):
    # Splitting with #, to separate, datatype with the other rule string
    curRule,comparisonType = currentRule.split("#")
    # Splitting the column with the condition
    col,cond = curRule.split(",")
    size = len(jsondata)
    # Getting only the signals that satisfy the datatype condition 
    signals = list(x for i in range(0,size) for x in [jsondata[i]] if jsondata[i]["signal"] == col and jsondata[i]["value_type"].lower() == comparisonType.lower() )
    # Framing the regular expression to understand the condition in a better way
    operRegex = re.compile(r'(.*?)(>=|<=|=|>|<|!=)(.*)')
    # below variables contain the splitted condition
    splitted = operRegex.search(cond)
    left = splitted.group(1)
    oper = splitted.group(2)
    right = splitted.group(3)
    
    if (comparisonType.lower() == "datetime"):
        right = right.replace(" *","").replace("-","").replace(":","")
    # resultSet is an empty list which holds the output
    resultSet = []
    # Only for datetime datatype, separate processing is required. Removing the spaces, hiphens and colons.
    # This helps in comparing the integers efficiently.
    # Each operator contains one conditional statement
    if (oper == ">"):
        if (comparisonType.lower() == "datetime"):
            resultSet = list(val for i in range(0,len(signals)) for val in [signals[i]] if signals[i][left].replace(" *","").replace("-","").replace(":","") < right) 
        else:    
            resultSet = list(val for i in range(0,len(signals)) for val in [signals[i]] if signals[i][left] < right)
    elif (oper == "<"):
        if (comparisonType.lower() == "datetime"):
            resultSet = list(val for i in range(0,len(signals)) for val in [signals[i]] if signals[i][left].replace(" *","").replace("-","").replace(":","") > right)
        else:
            resultSet = list(val for i in range(0,len(signals)) for val in [signals[i]] if signals[i][left] > right)
    elif (oper == "="):
        if (comparisonType.lower() == "datetime"):
            resultSet = list(val for i in range(0,len(signals)) for val in [signals[i]] if signals[i][left].replace(" *","").replace("-","").replace(":","") != right)
        else: 
            resultSet = list(val for i in range(0,len(signals)) for val in [signals[i]] if signals[i][left] != right)
    elif (oper == "!="):
        if (comparisonType.lower() == "datetime"):
            resultSet = list(val for i in range(0,len(signals)) for val in [signals[i]] if signals[i][left].replace(" *","").replace("-","").replace(":","") == right)      
        else:
            resultSet = list(val for i in range(0,len(signals)) for val in [signals[i]] if signals[i][left] == right)      
    elif (oper == ">="):
        if (comparisonType.lower() == "datetime"):
            resultSet = list(val for i in range(0,len(signals)) for val in [signals[i]] if signals[i][left].replace(" *","").replace("-","").replace(":","") < right)
        else:
            resultSet = list(val for i in range(0,len(signals)) for val in [signals[i]] if signals[i][left] < right)
    elif (oper == "<="):
        if (comparisonType.lower() == "datetime"):
            resultSet = list(val for i in range(0,len(signals)) for val in [signals[i]] if signals[i][left].replace(" *","").replace("-","").replace(":","") > right)
        else:
            resultSet = list(val for i in range(0,len(signals)) for val in [signals[i]] if signals[i][left] > right)
    else:
        print ("Invalid ruleset. Please check")
    return resultSet


#Opening the file which has the complete json raw data
with open('raw_data.json') as f:
        data = json.load(f)
f.close()

#Opening the rules file in read mode to execute the rules
fileHandler = open('rules.ini',"r")
resultList = []
for line in fileHandler:
    line.strip()
    if line.startswith("#"):
        continue
    signal,column,operator,value,datatype = line.split(",")
    # Below line calls the rule creator. Returns negative integer in case of error, else, will return the rule to be executed
    rule = createRule(signal.strip(),column.strip(),operator.strip(),value.strip(),datatype.strip())
    
    if (rule == "-1"):
        print ("Invalid operator used: " + operator + " Please use >,<,>=,<=,=,!=")
        continue
    if (rule == "-2"):
        print ("Invalid Data Type used: " + datatype + " Please use one of these, integer, string or datetime")
        continue
    if (rule == "-3"):
        print ("Invalid operator used for datatype string: " + operator + " Please use = or != in case of string")
        continue
    # Below function executed the rule that is created from the text file
    resultList = executeRule(rule,data)
    print ("Result for the rule, "+ rule + " is:")
    print (resultList)
    print ("\n")
fileHandler.close()