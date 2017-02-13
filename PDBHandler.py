import os
import sys
import datetime

import PDBConst

from metadata import PDBDef

sys.path.append(PDBDef.schemaBase)
from SchemaChecker import *

# Check config schema first
schemaPath = os.path.join(PDBDef.pdbDirBase, "PDBConfigSchema.py")
pdbConfigPath = os.path.join(PDBDef.pdbDirBase, "metadata/PDBSchema.py")
constPath = os.path.join(PDBDef.pdbDirBase, "PDBConst.py")
configChecker = SchemaChecker(pdbConfigPath, schemaPath, constPath)
configCheckResult, schema = configChecker.Check()
if not configCheckResult:
    exit("PDB schema check error!")

# Generate DB drop script
dbDropScriptPath = os.path.join(PDBDef.pdbDirBase,
                                PDBConst.pdbDirGenerated,
                                PDBDef.pdbFileDropDB)
dbDropScript = open(dbDropScriptPath, "w")
for db in schema:
    dbDropScript.write("drop database " + db[PDBConst.Name] + ";\n")
dbDropScript.close()

#
# Generate DB init script
#

dbInitScriptPath = os.path.join(PDBDef.pdbDirBase,
                                PDBConst.pdbDirGenerated,
                                PDBDef.pdbFileInitDB)
dbInitScript = open(dbInitScriptPath, "w")

# First create DB
for db in schema:
    dbInitScript.write("## Create Database " + db[PDBConst.Name] + " ##\n")
    dbInitScript.write("create database " + db[PDBConst.Name] + ";\n")
    dbInitScript.write("\n")
    dbInitScript.write("use " + db[PDBConst.Name] + ";\n")
    
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
            columnNames = []
            columnValues = []
            for rowValue in row:
                columnNames.append(rowValue[PDBConst.Name])
                columnValues.append(rowValue[PDBConst.Value])
            columns = ", ".join(columnNames)
            value = ", ".join(columnValues)
            dbInitScript.write("insert into " + table[PDBConst.Name] + " (" + columns + ") values (" + value + ");\n")
                               
        dbInitScript.write("\n")
    dbInitScript.write("\n")                               
                               
dbInitScript.close()

# Generate init shell script for MySQL
dbInitShellPath = os.path.join(PDBDef.pdbDirBase,
                               PDBConst.pdbDirGenerated,
                               PDBDef.pdbFileInitDBShell)
dbInitShell = open(dbInitShellPath, "w")
dbInitShell.write("# Usage: sh " + dbInitShellPath + " DB_USERNAME\n")
dbInitShell.write("if test $# -lt 1\n")
dbInitShell.write("then\n")
dbInitShell.write("    echo \"sh " + PDBDef.pdbFileInitDBShell + " DB_USERNAME\"\n")
dbInitShell.write("    exit\n")
dbInitShell.write("fi\n")
dropCommand = PDBDef.pdbCmdMysql + " -u $1 -p < " + dbDropScriptPath
dbInitShell.write(dropCommand + "\n")
dbInitShell.write("echo \"" + dropCommand + "\"\n");
initCommand = PDBDef.pdbCmdMysql + " -u $1 -p < " + dbInitScriptPath
dbInitShell.write(initCommand + "\n")
dbInitShell.write("echo \"" + initCommand + "\"\n")
dbInitShell.close()

# Generate DB backup shell script
dbBackupShellPath = os.path.join(PDBDef.pdbDirBase,
                                 PDBConst.pdbDirGenerated,
                                 PDBDef.pdbFileBackupDBShell)
dbBackupShell = open(dbBackupShellPath, "w")
dbBackupShell.write("# Usage: sh " + dbBackupShellPath + " DB_USERNAME DB_NAME PW\n")
dbBackupShell.write("if test $# -lt 3\n")
dbBackupShell.write("then\n")
dbBackupShell.write("    echo \"" + PDBDef.pdbFileBackupDBShell + " DB_USERNAME DB_NAME PW\"\n")
dbBackupShell.write("    exit\n")
dbBackupShell.write("fi\n")
dbBackupDir = os.path.join(PDBDef.pdbDirBase,
                           PDBConst.pdbDirBackup)
dbBackupFilePath = os.path.join(dbBackupDir, "$2_$(date +'%Y%m%d').bak")
backupCommand = PDBDef.pdbCmdMysqldump + " -u $1 -p $2 > " + dbBackupFilePath
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
dbRestoreShellPath = os.path.join(PDBDef.pdbDirBase,
                                  PDBConst.pdbDirGenerated,
                                  PDBDef.pdbFileRestoreDBShell)
dbRestoreShell = open(dbRestoreShellPath, "w")
dbRestoreShell.write("# Usage: sh " + dbRestoreShellPath + " DB_USERNAME DB_NAME BAK_FILE_NAME\n")
dbRestoreShell.write("if test $# -lt 3\n")
dbRestoreShell.write("then\n")
dbRestoreShell.write("    echo \"" +
                     PDBDef.pdbFileRestoreDBShell +
                     " DB_USERNAME DB_NAME BAK_FILE_NAME\"\n")
dbRestoreShell.write("    exit\n")
dbRestoreShell.write("fi\n")
dbBackupDir = os.path.join(PDBDef.pdbDirBase,
                           PDBConst.pdbDirBackup)
dbRestoreFilePath = os.path.join(dbBackupDir, "$3")
dbRestoreShell.write("dbBakFile=`echo " + dbRestoreFilePath + " | sed -e 's/.7z/.bak/'`\n")
dbRestoreShell.write("cd " + dbBackupDir + "\n")
dbRestoreShell.write("7z e " + dbRestoreFilePath + "\n")
restoreCommand = PDBDef.pdbCmdMysql + " -u $1 -p $2 < $dbBakFile"
dbRestoreShell.write(restoreCommand + "\n")
dbRestoreShell.write("echo \"" + restoreCommand + "\"\n");
dbRestoreShell.write("rm -rf $dbBakFile\n")
dbRestoreShell.close()
