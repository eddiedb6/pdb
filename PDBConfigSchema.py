{
    SchemaConfigRoot: {
        SchemaType: SchemaTypeArray,
        SchemaRule: [
            CheckForeachAsType(PDBConst.DB)
        ]
    },
    PDBConst.DB: {
        SchemaType: SchemaTypeDict,
        SchemaRule: [
            HasKey(PDBConst.Name, PDBConst.Tables)
        ]
    },
    PDBConst.Name: {
        SchemaType: SchemaTypeString
    },
    PDBConst.Tables: {
        SchemaType: SchemaTypeArray,
        SchemaRule: [
            CheckForeachAsType(PDBConst.Table)
        ]
    },
    PDBConst.Table: {
        SchemaType: SchemaTypeDict,
        SchemaRule: [
            HasKey(PDBConst.Name, PDBConst.Columns)
        ]
    },
    PDBConst.Columns: {
        SchemaType: SchemaTypeArray,
        SchemaRule: [
            CheckForeachAsType(PDBConst.Column)
        ]
    },
    PDBConst.Column: {
        SchemaType: SchemaTypeDict,
        SchemaRule: [
            HasKey(PDBConst.Name, PDBConst.Attributes)
        ]
    },
    PDBConst.Attributes: {
        SchemaType: SchemaTypeArray
    },
    PDBConst.Initials: {
        SchemaType: SchemaTypeDict
    },
    PDBConst.Value: {
        SchemaType: SchemaTypeString
    },
    PDBConst.PrimaryKey: {
        SchemaType: SchemaTypeArray
    }
}
