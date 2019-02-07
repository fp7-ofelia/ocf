CREATE TABLE privacy_userprivacy (
    user_urn varchar(255),
    accept tinyint(1),
    date_mod datetime,
    PRIMARY KEY (user_urn)
);
