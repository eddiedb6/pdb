[
    #############################################
    # User DB description should be added below #
    #############################################

    # e.g. #
    {
        PDBConst.Name: "ej",
        PDBConst.Tables: [
        {
            PDBConst.Name: "config",
            PDBConst.Columns: [
            {
                PDBConst.Name: "Name",
                PDBConst.Attributes: ["varchar(128)", "not null", "primary key"]
            },
            {
                PDBConst.Name: "Value",
                PDBConst.Attributes: ["varchar(128)"]
            }],
            PDBConst.PrimaryKey: ["Name"],
            PDBConst.Initials: [
                {"Name": "'version'", "Value": "'0.1'"}
            ]
        }]
    }
    
    #############################################
    # User DB description should be added above #
    #############################################
]
