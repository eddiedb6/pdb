import os
import sys
import datetime

import PDBConst
from metadata import PDBConfig
from schema import SchemaChecker

pdbDirBase = os.path.split(os.path.realpath(__file__))[0]

# Check database definition schema first
schemaPath = os.path.join(pdbDirBase, "PDBSchema.py")
dbDefinitionPath = PDBConfig.pdbDefinitionPath
constPath = os.path.join(pdbDirBase, "PDBConst.py")
configChecker = SchemaChecker.SchemaChecker(dbDefinitionPath, schemaPath, constPath)
configCheckResult, schema = configChecker.Check()
if not configCheckResult:
    exit("PDB schema check error!")

# Generate DB drop script
dbDropScriptPath = os.path.join(PDBConfig.pdbDirGenerated, PDBConfig.pdbFileDropDB)
dbDropScript = open(dbDropScriptPath, "w")
for db in schema:
    dbDropScript.write("drop database " + db[PDBConst.Name] + ";\n")
dbDropScript.close()

#
# Generate DB init script
#

dbInitScriptPath = os.path.join(PDBConfig.pdbDirGenerated, PDBConfig.pdbFileInitDB)
dbInitScript = open(dbInitScriptPath, "w")

# First create DB
for db in schema:
    dbInitScript.write("## Create Database " + db[PDBConst.Name] + " ##\n")
    dbInitScript.write("create database " + db[PDBConst.Name] + ";\n")
    dbInitScript.write("use " + db[PDBConst.Name] + ";\n")
    dbInitScript.write("\n")
    
    # Then create table 
    for table in db[PDBConst.Tables]:
        dbInitScript.write("## Create Table " + table[PDBConst.Name] + " ##\n")
        dbInitScript.write("create table " + table[PDBConst.Name] + " (\n")

        # Handle "PRIMARY KEY" first
        primaryKeys = None
        if PDBConst.PrimaryKey in table:
            primaryKeys = table[PDBConst.PrimaryKey]
            del table[PDBConst.PrimaryKey]
        
        # Add column description
        index = len(table[PDBConst.Columns])
        for column in table[PDBConst.Columns]:
            index = index - 1
            if len(column[PDBConst.Attributes]) > 1:
                dbInitScript.write("    " +
                                   column[PDBConst.Name] +
                                   " " +
                                   " ".join(column[PDBConst.Attributes]))
            else:
                dbInitScript.write("    " +
                                   column[PDBConst.Name] +
                                   " " +
                                   column[PDBConst.Attributes][0])
            if index == 0:
                if primaryKeys is not None:
                    dbInitScript.write(",\n")
                    dbInitScript.write("    PRIMARY KEY(" + ", ".join(primaryKeys) + ")")
                dbInitScript.write(");\n")
            else:
                dbInitScript.write(",\n")

        # Insert initial values
        if PDBConst.Initials not in table:
            continue
        for row in  table[PDBConst.Initials]:
            columns = ", ".join(row.keys())
            value = ", ".join(row.values())
            dbInitScript.write("insert into " + table[PDBConst.Name] + " (" + columns + ") values (" + value + ");\n")
                               
        dbInitScript.write("\n")
    dbInitScript.write("\n")                               
                               
dbInitScript.close()

# Generate init shell script for MySQL
dbInitShellPath = os.path.join(PDBConfig.pdbDirGenerated, PDBConfig.pdbFileInitDBShell)
dbInitShell = open(dbInitShellPath, "w")
dbInitShell.write("# Usage: sh " + dbInitShellPath + " DB_USERNAME\n")
dbInitShell.write("if test $# -lt 1\n")
dbInitShell.write("then\n")
dbInitShell.write("    echo \"sh " + PDBConfig.pdbFileInitDBShell + " DB_USERNAME\"\n")
dbInitShell.write("    exit\n")
dbInitShell.write("fi\n")
dropCommand = PDBConfig.pdbCmdMysql + " -u $1 -p < " + dbDropScriptPath
dbInitShell.write(dropCommand + "\n")
dbInitShell.write("echo \"" + dropCommand + "\"\n");
initCommand = PDBConfig.pdbCmdMysql + " -u $1 -p < " + dbInitScriptPath
dbInitShell.write(initCommand + "\n")
dbInitShell.write("echo \"" + initCommand + "\"\n")
dbInitShell.close()

# Generate DB backup shell script
dbBackupShellPath = os.path.join(PDBConfig.pdbDirGenerated, PDBConfig.pdbFileBackupDBShell)
dbBackupShell = open(dbBackupShellPath, "w")
dbBackupShell.write("# Usage: sh " + dbBackupShellPath + " DB_USERNAME DB_NAME PW\n")
dbBackupShell.write("if test $# -lt 3\n")
dbBackupShell.write("then\n")
dbBackupShell.write("    echo \"" + PDBConfig.pdbFileBackupDBShell + " DB_USERNAME DB_NAME PW\"\n")
dbBackupShell.write("    exit\n")
dbBackupShell.write("fi\n")
dbBackupFilePath = os.path.join(PDBConfig.pdbDirBackup, "$2_$(date +'%Y%m%d').bak")
backupCommand = PDBConfig.pdbCmdMysqldump + " -u $1 -p $2 > " + dbBackupFilePath
dbBackupShell.write(backupCommand + "\n")
dbBackupShell.write("echo \"" + backupCommand + "\"\n");
dbBackupShell.write("7z a -p$3 " +
                    dbBackupFilePath.replace(".bak", ".7z") +
                    " " +
                    dbBackupFilePath +
                    "\n")
dbBackupShell.write("rm -rf " + dbBackupFilePath + "\n")
dbBackupShell.close()

# Generate DB restore shell script
dbRestoreShellPath = os.path.join(PDBConfig.pdbDirGenerated, PDBConfig.pdbFileRestoreDBShell)
dbRestoreShell = open(dbRestoreShellPath, "w")
dbRestoreShell.write("# Usage: sh " + dbRestoreShellPath + " DB_USERNAME DB_NAME BAK_FILE_NAME\n")
dbRestoreShell.write("if test $# -lt 3\n")
dbRestoreShell.write("then\n")
dbRestoreShell.write("    echo \"" +
                     PDBConfig.pdbFileRestoreDBShell +
                     " DB_USERNAME DB_NAME BAK_FILE_NAME\"\n")
dbRestoreShell.write("    exit\n")
dbRestoreShell.write("fi\n")
dbRestoreFilePath = os.path.join(PDBConfig.pdbDirBackup, "$3")
dbRestoreShell.write("dbBakFile=`echo " + dbRestoreFilePath + " | sed -e 's/.7z/.bak/'`\n")
dbRestoreShell.write("cd " + PDBConfig.pdbDirBackup + "\n")
dbRestoreShell.write("7z e " + dbRestoreFilePath + "\n")
restoreCommand = PDBConfig.pdbCmdMysql + " -u $1 -p $2 < $dbBakFile"
dbRestoreShell.write(restoreCommand + "\n")
dbRestoreShell.write("echo \"" + restoreCommand + "\"\n");
dbRestoreShell.write("rm -rf $dbBakFile\n")
dbRestoreShell.close()
