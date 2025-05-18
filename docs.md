**1. Úvod**

Measurement API je RESTful služba navržená pro správu měření a jejich konfigurací. Umožňuje klientům vytvářet, číst a spravovat data týkající se různých typů měření, včetně snímků z RGB a HSI kamer, akustických dat a souvisejících konfiguračních parametrů. API je postaveno pomocí frameworku FastAPI a využívá asynchronní SQLAlchemy pro interakci s databází PostgreSQL.

**2. Chybové kódy**

API používá standardní HTTP stavové kódy k indikaci úspěchu nebo selhání operací:

*   `200 OK`: Požadavek byl úspěšně zpracován.
*   `201 Created`: Nový zdroj byl úspěšně vytvořen.
*   `404 Not Found`: Požadovaný zdroj nebyl nalezen.
*   `422 Unprocessable Entity`: Požadavek byl sice syntakticky správný, ale obsahoval sémantické chyby (např. nevalidní data). Toto je obvykle zpracováváno FastAPI automaticky pro Pydantic modely.
*   `500 Internal Server Error`: Došlo k neočekávané chybě na serveru. Odpověď bude obsahovat JSON objekt s klíči `status: "error"` a `message: "popis chyby"`.

**3. Nastavení databáze**

API vyžaduje připojení k databázi PostgreSQL. Připojovací řetězec je konfigurován prostřednictvím proměnné prostředí `DATABASE_URL` v souboru `settings.py`.

**4. CORS (Cross-Origin Resource Sharing)**

API má povolený CORS pro všechny zdroje (`allow_origins=["*"]`), metody a hlavičky, což umožňuje požadavky z jakékoli domény.

**5. Definice Endpointů**

Následuje detailní popis jednotlivých dostupných endpointů.

---

**5.1. Diagnostika a Schéma**

**5.1.1. Kontrola dostupnosti databáze**

*   **Endpoint:** `GET /check-db`
*   **Popis:** Tento endpoint slouží k ověření, zda je API schopno úspěšně komunikovat s databází. Provede jednoduchý dotaz `SELECT NOW()` a vrátí aktuální čas databázového serveru.
*   **Parametry:** Žádné.
*   **Tělo požadavku:** Žádné.
*   **Úspěšná odpověď (200 OK):**

```json
{
    "status": "ok",
    "result": {
        "now": "YYYY-MM-DDTHH:MM:SS.ssssssZ"
    }
}
```

*   **Chybová odpověď (500 Internal Server Error):**

```json
{
    "status": "error",
    "message": "Popis chyby připojení k databázi"
}
```

**5.1.2. Získání schématu databáze**

*   **Endpoint:** `GET /db-schema`
*   **Popis:** Načte a vrátí kompletní schéma veřejné části databáze. Pro každou tabulku ve schématu `public` vypíše seznam jejích sloupců a jejich datových typů. To je užitečné pro pochopení struktury databáze bez přímého přístupu.
*   **Parametry:** Žádné.
*   **Tělo požádavku:** Žádné.
*   **Úspěšná odpověď (200 OK):**

```json
{
    "status": "ok",
    "schema": {
        "nazev_tabulky_1": [
            {"name": "nazev_sloupce_1", "type": "datovy_typ_1"},
            {"name": "nazev_sloupce_2", "type": "datovy_typ_2"}
        ],
        "nazev_tabulky_2": [
            // ... další sloupce
        ]
    }
}
```

*   **Chybová odpověď (500 Internal Server Error):**

```json
{
    "status": "error",
    "message": "Popis chyby při načítání schématu"
}
```

---

**5.2. Správa Měření (Measurements)**

**5.2.1. Získání všech měření**

*   **Endpoint:** `GET /measurements`
*   **Popis:** Načte a vrátí seznam všech záznamů o měřeních uložených v databázi. Každý záznam obsahuje všechny atributy daného měření.
*   **Parametry:** Žádné.
*   **Tělo požadavku:** Žádné.
*   **Úspěšná odpověď (200 OK):**

