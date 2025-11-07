# 🕉️ Bhajan Search - Streamlit App

Šī ir bhajanu meklētāja aplikācija ar fiksētu bhajanu kolekciju. Aplikācija ielādē datus no `Bhajans.xlsx` faila un ļauj meklēt bhajanus pēc nosaukuma, kategorijas vai autora.

## 📋 Prasības

- Python 3.8 vai jaunāks
- pip (Python package manager)

## 🚀 Instalācija un palaišana

### 1. Lejupielādējiet failus

Jums nepieciešami šie faili:
- `bhajan_streamlit_app.py` (galvenā aplikācijas faila)
- `data_loader.py` (datu ielādētāja modulis)
- `Bhajans.xlsx` (jūsu bhajanu datu fails)
- `requirements.txt` (Python bibliotēku saraksts)

### 2. Instalējiet nepieciešamās bibliotēkas

```bash
pip install -r requirements.txt
```

Vai manuāli:
```bash
pip install streamlit pandas openpyxl
```

### 3. Pārliecinieties, ka Bhajans.xlsx ir tajā pašā mapē

Failu struktūrai jābūt:
```
bhajan-search/
├── bhajan_streamlit_app.py
├── data_loader.py
├── Bhajans.xlsx          # Svarīgi: šim failam jābūt šeit!
├── requirements.txt
└── README.md
```

### 4. Palaidiet aplikāciju

```bash
streamlit run bhajan_streamlit_app.py
```

### 5. Atveriet aplikāciju

Aplikācija atvērsies jūsu pārlūkprogrammā adresē: `http://localhost:8501`

## 📊 Excel faila formāts

Jūsu Excel failam jābūt šādām kolonnām:

| Category | Bhajan_Title | Author | Verse_Number | Original | English | Russian | Latvian |
|----------|-------------|--------|--------------|----------|---------|---------|---------|
| Śrī Guru | Śrī Guru-paramparā | Śrīla Bhaktisiddhānta... | 1 | kṛṣṇa hôite... | In the beginning... | В начале... | Radīšanas sākumā... |

### Kolonnu apraksti:

- **Category**: Bhajana kategorija (piem., "Śrī Guru", "Śrī Kṛṣṇa")
- **Bhajan_Title**: Bhajana nosaukums
- **Author**: Autora vārds
- **Verse_Number**: Panta numurs (1, 2, 3, utt.)
- **Original**: Oriģināls teksts sanskritā/bengali
- **English**: Tulkojums angļu valodā
- **Russian**: Tulkojums krievu valodā (optional)
- **Latvian**: Tulkojums latviešu valodā (optional)

### ⚠️ **Datu kvalitātes prasības:**

- **Nav tukšu šūnu**: Category, Bhajan_Title, Author kolonnas nedrīkst būt tukšas
- **Verse_Number**: Jābūt skaitlim (1, 2, 3...)
- **Nav dublējošu pantu**: Katram bhajanam katrs Verse_Number drīkst būt tikai vienreiz
- **UTF-8 encoding**: Saglabājiet Excel failu ar UTF-8 kodējumu diakritiskajām zīmēm

### 🧹 **Automātiskā teksta tīrīšana:**

Aplikācija automātiski notīra:
- ✅ `_x000D_` simbolus (Excel line break artefakti)
- ✅ Liekos atstarpes un tukšas rindas
- ✅ Nederīgos rakstzīmju kodējumus
- ✅ Saglabā pareizos line breaks sanskrita/bengali pantiem

## 🎯 Aplikācijas funkcijas

### 🏠 Sākuma lapa
- Trīs galvenās navegācijas opcijas (pogas)
- Statistika par bhajanu kolekciju

### 📚 Meklēšanas opcijas
1. **By Title: A-Z** - visi bhajani alfabētiskā secībā
   - **Bhajana nosaukums** = hipersaite uz bhajanu
   - **👤 Autora vārds** = hipersaite uz autora visiem bhajaniem

2. **By Category** - bhajani grupēti pēc kategorijām  
   - **Kategorija (skaits)** = hipersaite uz kategorijas bhajaniem

3. **By Author** - bhajani grupēti pēc autoriem
   - **Autors (skaits)** = hipersaite uz autora bhajaniem

