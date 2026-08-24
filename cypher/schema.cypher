
CREATE NODE TABLE Drug(
    id INT64,
    name STRING,
    PRIMARY KEY(id)
);

CREATE NODE TABLE Target(
    id INT64,
    name STRING,
    external_id STRING,
    approved_name STRING,
    target_class STRING,
    PRIMARY KEY(id)
);

CREATE NODE TABLE Disease(
    id INT64,
    name STRING,
    PRIMARY KEY(id)
);

CREATE NODE TABLE Pathway(
    id INT64,
    name STRING,
    PRIMARY KEY(id)
);


CREATE NODE TABLE FDALabel(
    id STRING,
    set_id STRING,
    effective_time STRING,
    version STRING,
    spl_id STRING,
    title STRING,
    PRIMARY KEY(id)
);

CREATE NODE TABLE FDASection(
    id STRING,
    section STRING,
    text STRING,
    PRIMARY KEY(id)
);

CREATE NODE TABLE FDAIngredient(
    id STRING,
    name STRING,
    PRIMARY KEY(id)
);


CREATE REL TABLE TARGETS(
    FROM Drug TO Target
);

CREATE REL TABLE INDICATED_FOR(
    FROM Drug TO Disease,
    max_clinical_stage STRING
);

CREATE REL TABLE INTERACTS_WITH(
    FROM Drug TO Drug
);

CREATE REL TABLE PARTICIPATES_IN(
    FROM Target TO Pathway
);

CREATE REL TABLE ASSOCIATED_WITH(
    FROM Target TO Disease,
    score FLOAT
);



CREATE REL TABLE HAS_FDA_LABEL(
    FROM Drug TO FDALabel
);

CREATE REL TABLE HAS_SECTION(
    FROM FDALabel TO FDASection
);

CREATE REL TABLE HAS_INGREDIENT(
    FROM Drug TO FDAIngredient
);