```json
{
    "measurements": [
        {
            "id": 1,
            "snapshot_rgb_camera": "base64_encoded_string_nebo_null",
            "snapshot_hsi_camera": "base64_encoded_string_nebo_null",
            "acustic": 123,
            "config_id": 1,
            "created_at": "YYYY-MM-DDTHH:MM:SS.ssssss"
        }
        // ... další měření
    ]
}
```

*   **Chybová odpověď (500 Internal Server Error):**

```json
{
    "status": "error",
    "message": "Popis chyby při načítání měření"
}
```

**5.2.2. Vytvoření nového měření**

*   **Endpoint:** `POST /measurements`
*   **Popis:** Umožňuje vytvořit nový záznam o měření. Data pro měření jsou předávána jako parametry dotazu nebo data formuláře. Čas vytvoření (`created_at`) je automaticky nastaven na aktuální čas serveru při vkládání do databáze. Pokud jsou hodnoty pro `snapshot_rgb_camera` nebo `snapshot_hsi_camera` řetězce "None", jsou v databázi uloženy jako `NULL`.
*   **Parametry (Query/Form data):**
    *   `snapshot_rgb_camera` (string, volitelné): Snímek z RGB kamery kódovaný v Base64.
    *   `snapshot_hsi_camera` (string, volitelné): Snímek z HSI kamery kódovaný v Base64.
    *   `acustic` (integer, volitelné): Akustická hodnota měření.
    *   `config_id` (integer, volitelné): ID související konfigurace.
    *   `created_at` (datetime, volitelné): Tento parametr je v aktuální implementaci přítomen v signatuře funkce, ale jeho hodnota je při vkládání do databáze ignorována a nahrazena aktuálním časem serveru.
*   **Tělo požadavku:** Žádné (data jsou v parametrech).
*   **Úspěšná odpověď (201 Created):**

```json
{
    "measurement": [ // Poznámka: vrací pole s jedním prvkem
        {
            "id": 2,
            "snapshot_rgb_camera": "base64...",
            "snapshot_hsi_camera": null,
            "acustic": 456,
            "config_id": 1,
            "created_at": "YYYY-MM-DDTHH:MM:SS.ssssss"
        }
    ]
}
```

*   **Chybová odpověď (500 Internal Server Error):**

```json
{
    "status": "error",
    "message": "Popis chyby při vytváření měření"
}
```

**5.2.3. Získání měření podle ID**

*   **Endpoint:** `GET /measurement/{measurement_id}`
*   **Popis:** Načte a vrátí konkrétní záznam o měření na základě jeho unikátního ID.
*   **Parametry cesty:**
    *   `measurement_id` (integer, povinné): ID požadovaného měření.
*   **Tělo požadavku:** Žádné.
*   **Úspěšná odpověď (200 OK):**

```json
{
    "measurement": {
        "id": 1,
        "snapshot_rgb_camera": "base64...",
        "snapshot_hsi_camera": null,
        "acustic": 123,
        "config_id": 1,
        "created_at": "YYYY-MM-DDTHH:MM:SS.ssssss"
    }
}
```

*   **Chybové odpovědi:**
    *   `404 Not Found`: Pokud měření s daným ID neexistuje.

```json
{
    "status": "error",
    "message": "Measurement with id {measurement_id} not found"
}
```

    *   `500 Internal Server Error`: Při jiné chybě.

**5.2.4. Získání měření podle ID konfigurace**

*   **Endpoint:** `GET /measurement/config/{config_id}`
*   **Popis:** Načte a vrátí seznam všech měření, která jsou asociována s konkrétním ID konfigurace. To umožňuje filtrovat měření na základě konfigurace, se kterou byla pořízena.
*   **Parametry cesty:**
    *   `config_id` (integer, povinné): ID konfigurace, pro kterou se mají načíst měření.
*   **Tělo požadavku:** Žádné.
*   **Úspěšná odpověď (200 OK):**

