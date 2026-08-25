CREATE NODE TABLE Drug(
    id STRING,
    name STRING,
    drug_type STRING,
    parent_id STRING,
    maximum_clinical_stage STRING,
    PRIMARY KEY(id)
);

CREATE NODE TABLE Disease(
    id STRING,
    code STRING,
    name STRING,
    description STRING,
    PRIMARY KEY(id)
);

CREATE NODE TABLE Target(
    id INT64,
    name STRING,
    external_id STRING,
    approved_name STRING,
    biotype STRING,
    approved_symbol STRING,
    PRIMARY KEY(id)
);

CREATE NODE TABLE TargetClass(
    id INT64,
    label STRING,
    level STRING,
    PRIMARY KEY(id)
);

CREATE NODE TABLE Pathway(
    id STRING,
    name STRING,
    top_level_term STRING,
    PRIMARY KEY(id)
);

CREATE NODE TABLE Protein(
    protein_key STRING,
    id STRING,
    source STRING,
    PRIMARY KEY(protein_key)
);

CREATE NODE TABLE GO(
    id STRING,
    PRIMARY KEY(id)
);

CREATE NODE TABLE Tractability(
    id STRING,
    modality STRING,
    value BOOLEAN,
    PRIMARY KEY(id)
);


CREATE REL TABLE TARGETS(
    FROM Drug TO Target,
    action_type STRING,
    mechanism_of_action STRING
);

CREATE REL TABLE INDICATED_FOR(
    FROM Drug TO Disease,
    max_clinical_stage STRING
);

CREATE REL TABLE ASSOCIATED_WITH(
    FROM Target TO Disease,
    association_score DOUBLE,
    evidence_count INT64,
    aggregation_type STRING,
    aggregation_value STRING
);

CREATE REL TABLE HAS_TARGET_CLASS(
    FROM Target TO TargetClass
);

CREATE REL TABLE PARTICIPATES_IN(
    FROM Target TO Pathway
);

CREATE REL TABLE HAS_PROTEIN(
    FROM Target TO Protein
);

CREATE REL TABLE HAS_GO(
    FROM Target TO GO
);

CREATE REL TABLE HAS_TRACTABILITY(
    FROM Target TO Tractability,
    value BOOLEAN
);