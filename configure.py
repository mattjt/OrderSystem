from OrderSystem import db
from OrderSystem.sql.ORM import User, Subteam
from OrderSystem.utilities.Helpers import hash_password


def create_subteam():
    new_subteam = Subteam("Administrators", "Website Admin [Single-User]", True, True)
    db.session.add(new_subteam)
    db.session.commit()


def create_user():
    new_user = User(
        "admin",
        "MORT",
        "Admin",
        hash_password('mort11admin'),
        "mort11org@mort11.org",
        True,
        True,
        True,
        True,
        True,
        True,
        True,
        True,
        1,
        "None",
        False
    )

    db.session.add(new_user)
    db.session.commit()


if __name__ == "__main__":
    create_subteam()
    create_user()