```json
{
    "measurement": [
        {
            "id": 1,
            "snapshot_rgb_camera": "base64...",
            "snapshot_hsi_camera": null,
            "acustic": 123,
            "config_id": 1, // Bude shodné s config_id v URL
            "created_at": "YYYY-MM-DDTHH:MM:SS.ssssss"
        }
        // ... další měření pro dané config_id
    ]
}
```

*   **Chybové odpovědi:**
    *   `404 Not Found`: Pokud pro dané `config_id` neexistují žádná měření.

```json
{
    "status": "error",
    "message": "Measurement with config id {config_id} not found"
}
```

    *   `500 Internal Server Error`: Při jiné chybě.

---

**5.3. Správa Konfigurací (Config)**

**5.3.1. Získání všech konfigurací**

*   **Endpoint:** `GET /config`
*   **Popis:** Načte a vrátí seznam všech konfiguračních záznamů uložených v databázi. Každý záznam obsahuje parametry dané konfigurace.
*   **Parametry:** Žádné.
*   **Tělo požadavku:** Žádné.
*   **Úspěšná odpověď (200 OK):**

```json
{
    "config": [
        {
            "id": 1,
            "interval_value": 60,
            "frequency": 10.5,
            "rgb_camera": true,
            "hsi_camera": false,
            "created_at": "YYYY-MM-DDTHH:MM:SS.ssssss"
        }
        // ... další konfigurace
    ]
}
```

*   **Chybová odpověď (500 Internal Server Error):**

```json
{
    "status": "error",
    "message": "Popis chyby při načítání konfigurací"
}
```

**5.3.2. Vytvoření nové konfigurace**

*   **Endpoint:** `POST /config`
*   **Popis:** Umožňuje vytvořit nový konfigurační záznam. Data pro konfiguraci jsou předávána v těle požadavku ve formátu JSON a validována podle modelu `ConfigCreateRequest`. Čas vytvoření (`created_at`) je automaticky nastaven na aktuální čas serveru.
*   **Parametry:** Žádné.
*   **Tělo požadavku (JSON, model `ConfigCreateRequest`):**

```json
{
    "interval_value": 120, // integer, povinné
    "frequency": 20.0, // float, volitelné
    "rgb_camera": false, // boolean, volitelné
    "hsi_camera": true // boolean, volitelné
}
```

*   **Úspěšná odpověď (201 Created):**

```json
{
    "config": [ // Poznámka: vrací pole s jedním prvkem
        {
            "id": 2,
            "interval_value": 120,
            "frequency": 20.0,
            "rgb_camera": false,
            "hsi_camera": true,
            "created_at": "YYYY-MM-DDTHH:MM:SS.ssssss"
        }
    ]
}
```

*   **Chybové odpovědi:**
    *   `422 Unprocessable Entity`: Pokud tělo požadavku neodpovídá schématu `ConfigCreateRequest`.
    *   `500 Internal Server Error`: Při jiné chybě.

**5.3.3. Získání konfigurace podle ID**

*   **Endpoint:** `GET /config/{config_id}`
*   **Popis:** Načte a vrátí konkrétní konfigurační záznam na základě jeho unikátního ID.
*   **Parametry cesty:**
    *   `config_id` (integer, povinné): ID požadované konfigurace.
*   **Tělo požadavku:** Žádné.
*   **Úspěšná odpověď (200 OK):**

```json
{
    "config": {
        "id": 1,
        "interval_value": 60,
        "frequency": 10.5,
        "rgb_camera": true,
        "hsi_camera": false,
        "created_at": "YYYY-MM-DDTHH:MM:SS.ssssss"
    }
}
```

*   **Chybové odpovědi:**
    *   `404 Not Found`: Pokud konfigurace s daným ID neexistuje.

```json
{
    "status": "error",
    "message": "Config with id {config_id} not found"
}
```

    *   `500 Internal Server Error`: Při jiné chybě.
