import unicodedata
from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st

# ---------------------------------------------------------------------------
# Konfigurácia stránky
# ---------------------------------------------------------------------------
st.set_page_config(page_title="AutoServis Pro – virtuálna recepčná", page_icon="🚗")

# ---------------------------------------------------------------------------
# Znalostná báza
# ---------------------------------------------------------------------------
NAZOV_SERVISU = "AutoServis Pro"
KONTAKT = "+421 900 123 456"
OTVARACIE_HODINY = "Pondelok – Piatok: 7:30 – 17:00 (víkend zatvorené)"

CENNIK = {
    "prezutie": {"nazov": "Prezutie pneumatík", "cena": 40},
    "olej": {"nazov": "Výmena oleja", "cena": 60},
    "diagnostika": {"nazov": "Diagnostika", "cena": 50},
    "geometria": {"nazov": "Geometria", "cena": 45},
    "brzdy": {"nazov": "Brzdy", "cena": 25},
    "klima": {"nazov": "Klimatizácia", "cena": 55},
}

# Kľúčové slová (bez diakritiky, malými písmenami)
KLUCOVE_SLOVA_SLUZIEB = {
    "prezutie": ["prezut", "pneu", "kolesa", "kolies", "gum", "zimne", "letne"],
    "olej": ["olej", "oleja", "oleji"],
    "diagnostika": ["diagnost", "chyba", "kontrolka", "porucha"],
    "geometria": ["geometri", "zbiehavost", "nastavenie kolies"],
    "brzdy": ["brzd", "platnick", "kotuc"],
    "klima": ["klim", "chladenie"],
}

KLUCOVE_SLOVA_INTENTOV = {
    "pozdrav": ["ahoj", "dobry den", "dobre rano", "dobry vecer", "cau", "cav", "zdravim", "servus", "nazdar"],
    "hodiny": ["hodin", "otvaracie", "otvorene", "otvoren", "zatvoren", "kedy", "do kedy", "od kedy", "pracovn", "otvarate"],
    "cennik": ["cena", "ceny", "cenu", "cennik", "kolko", "stoji", "stoja", "kolko to", "platit", "eur", "€", "poplatok"],
    "kontakt": ["kontakt", "telefon", "cislo", "zavolat", "volat", "zatelefon", "tel."],
    "sluzby": ["sluzby", "sluzba", "co robite", "co ponukate", "ponuka", "ponukate", "opravujete"],
    "podakovanie": ["dakujem", "dik", "vdaka", "dakujeme", "super"],
    "rozlucka": ["dovidenia", "nashle", "papa", "ciao", "uvidenia"],
}


# ---------------------------------------------------------------------------
# Pomocné funkcie
# ---------------------------------------------------------------------------
def normalizuj(text: str) -> str:
    """Malé písmená + odstránenie diakritiky."""
    text = text.lower().strip()
    text = unicodedata.normalize("NFD", text)
    return "".join(c for c in text if unicodedata.category(c) != "Mn")


def obsahuje(text: str, slova: list[str]) -> bool:
    return any(s in text for s in slova)


def najdi_sluzby(text: str) -> list[str]:
    return [kluc for kluc, slova in KLUCOVE_SLOVA_SLUZIEB.items() if obsahuje(text, slova)]


def je_otvorene_teraz() -> bool:
    teraz = datetime.now(ZoneInfo("Europe/Bratislava"))
    if teraz.weekday() > 4:  # sobota, nedeľa
        return False
    minuty = teraz.hour * 60 + teraz.minute
    return 7 * 60 + 30 <= minuty < 17 * 60


def format_cennik() -> str:
    riadky = [f"- **{s['nazov']}**: {s['cena']} €" for s in CENNIK.values()]
    return "\n".join(riadky)


def odpoved_hodiny() -> str:
    stav = "Momentálne máme **otvorené** ✅" if je_otvorene_teraz() else "Momentálne máme **zatvorené** ⏰"
    return f"🕒 **Otváracie hodiny:** {OTVARACIE_HODINY}\n\n{stav}"


def odpoved_kontakt() -> str:
    return f"📞 Zavolajte nám na **{KONTAKT}** a radi si s vami dohodneme termín."