### 📖 Bhajana apskatīšana
- Nosaukums un autors
- Kategorijas norāde
- **4 valodu atbalsts**: 
  - 📜 Original (Sanskrit/Bengali)
  - 🇬🇧 English 
  - 🇷🇺 Русский (Russian)
  - 🇱🇻 Latviešu (Latvian)
- **Verse numuri** redzami visās valodās
- Skaidrs, lasāms izkārtojums ar versiem

### 🔗 Interaktīvā navigācija
- **Nav "View" vai "Browse" pogu** - viss darbojas ar hipersaitēm
- **Bhajanu nosaukumi** ved tieši uz bhajanu saturu
- **Autoru vārdi** ved uz autora bhajanu sarakstu
- **Kategorijas** ved uz kategorijas bhajanu sarakstu

### 📱 Responsīvs dizains
- Optimizēts gan datoriem, gan mobilajām ierīcēm
- Mūsdienīgs, tīrs dizains
- Viegla navigācija

## 🌐 GitHub + Streamlit Community Cloud izvietošana

### 1. Izveidojiet GitHub repozitoriju
1. Dodieties uz [github.com](https://github.com) 
2. Izveidojiet jaunu public repozitoriju `bhajan-search-app`
3. Augšupielādējiet visus failus:
   - `bhajan_streamlit_app.py`
   - `data_loader.py` 
   - `Bhajans.xlsx`
   - `requirements.txt`
   - `README.md`

### 2. Izvietojiet Streamlit Community Cloud
1. Dodieties uz [share.streamlit.io](https://share.streamlit.io)
2. Piesakieties ar GitHub kontu
3. Izveidojiet jaunu aplikāciju:
   - **Repository:** `jūsu-lietotājvārds/bhajan-search-app`
   - **Branch:** `main`  
   - **Main file path:** `bhajan_streamlit_app.py`
4. Nospiediet "Deploy!"

### 3. Rezultāts
Jūs iegūsiet publisko URL: `https://jūsu-app.streamlit.app`

## 📁 Bhajanu kolekcijas paplašināšana

Lai pievienotu jaunus bhajanus:

1. Atveriet `Bhajans.xlsx` Excel failā
2. Pievienojiet jaunas rindas ar bhajanu datiem
3. Saglabājiet failu
4. Ja izmantojat GitHub, augšupielādējiet atjaunināto failu
5. Streamlit automātiski atjauninās aplikāciju

### Piemērs jaunai rindai:
| Category | Bhajan_Title | Author | Verse_Number | Original | English |
|----------|-------------|--------|--------------|----------|---------|
| Śrī Kṛṣṇa | Govinda Jaya Jaya | Traditional | 1 | govinda jaya jaya... | All glories to Govinda... |

## 🔧 Pielāgošana

### Dizaina maiņa
CSS stili ir definēti `bhajan_streamlit_app.py` failā. Varat pielāgot:
- Krāsas
- Fontus
- Izliktum
- Animācijas

### Funkcionalitātes paplašināšana
Varat pievienot:
- Meklēšanas funkciju
- Favorītu sistēmu
- Print/PDF opcijas
- Audio atskaņošanu
- Komentāru sistēmu

## ⚠️ Svarīgi

1. **Excel faila nosaukums:** Failam obligāti jābūt `Bhajans.xlsx`
2. **Kolonnu nosaukumi:** Izmantojiet tieši tos pašus nosaukumus kā parādīts
3. **Failu izvietojums:** Visi faili jābūt vienā mapē
4. **Encoding:** Pārliecinieties, ka Excel fails ir saglabāts UTF-8 formātā

## 📞 Problēmu risināšana

### Aplikācija nesākas
```bash
# Pārbaudiet Python versiju
python --version

# Pārinstalējiet bibliotēkas
pip install --upgrade streamlit pandas openpyxl
```

### Excel fails netiek atrasts
- Pārliecinieties, ka `Bhajans.xlsx` ir tajā pašā mapē kā `.py` faili
- Pārbaudiet faila nosaukumu (lietot/mazie burti ir svarīgi)

### Dati neparādās pareizi
- Atveriet Excel failu un pārbaudiet kolonnu nosaukumus
- Pārliecinieties, ka nav tukšu rindu starp datiem

## 🙏 Pateicības

Šī aplikācija ir veidota, lai palīdzētu bhakti kopienu dalīties un meklēt svētās dziesmas un mantras. 

**Hare Kṛṣṇa! 🕉️**
