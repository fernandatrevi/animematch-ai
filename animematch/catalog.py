"""Anime catalog loading and validation."""
import pandas as pd

SAMPLE = [
("Attack on Titan","Action Drama Mystery","Humanity fights for survival behind enormous walls.",8.9,87),
("Death Note","Mystery Psychological Thriller","A student discovers a notebook with deadly powers.",8.6,37),
("Jujutsu Kaisen","Action Supernatural Fantasy","Students battle curses using supernatural abilities.",8.5,24),
("Erased","Mystery Thriller Drama","A man travels into his childhood to prevent tragedy.",8.3,12),
("Parasyte: The Maxim","Action Horror Sci-Fi","A teenager shares his body with an alien parasite.",8.3,24),
("Steins;Gate","Sci-Fi Thriller Drama","Friends discover a way to send messages into the past.",9.0,24),
("Fullmetal Alchemist: Brotherhood","Action Adventure Fantasy","Two brothers seek to recover what they lost.",9.1,64),
("Violet Evergarden","Drama Fantasy Slice of Life","A former soldier learns to understand emotions.",8.6,13),
("Spy x Family","Comedy Action Slice of Life","A spy builds a family for an undercover mission.",8.4,25),
("Monster","Mystery Psychological Thriller","A surgeon pursues a dangerous man he once saved.",8.9,74),
("Psycho-Pass","Sci-Fi Crime Psychological","Inspectors investigate crime in a monitored society.",8.3,22),
("Your Lie in April","Romance Drama Music","A pianist rediscovers music through friendship.",8.6,22),
("Made in Abyss","Adventure Mystery Fantasy","Young explorers descend into a mysterious abyss.",8.6,13),
("Mob Psycho 100","Action Comedy Supernatural","A psychic teenager tries to live a normal life.",8.5,12),
("Odd Taxi","Mystery Drama Thriller","A taxi driver becomes involved in a disappearance.",8.7,13),
]
COLUMNS=["title","genres","synopsis","score","episodes"]

def sample_catalog():
    """Return an offline demonstration catalog."""
    return pd.DataFrame(SAMPLE,columns=COLUMNS)

def normalize_catalog(frame):
    required=set(COLUMNS)
    missing=required.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing catalog columns: {', '.join(sorted(missing))}")
    data=frame.copy()
    for field in ("title","genres","synopsis"):
        data[field]=data[field].fillna("").astype(str).str.strip()
    for field in ("score","episodes"):
        data[field]=pd.to_numeric(data[field],errors="coerce")
    return data.loc[data["title"].ne("")].drop_duplicates("title").reset_index(drop=True)
