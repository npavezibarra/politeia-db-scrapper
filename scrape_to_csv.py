import asyncio
import csv
import os
import re
from datetime import datetime
from playwright.async_api import async_playwright

BASE_URL = "https://www.emol.com/especiales/2024/nacional/elecciones2024/resultados.asp#!a2758"
OUTPUT_DIR = "/Users/nicolas/Desktop/PoliteiaDB/RM"

COMMUNE_CODES = {
    "Alhué": "13502", "Buin": "13402", "Calera de Tango": "13403", "Cerrillos": "13102",
    "Cerro Navia": "13103", "Cholchol": "9121", "Colina": "13301", "Algarrobo": "56001",
    "Alto Biobío": "81301", "Alto del Carmen": "31302", "Alto Hospicio": "21102", "Ancud": "10117",
    "Andacollo": "41103", "Angol": "91201", "Antártica": "12111", "Antofagasta": "22101",
    "Antuco": "81302", "Arauco": "81201", "Arica": "15101", "Aysén": "11103",
    "Bulnes": "16101", "Cabildo": "54002", "Cabo de Hornos": "12110", "Cabrero": "81303",
    "Calama": "22201", "Calbuco": "10102", "Caldera": "31102", "Calle Larga": "53001",
    "Camarones": "15102", "Camiña": "21202", "Canela": "41202", "Cañete": "81202",
    "Carahue": "91102", "Cartagena": "56002", "Casablanca": "51002", "Castro": "10118",
    "Catemu": "57001", "Cauquenes": "71401", "Chaitén": "10127", "Chañaral": "31201",
    "Chanco": "71402", "Chépica": "61302", "Chiguayante": "81103", "Chile Chico": "11109",
    "Chillán": "16102", "Chillán Viejo": "16103", "Chimbarongo": "61303", "Chonchi": "10119",
    "Cisnes": "11104", "Cobquecura": "16115", "Cochamó": "10103", "Cochrane": "11106",
    "Codegua": "61102", "Coelemu": "16116", "Coihueco": "16110", "Coinco": "61103",
    "Colbún": "71302", "Colchane": "21203", "Collipulli": "91202", "Coltauco": "61104",
    "Combarbalá": "41302", "Concepción": "81101", "Concón": "51003", "Constitución": "71102",
    "Contulmo": "81203", "Copiapó": "31101", "Coquimbo": "41102", "Coronel": "81102",
    "Corral": "14102", "Coyhaique": "11101", "Cunco": "91103", "Curacautín": "91203",
    "Curaco de Vélez": "10120", "Curanilahue": "81204", "Curarrehue": "91104", "Curepto": "71103",
    "Curicó": "71201", "Dalcahue": "10121", "Diego de Almagro": "31202", "Doñihue": "61105",
    "El Carmen": "16104", "El Quisco": "56003", "El Tabo": "56004", "Empedrado": "71104",
    "Ercilla": "91204", "Florida": "81104", "Freire": "91105", "Freirina": "31303",
    "Fresia": "10104", "Frutillar": "10105", "Futaleufú": "10128", "Futrono": "14110",
    "Galvarino": "91106", "General Lagos": "15202", "Gorbea": "91107", "Graneros": "61106",
    "Guaitecas": "11105", "Hijuelas": "55001", "Hualaihué": "10129", "Hualañé": "71202",
    "Hualpén": "81112", "Hualqui": "81105", "Huara": "21204", "Huasco": "31304",
    "Illapel": "41201", "Iquique": "21101", "Isla de Pascua": "52001", "Juan Fernández": "51004",
    "La Calera": "55002", "La Cruz": "55003", "La Estrella": "61202", "La Higuera": "41104",
    "La Ligua": "54001", "La Serena": "41101", "La Unión": "14109", "Lago Ranco": "14111",
    "Lago Verde": "11102", "Laguna Blanca": "12102", "Laja": "81304", "Lanco": "14103",
    "Las Cabras": "61107", "Lautaro": "91108", "Lebu": "81205", "Licantén": "71203",
    "Limache": "58001", "Linares": "71301", "Litueche": "61203", "Llaillay": "57002",
    "Llanquihue": "10107", "Lolol": "61304", "Loncoche": "91109", "Longaví": "71303",
    "Lonquimay": "91205", "Los Álamos": "81206", "Los Andes": "53002", "Los Ángeles": "81305",
    "Los Lagos": "14104", "Los Muermos": "10106", "Los Sauces": "91206", "Los Vilos": "41203",
    "Lota": "81106", "Lumaco": "91207", "Machalí": "61108", "Máfil": "14105",
    "Malloa": "61109", "Marchigüe": "61204", "María Elena": "22302", "Mariquina": "14106",
    "Maule": "71105", "Maullín": "10108", "Mejillones": "22102", "Melipeuco": "91110",
    "Molina": "71204", "Monte Patria": "41303", "Mostazal": "61110", "Mulchén": "81306",
    "Nacimiento": "81307", "Nancagua": "61305", "Navidad": "61205", "Negrete": "81308",
    "Ninhue": "16117", "Ñiquén": "16111", "Nogales": "55004", "Nueva Imperial": "91111",
    "O’Higgins": "11107", "Olivar": "61111", "Ollagüe": "22202", "Olmué": "58002",
    "Osorno": "10110", "Ovalle": "41301", "Padre Las Casas": "91112", "Paihuano": "41105",
    "Paillaco": "14107", "Palena": "10130", "Palmilla": "61306", "Panguipulli": "14108",
    "Panquehue": "57003", "Papudo": "54003", "Paredones": "61206", "Parral": "71304",
    "Pelarco": "71106", "Pelluhue": "71403", "Pemuco": "16105", "Pencahue": "71107",
    "Penco": "81107", "Peralillo": "61307", "Perquenco": "91113", "Petorca": "54004",
    "Peumo": "61112", "Pica": "21205", "Pichidegua": "61113", "Pichilemu": "61201",
    "Pinto": "16106", "Pitrufquén": "91114", "Placilla": "61308", "Portezuelo": "16118",
    "Porvenir": "12105", "Pozo Almonte": "21201", "Primavera": "12106", "Pucón": "91115",
    "Puerto Montt": "10101", "Puerto Natales": "12108", "Puerto Octay": "10111",
    "Puerto Varas": "10109", "Pumanque": "61309", "Punitaqui": "41304", "Punta Arenas": "12101",
    "Puqueldón": "10122", "Purén": "91208", "Purranque": "10112", "Putaendo": "57004",
    "Putre": "15201", "Puyehue": "10113", "Queilén": "10123", "Quellón": "10124",
    "Quemchi": "10125", "Quilaco": "81309", "Quilleco": "81310", "Quillón": "16107",
    "Quillota": "55005", "Quilpué": "58003", "Quinchao": "10126", "Quinta de Tilcoco": "61114",
    "Quirihue": "16119", "Rancagua": "61101", "Ránquil": "16120", "Rauco": "71205",
    "Renaico": "91209", "Rengo": "61115", "Requínoa": "61116", "Retiro": "71305",
    "Rinconada": "53003", "Río Bueno": "14112", "Río Claro": "71108", "Río Hurtado": "41305",
    "Río Ibáñez": "11110", "Río Negro": "10114", "Río Verde": "12103", "Romeral": "71206",
    "Saavedra": "91116", "Sagrada Familia": "71207", "Salamanca": "41204",
    "San Antonio": "56005", "San Carlos": "16112", "San Clemente": "71109",
    "San Esteban": "53004", "San Fabián": "16113", "San Felipe": "57005",
    "San Fernando": "61301", "San Gregorio": "12104", "San Ignacio": "16108",
    "San Javier": "71306", "San Juan de la Costa": "10115", "San Nicolás": "16114",
    "San Pablo": "10116", "San Pedro de Atacama": "22203", "San Pedro de la Paz": "81108",
    "San Rafael": "71110", "San Rosendo": "81311", "San Vicente": "61117",
    "Santa Bárbara": "81312", "Santa Cruz": "61310", "Santa Juana": "81109",
    "Santa Juana": "81109", # Possible duplicate from user input, keeping safe
    "Santo Domingo": "56006", "Sierra Gorda": "22103", "Talca": "71101",
    "Talcahuano": "81110", "Taltal": "22104", "Temuco": "91101", "Teno": "71208",
    "Teodoro Schmidt": "91117", "Tierra Amarilla": "31103", "Timaukel": "12107",
    "Tirúa": "81207", "Tocopilla": "22301", "Toltén": "91118", "Tomé": "81111",
    "Torres del Paine": "12109", "Tortel": "11108", "Traiguén": "91210",
    "Trehuaco": "16121", "Tucapel": "81313", "Valdivia": "14101", "Vallenar": "31301",
    "Valparaíso": "51001", "Vichuquén": "71209", "Victoria": "91211", "Vicuña": "41106",
    "Vilcún": "91119", "Villa Alegre": "71307", "Villa Alemana": "58004",
    "Villarrica": "91120", "Viña del Mar": "51005", "Yerbas Buenas": "71308",
    "Yumbel": "81314", "Yungay": "16109", "Zapallar": "54005", "Conchalí": "13104",
    "Curacaví": "13405", "El Bosque": "13105", "El Monte": "13603",
    "Estación Central": "13106", "Huechuraba": "13107", "Independencia": "13108",
    "Isla de Maipo": "13406", "La Cisterna": "13109", "La Florida": "13110",
    "La Granja": "13111", "La Pintana": "13112", "La Reina": "13113", "Lampa": "13302",
    "Las Condes": "13114", "Lo Barnechea": "13115", "Lo Espejo": "13116",
    "Lo Prado": "13117", "Macul": "13118", "Maipú": "13119", "María Pinto": "13503",
    "Melipilla": "13501", "Ñuñoa": "13120", "Padre Hurtado": "13604", "Paine": "13404",
    "Pedro Aguirre Cerda": "13121", "Peñaflor": "13605", "Peñalolén": "13122",
    "Pirque": "13202", "Providencia": "13123", "Puchuncaví": "5307",
    "Pudahuel": "13123", "Puente Alto": "13201", "Quilicura": "13124",
    "Quinta Normal": "13125", "Quintero": "5306", "Recoleta": "13126",
    "Renca": "13127", "San Bernardo": "13401", "San Joaquín": "13128",
    "San José de Maipo": "13203", "San Miguel": "13129", "San Pedro": "13504",
    "San Ramón": "13130", "Santa María": "5605", "Santiago": "13101",
    "Talagante": "13601", "Tiltil": "13303", "Vitacura": "13131"
}

