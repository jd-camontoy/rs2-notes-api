db = db.getSiblingDB("motivation_meter_db")
db.survey_settings.drop()

db.survey_settings.insertOne({
    "number_of_respondents": [10, 20, 30],
    "keywords_selection": [
        "Salary",
        "Management",
        "Growth",
        "Culture"
    ]
})