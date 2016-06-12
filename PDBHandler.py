import os
import datetime

import PDBConst

from metadata import PDBSchema
from metadata import PDBDef

# Generate DB drop script
dbDropScriptPath = os.path.join(PDBDef.pdbDirBase,
                                PDBConst.pdbDirGenerated,
                                PDBDef.pdbFileDropDB)
dbDropScript = open(dbDropScriptPath, "w")
for dbName in PDBSchema.pdbDB.keys():
    dbDropScript.write("drop database " + dbName + ";\n")
dbDropScript.close()

#
# Generate DB init script
#

dbInitScriptPath = os.path.join(PDBDef.pdbDirBase,
                                PDBConst.pdbDirGenerated,
                                PDBDef.pdbFileInitDB)
dbInitScript = open(dbInitScriptPath, "w")

# First create DB
for dbName in PDBSchema.pdbDB.keys():
    dbInitScript.write("## Create Database " + dbName + " ##\n")
    dbInitScript.write("create database " + dbName + ";\n")
    dbInitScript.write("\n")
    dbInitScript.write("use " + dbName + ";\n")
    
    # Then create table 
    for tableName in PDBSchema.pdbDB[dbName].keys():
        dbInitScript.write("## Create Table " + tableName + " ##\n")
        dbInitScript.write("create table " + tableName + " (\n")

        # Handle "PRIMARY KEY" first
        primaryKeys = None
        if "PRIMARY KEY" in PDBSchema.pdbDB[dbName][tableName][PDBConst.pdbSchema].keys():
            primaryKeys = PDBSchema.pdbDB[dbName][tableName][PDBConst.pdbSchema]["PRIMARY KEY"]
            del PDBSchema.pdbDB[dbName][tableName][PDBConst.pdbSchema]["PRIMARY KEY"]
        
        # Add column description
        index = len(PDBSchema.pdbDB[dbName][tableName][PDBConst.pdbSchema])
        for column in PDBSchema.pdbDB[dbName][tableName][PDBConst.pdbSchema].keys():
            index = index - 1
            if len(PDBSchema.pdbDB[dbName][tableName][PDBConst.pdbSchema][column]) > 1:
                dbInitScript.write("    " +
                                   column +
                                   " " +
                                   " ".join(PDBSchema.pdbDB[dbName][tableName][PDBConst.pdbSchema][column]))
            else:
                dbInitScript.write("    " +
                                   column +
                                   " " +
                                   PDBSchema.pdbDB[dbName][tableName][PDBConst.pdbSchema][column][0])
            if index == 0:
                if primaryKeys is not None:
                    dbInitScript.write(",\n")
                    dbInitScript.write("    PRIMARY KEY(" + ", ".join(primaryKeys) + ")")
                dbInitScript.write(");\n")
            else:
                dbInitScript.write(",\n")

        # Insert initial values
        if not  PDBSchema.pdbDB[dbName][tableName].has_key(PDBConst.pdbValues):
            continue
        for row in  PDBSchema.pdbDB[dbName][tableName][PDBConst.pdbValues]:
            columns = ", ".join(row.keys())
            value = ", ".join(row.values())
            dbInitScript.write("insert into " + tableName + " (" + columns + ") values (" + value + ");\n")
                               
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
