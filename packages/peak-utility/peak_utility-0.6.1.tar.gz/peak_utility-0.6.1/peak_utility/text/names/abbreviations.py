MALE_ABBREVIATIONS = {
    "Andy": "Andrew",
    "Bill": "William",
    "Billy": "William",
    "Bob": "Robert",
    "Bobbie": "Robert",
    "Bobby": "Robert",
    "Brad": "Bradley",
    "Charlie": "Charles",
    "Chris": "Christopher",
    "Chuck": "Charles",
    "Dan": "Daniel",
    "Danny": "Daniel",
    "Dave": "David",
    "Davey": "David",
    "Davie": "David",
    "Dick": "Richard",
    "Don": "Donald",
    "Doug": "Douglas",
    "Dougie": "Douglas",
    "Ed": "Edward",
    "Eddie": "Edward",
    "Frank": "Francis",
    "Fred": "Frederick",
    "Freddy": "Frederick",
    "Freddie": "Frederick",
    "Ged": "Gerald",
    "Ger": "Gerald",
    "Gerry": "Gerald",
    "Greg": "Gregory",
    "Jerry": "Gerald",
    "Jim": "James",
    "Jimmy": "James",
    "Joe": "Joseph",
    "John": "Jonathan",
    "Johnnie": "Jonathan",
    "Johnny": "Jonathan",
    "Jon": "Jonathan",
    "Ken": "Kenneth",
    "Kenny": "Kenneth",
    "Larry": "Lawrence",
    "Matt": "Matthew",
    "Mattie": "Matthew",
    "Matty": "Matthew",
    "Mick": "Michael",
    "Mickey": "Michael",
    "Micky": "Michael",
    "Mike": "Michael",
    "Nick": "Nicholas",
    "Nicky": "Nicholas",
    "Paddy": ["Padraig", "Patrick"],
    "Pat": "Patrick",
    "Pete": "Peter",
    "Phil": ["Philip", "Phillip"],
    "Rich": "Richard",
    "Rick": "Richard",
    "Rob": "Robert",
    "Robbie": "Robert",
    "Robby": "Robert",
    "Ron": "Ronald",
    "Sam": "Samuel",
    "Sammy": "Samuel",
    "Sid": "Sidney",
    "Ste": ["Stephen", "Steven"],
    "Steve": ["Stephen", "Steven"],
    "Ted": ["Edward", "Theodore"],
    "Tim": "Timothy",
    "Tom": "Thomas",
    "Tommy": "Thomas",
    "Tony": "Anthony",
    "Will": "William",
    "Willy": "William",
}


def abbreviations_for(name: str) -> list[str]:
    return sorted(
        [
            key
            for key, value in MALE_ABBREVIATIONS.items()
            if value == name or name in value
        ]
    )


def alternatives_for(name: str) -> list[str]:
    return sorted(set(full_names_for(name) + abbreviations_for(name)))


def full_names_for(name: str) -> list[str]:
    abbrs = MALE_ABBREVIATIONS.get(name)
    return [abbrs] if isinstance(abbrs, str) else sorted(abbrs) if abbrs else []
