import sys
sys.path.append("..")
import PDBConst

pdbDB = {
    #############################################
    # User DB description should be added below #
    #############################################

    # e.g. #
    "ej": { # DB name
        "config": { # Table name
            PDBConst.pdbSchema: { # Table description
                "Name": ["varchar(128)", "not null", "primary key"],
                "Value": ["varchar(128)"]
            },
            PDBConst.pdbValues: [ # Table initial values if needed
                {"Name": "'version'", "Value": "'0.1'"}
            ]
        }
    }
    
    #############################################
    # User DB description should be added above #
    #############################################
}