def generuj_odpoved(sprava: str) -> str:
    """Jednoduchý pravidlový „mozog“ chatbota nad vnútornou znalostnou bázou."""
    t = normalizuj(sprava)

    if not t:
        return "Napíšte mi, s čím vám môžem pomôcť. 🙂"

    sluzby = najdi_sluzby(t)
    pyta_hodiny = obsahuje(t, KLUCOVE_SLOVA_INTENTOV["hodiny"])
    pyta_cenu = obsahuje(t, KLUCOVE_SLOVA_INTENTOV["cennik"])
    pyta_kontakt = obsahuje(t, KLUCOVE_SLOVA_INTENTOV["kontakt"])

    casti = []

    # Konkrétna služba + cena (alebo len spomenutie služby)
    if sluzby:
        for k in sluzby:
            s = CENNIK[k]
            casti.append(f"🔧 **{s['nazov']}** u nás stojí **{s['cena']} €**.")
    elif pyta_cenu:
        casti.append("💶 **Náš cenník:**\n\n" + format_cennik())

    if pyta_hodiny:
        casti.append(odpoved_hodiny())

    if pyta_kontakt:
        casti.append(odpoved_kontakt())

    if casti:
        if sluzby and not pyta_kontakt:
            casti.append(f"Na objednanie nám zavolajte na {KONTAKT}.")
        return "\n\n".join(casti)

    # Ostatné intenty
    if obsahuje(t, KLUCOVE_SLOVA_INTENTOV["sluzby"]):
        return "🚗 **Ponúkame tieto služby:**\n\n" + format_cennik()

    if obsahuje(t, KLUCOVE_SLOVA_INTENTOV["podakovanie"]):
        return "Rado sa stalo! 😊 Ak budete mať ďalšie otázky, som tu."

    if obsahuje(t, KLUCOVE_SLOVA_INTENTOV["rozlucka"]):
        return "Dovidenia a šťastnú cestu! 🚗"

    if obsahuje(t, KLUCOVE_SLOVA_INTENTOV["pozdrav"]):
        return (
            f"Dobrý deň! Som virtuálna recepčná servisu **{NAZOV_SERVISU}**. "
            "Môžem vám poradiť s cenami, otváracími hodinami alebo kontaktom."
        )

    # Záložná odpoveď
    return (
        "Prepáčte, tejto otázke celkom nerozumiem. 🤔 Viem vám poradiť s:\n\n"
        "- **cenami** služieb (napr. „Koľko stojí výmena oleja?“)\n"
        "- **otváracími hodinami**\n"
        "- **kontaktom**\n\n"
        f"Pre všetko ostatné nám zavolajte na {KONTAKT}."
    )


UVITACIA_SPRAVA = (
    f"Dobrý deň! 👋 Som virtuálna recepčná servisu **{NAZOV_SERVISU}**. "
    "Opýtajte sa ma na ceny, otváracie hodiny alebo kontakt."
)


def vymaz_historiu():
    st.session_state.messages = [{"role": "assistant", "content": UVITACIA_SPRAVA}]


# ---------------------------------------------------------------------------
# Stav relácie
# ---------------------------------------------------------------------------
if "messages" not in st.session_state:
    vymaz_historiu()

# ---------------------------------------------------------------------------
# Bočný panel
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header(f"🚗 {NAZOV_SERVISU}")

    st.subheader("🕒 Otváracie hodiny")
    st.write("Po – Pi: 7:30 – 17:00")

    st.subheader("💶 Cenník")
    for s in CENNIK.values():
        st.write(f"- {s['nazov']}: **{s['cena']} €**")

    st.subheader("📞 Kontakt")
    st.write(KONTAKT)

    st.divider()
    st.button("🗑️ Vymazať históriu konverzácie", on_click=vymaz_historiu, use_container_width=True)

# ---------------------------------------------------------------------------
# Hlavná časť – chat
# ---------------------------------------------------------------------------
st.title("🤖 Virtuálna recepčná")
st.caption(f"{NAZOV_SERVISU} – odpovieme na vaše otázky o cenách, hodinách a kontakte.")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Napíšte svoju otázku…"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    odpoved = generuj_odpoved(prompt)
    st.session_state.messages.append({"role": "assistant", "content": odpoved})
    with st.chat_message("assistant"):
        st.markdown(odpoved)