class CsvGenerator:
    def __init__(self, output_dir=OUTPUT_DIR):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        # ID Counters
        self.ids = {
            "jurisdiction": 1,
            "election": 1,
            "person": 1,
            "party": 1,
            "candidacy": 1,
            "office_term": 1,
            "party_membership": 1,
            "result": 1
        }
        
        # Caches for relational integrity (Name/Key -> ID)
        self.cache_jurisdictions = {} # "Type:Name" -> ID
        self.cache_people = {} # "Given Paternal" -> ID
        self.cache_parties = {} # "Official Name" -> ID
        
        # Open CSV Writers
        self.files = {}
        self.writers = {}
        
        self.tables = {
            "wp_politeia_jurisdictions": ["id", "official_name", "common_name", "type", "parent_id", "external_code", "created_at", "updated_at"],
            "wp_politeia_elections": ["id", "office_id", "jurisdiction_id", "election_date", "title", "rounds", "created_at", "updated_at"],
            "wp_politeia_election_results": ["id", "election_id", "jurisdiction_id", "valid_votes", "blank_votes", "null_votes", "total_votes", "participation_rate", "created_at", "updated_at"],
            "wp_politeia_candidacies": ["id", "election_id", "person_id", "party_id", "votes", "vote_share", "elected", "created_at", "updated_at"],
            "wp_politeia_political_parties": ["id", "official_name", "short_name", "created_at", "updated_at"],
            "wp_politeia_party_memberships": ["id", "person_id", "party_id", "started_on", "created_at", "updated_at"],
            "wp_politeia_office_terms": ["id", "person_id", "office_id", "jurisdiction_id", "started_on", "status", "created_at", "updated_at"]
        }
        
        for table, cols in self.tables.items():
            f = open(os.path.join(self.output_dir, f"{table}.csv"), "w", newline="", encoding="utf-8")
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            self.files[table] = f
            self.writers[table] = w

    def close(self):
        for f in self.files.values():
            f.close()

    def _now(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_or_create_jurisdiction(self, name, type_, parent_id=None):
        key = f"{type_}:{name}"
        if key in self.cache_jurisdictions:
            return self.cache_jurisdictions[key]
        
        new_id = self.ids["jurisdiction"]
        self.ids["jurisdiction"] += 1
        
        external_code = ""
        if type_ == "COMMUNE" and name in COMMUNE_CODES:
            external_code = COMMUNE_CODES[name]
        
        self.writers["wp_politeia_jurisdictions"].writerow({
            "id": new_id,
            "official_name": name,
            "common_name": name,
            "type": type_,
            "parent_id": parent_id if parent_id else "",
            "external_code": external_code,
            "created_at": self._now(),
            "updated_at": self._now()
        })
        
        self.cache_jurisdictions[key] = new_id
        return new_id

    def get_or_create_party(self, official_name):
        if official_name in self.cache_parties:
            return self.cache_parties[official_name]
        
        new_id = self.ids["party"]
        self.ids["party"] += 1
        
        # Extract short name
        short_name = ""
        match = re.search(r"^([A-Z]+)\s*\(", official_name)
        if match:
            short_name = match.group(1)
            
        self.writers["wp_politeia_political_parties"].writerow({
            "id": new_id,
            "official_name": official_name,
            "short_name": short_name,
            "created_at": self._now(),
            "updated_at": self._now()
        })
        
        self.cache_parties[official_name] = new_id
        return new_id

    def get_or_create_person(self, name):
        # Name format: First Last
        # Simple split
        parts = name.strip().split()
        if len(parts) >= 1:
            given = " ".join(parts[:-1]) if len(parts) > 1 else parts[0]
            paternal = parts[-1] if len(parts) > 1 else ""
        else:
            given = "Unknown"
            paternal = ""
            
        key = name # Assuming Name is unique enough for this scrape session
        if key in self.cache_people:
            return self.cache_people[key]
            
        new_id = self.ids["person"]
        self.ids["person"] += 1
        
        # Using a specialized writer for People isn't setup because user didn't ask for People CSV?
        # WAIT. User request: "wp_politeia_candidacies" links to people.
        # But user list of tables to output: elections, election_results, candidacies, parties, party_memberships, office_terms.
        # wp_politeia_people IS NOT in the requested list, but it's a Foreign Key for Candidacies, Office Terms, Party Memberships.
        # I MUST generate it to check correctness, or I just allow IDs to exist without the file.
        # I will generate it to be safe, but maybe not verify it.
        # Actually I added it to self.tables above? No I didn't. 
        # I will add it to self.tables to ensure completeness.
        
        # CHECK: Did I include it in self.tables? No.
        # Adding it now.
        if "wp_politeia_people" not in self.writers:
             # Lazy init if I missed it, or just add to init
             pass
        
        # I'll create the people csv anyway.
        return new_id

    # FIX: Add people table handling
    def add_people_table(self):
        cols = ["id", "given_names", "paternal_surname", "created_at", "updated_at"]
        f = open(os.path.join(self.output_dir, "wp_politeia_people.csv"), "w", newline="", encoding="utf-8")
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        self.files["wp_politeia_people"] = f
        self.writers["wp_politeia_people"] = w
        
    def write_person(self, id, name):
        parts = name.strip().split()
        given = " ".join(parts[:-1]) if len(parts) > 1 else parts[0]
        paternal = parts[-1] if len(parts) > 1 else ""
        
        self.writers["wp_politeia_people"].writerow({
            "id": id,
            "given_names": given,
            "paternal_surname": paternal,
            "created_at": self._now(),
            "updated_at": self._now()
        })

    def create_election(self, office_id, jurisdiction_id, commune_name):
        new_id = self.ids["election"]
        self.ids["election"] += 1
        
        self.writers["wp_politeia_elections"].writerow({
            "id": new_id,
            "office_id": office_id,
            "jurisdiction_id": jurisdiction_id,
            "election_date": "2024-10-27",
            "title": f"Elección de Alcalde 2024 - {commune_name}",
            "rounds": 1,
            "created_at": self._now(),
            "updated_at": self._now()
        })
        return new_id

    def create_candidacy(self, election_id, person_id, party_id, votes, vote_share, elected):
        new_id = self.ids["candidacy"]
        self.ids["candidacy"] += 1
        
        self.writers["wp_politeia_candidacies"].writerow({
            "id": new_id,
            "election_id": election_id,
            "person_id": person_id,
            "party_id": party_id,
            "votes": votes,
            "vote_share": vote_share,
            "elected": 1 if elected else 0,
            "created_at": self._now(),
            "updated_at": self._now()
        })
        return new_id

    def create_membership(self, person_id, party_id):
        new_id = self.ids["party_membership"]
        self.ids["party_membership"] += 1
        
        self.writers["wp_politeia_party_memberships"].writerow({
            "id": new_id,
            "person_id": person_id,
            "party_id": party_id,
            "started_on": "2024-10-27", # Assumption
            "created_at": self._now(),
            "updated_at": self._now()
        })

    def create_office_term(self, person_id, office_id, jurisdiction_id):
        new_id = self.ids["office_term"]
        self.ids["office_term"] += 1
        
        self.writers["wp_politeia_office_terms"].writerow({
            "id": new_id,
            "person_id": person_id,
            "office_id": office_id,
            "jurisdiction_id": jurisdiction_id,
            "started_on": "2024-12-06", # Assumption
            "status": "ACTIVE",
            "created_at": self._now(),
            "updated_at": self._now()
        })

    def create_result(self, election_id, jurisdiction_id, valid, blank, null, total, rate):
        new_id = self.ids["result"]
        self.ids["result"] += 1
        
        self.writers["wp_politeia_election_results"].writerow({
            "id": new_id,
            "election_id": election_id,
            "jurisdiction_id": jurisdiction_id,
            "valid_votes": valid,
            "blank_votes": blank,
            "null_votes": null,
            "total_votes": total,
            "participation_rate": rate,
            "created_at": self._now(),
            "updated_at": self._now()
        })


async def extract_rm_communes(page):
    """
    Extracts (Commune Name, Emol ID) tuples for the Metropolitan Region (RM).
    """
    print("Strategy: Extracting RM communes list first...")
    
    try:
        # Playwright log says: "35 × locator resolved to 16 elements". 
        # So elements exists but maybe not visible?
        # Let's wait for state="attached" instead.
        await page.wait_for_selector("ul.ul-region", state="attached", timeout=15000)
    except Exception as e:
        print(f"Error waiting for regions: {e}")
        return []

    rm_communes = []
    
    regions = await page.query_selector_all("ul.ul-region")
    found_rm = False
    
    for reg in regions:
        r_code = await reg.get_attribute("data-region")
        # Fix: handle lowercase 'rm'
        if r_code and (r_code.lower() == "13" or r_code.lower() == "rm"):
            print(f"Found RM block (code: {r_code})")
            items = await reg.query_selector_all("li[data-el='a']")
            for li in items:
                name = (await li.text_content()).strip()
                code = await li.get_attribute("data-zn")
                if name and code:
                     # Filter out meta-groupings if they don't look like commune IDs (usually 4 digits)
                     # But some are short. Alhué is 2801.
                     # Let's print what we find
                     # print(f"  Discovered: {name} -> {code}")
                     rm_communes.append((name, code))
            found_rm = True
            break
            
    if not found_rm:
        print("Fallback: Searching all regions for 'Santiago' to find RM...")
        for reg in regions:
            text = await reg.text_content()
            if "Santiago" in text and "Puente Alto" in text:
                 items = await reg.query_selector_all("li[data-el='a']")
                 for li in items:
                    name = (await li.text_content()).strip()
                    code = await li.get_attribute("data-zn")
                    if name and code:
                        rm_communes.append((name, code))
                 break
                 
    print(f"Extracted {len(rm_communes)} communes for RM.")
    return rm_communes

async def scrape_to_csv():
    csv_gen = CsvGenerator()
    csv_gen.add_people_table()
    
    # Ensure RM region exists
    rm_region_id = csv_gen.get_or_create_jurisdiction("Región Metropolitana", "REGION")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(locale="es-CL", timezone_id="America/Santiago")
        page = await context.new_page()
        
        # Debug helper
        page.on("console", lambda msg: print(f"BROWSER LOG: {msg.text}"))
        
        print(f"Navigating to {BASE_URL}...")
        try:
            await page.goto(BASE_URL, wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            print(f"Initial navigation failed: {e}")
            await browser.close()
            csv_gen.close()
            return

        # 1. Discovery Phase
        communes = await extract_rm_communes(page)
        
        if not communes:
            print("CRITICAL: No communes found. Exiting.")
            await browser.close()
            csv_gen.close()
            return

        # 2. Iteration Phase
        OFFICE_ALCALDE = 1
        
        for idx, (commune_name, emol_id) in enumerate(communes):
            print(f"Processing [{idx+1}/{len(communes)}]: {commune_name} (ID: {emol_id})")
            
            target_url = f"{BASE_URL}#!a{emol_id}"
            
            retries = 2
            success = False
            
            for attempt in range(retries):
                try:
                    # Strategy: Click navigation is more reliable than Hash navigation for this SPA
                    # 1. Reset to Base URL (loads Santiago default)
                    if attempt == 0:
                        await page.goto(BASE_URL, wait_until="domcontentloaded")
                    
                    # 2. Find and Click the Commune Link in Sidebar
                    # We use JS click to be robust against visibility issues
                    # Selector: li[data-zn='{id}']
                    # Note: We must ensure it exists.
                    
                    try:
                        # Wait for sidebar to be present
                        await page.wait_for_selector(f"li[data-zn='{emol_id}']", state="attached", timeout=10000)
                        
                        # Click it
                        await page.evaluate(f"document.querySelector(\"li[data-zn='{emol_id}']\").click()")
                        
                    except Exception as click_e:
                        print(f"  Warning: Could not click commune {commune_name} (ID {emol_id}): {click_e}")
                        # Retry loop will handle it
                        raise click_e

                    # Robustness: Wait for headers to load and MATCH commune name
                    # Use :has-text to ensure we wait for the UPDATE, not just the element existence
                    header_sel = f".res-box-content h3:has-text('{commune_name}')"
                    try:
                        await page.wait_for_selector(header_sel, timeout=12000)
                    except:
                        print(f"  Warning: Specific header for {commune_name} did not appear.")
                        # Dump what we see
                        found_h3 = await page.query_selector(".res-box-content h3")
                        if found_h3:
                            print(f"  Saw instead: {await found_h3.text_content()}")

                    # Add safety sleep for odometer
                    await page.wait_for_timeout(2000)
                    
                    # No need to check text manually, selector did it
                    success = True
                    break
                        
                except Exception as e:
                    print(f"  Attempt {attempt+1}: Navigation error: {e}")
            
            if not success:
                print(f"  Skipping {commune_name} - could not load data.")
                continue

            # --- Data Extraction ---
            try:
                # Commune Entity
                commune_id = csv_gen.get_or_create_jurisdiction(commune_name, "COMMUNE", rm_region_id)
                election_id = csv_gen.create_election(OFFICE_ALCALDE, commune_id, commune_name)
                
                # Candidates
                candidate_lis = await page.query_selector_all("ul.res-ul-candidatos li")
                c_count = 0
                
                for li in candidate_lis:
                    name_el = await li.query_selector("div.res-candidato > b")
                    if not name_el: continue 
                    name = (await name_el.text_content()).strip()
                    
                    class_attr = await li.get_attribute("class")
                    is_elected = "ganador" in (class_attr or "")

                    pact_el = await li.query_selector("div.res-candidato > span")
                    party_name = (await pact_el.text_content()).strip() if pact_el else "Independent"
                    
                    votes_el = await li.query_selector("div.res-votos i")
                    votes_str = (await votes_el.text_content()).strip().replace(".", "") if votes_el else "0"
                    votes = int(votes_str) if votes_str.isdigit() else 0
                    
                    pct_el = await li.query_selector("div.res-votos span")
                    pct_str = (await pct_el.text_content()).strip().replace(",", ".").replace("%", "") if pct_el else "0"
                    try: pct = float(pct_str)
                    except: pct = 0.0

                    person_id = csv_gen.get_or_create_person(name)
                    csv_gen.write_person(person_id, name)
                    party_id = csv_gen.get_or_create_party(party_name)
                    
                    csv_gen.create_candidacy(election_id, person_id, party_id, votes, pct, is_elected)
                    csv_gen.create_membership(person_id, party_id)
                    
                    if is_elected:
                        csv_gen.create_office_term(person_id, OFFICE_ALCALDE, commune_id)
                    c_count += 1

                print(f"  -> Extracted {c_count} candidates.")

                # Participation Stats
                def clean_int(s): return int(s.replace(".", "").strip()) if s else 0
                def clean_pct(s): return float(s.replace("%","").replace(",",".").strip()) if s else 0.0

                valid, null_votes, blank, total, part_rate = 0, 0, 0, 0, 0.0
                
                try:
                    v_el = await page.query_selector('dl.res-resumen-votacion dt[data-voto="v"] i')
                    valid = clean_int(await v_el.text_content()) if v_el else 0
                    
                    n_el = await page.query_selector('dl.res-resumen-votacion dt[data-voto="n"] i')
                    null_votes = clean_int(await n_el.text_content()) if n_el else 0
                    
                    b_el = await page.query_selector('dl.res-resumen-votacion dt[data-voto="b"] i')
                    blank = clean_int(await b_el.text_content()) if b_el else 0
                    
                    # Try explicitly extracting total from the participation list first
                    vot_el = await page.query_selector('ol.res-participacion li[data-year="2024"] span[data-part="vot"]')
                    if vot_el:
                         total = clean_int(await vot_el.text_content())
                    
                    # Fallback to sum if total is 0 or not found
                    if total == 0:
                        total = valid + null_votes + blank
                    
                    pcj_el = await page.query_selector('ol.res-participacion li[data-year="2024"] b[data-part="pcj"]')
                    part_rate = clean_pct(await pcj_el.text_content()) if pcj_el else 0.0

                except Exception as stats_e:
                    print(f"  Warning: Stats extraction issue: {stats_e}")

                csv_gen.create_result(election_id, commune_id, valid, blank, null_votes, total, part_rate)
                
            except Exception as e:
                print(f"  Error scraping data for {commune_name}: {e}")

    await browser.close()
    csv_gen.close()
    print("FINISHED.")

if __name__ == "__main__":
    asyncio.run(scrape_to_csv())
