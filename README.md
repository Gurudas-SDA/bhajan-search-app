# 🕉️ Bhajan Search - Streamlit App

Šī ir bhajanu meklētāja aplikācija, kas izveidota ar Streamlit. Aplikācija ļauj jums ielādēt Excel failu ar bhajanu datiem un meklēt bhajanus pēc nosaukuma, kategorijas vai autora.

## 📋 Prasības

- Python 3.8 vai jaunāks
- pip (Python package manager)

## 🚀 Instalācija un palaišana

### 1. Instalējiet nepieciešamās bibliotēkas

```bash
pip install -r requirements.txt
```

Vai manuāli:
```bash
pip install streamlit pandas openpyxl
```

### 2. Palaidiet aplikāciju

```bash
streamlit run bhajan_streamlit_app.py
```

### 3. Atveriet aplikāciju

Pēc komandas izpildes jūsu pārlūkprogrammā automātiski atvērsies aplikācija adresē: `http://localhost:8501`

## 📂 Failu struktūra

```
bhajan-search/
├── bhajan_streamlit_app.py    # Galvenā aplikācijas faila
├── data_loader.py             # Datu ielādētāja modulis
├── requirements.txt           # Python bibliotēku saraksts
└── README.md                  # Šis fails
```

## 📊 Excel faila formāts

Jūsu Excel failam jābūt šādām kolonnām:

| Category | Bhajan_Title | Author | Verse_Number | Original | English |
|----------|-------------|--------|--------------|----------|---------|
| Śrī Guru | Śrī Guru-paramparā | Śrīla Bhaktisiddhānta... | 1 | kṛṣṇa hôite... | In the beginning... |

### Kolonnu apraksti:

- **Category**: Bhajana kategorija (piem., "Śrī Guru", "Śrī Kṛṣṇa")
- **Bhajan_Title**: Bhajana nosaukums
- **Author**: Autora vārds
- **Verse_Number**: Panta numurs (1, 2, 3, utt.)
- **Original**: Oriģināls teksts sanskritā/bengali
- **English**: Tulkojums angļu valodā

## 🎯 Aplikācijas funkcijas

### 🏠 Sākuma lapa
- Faila augšupielāde
- Trīs galvenās navegācijas opcijas
- Statistika par bhajanu skaitu

### 📚 Meklēšanas opcijas
1. **By Title: A-Z** - visi bhajani alfabētiskā secībā
2. **By Category** - bhajani grupēti pēc kategorijām  
3. **By Author** - bhajani grupēti pēc autoriem

### 📖 Bhajana apskatīšana
- Nosaukums un autors
- Kategorijas norāde
- Pārslēgšanās starp oriģinālu un angļu valodu
- Skaidrs, lasāms izkārtojums ar versiem

### 📱 Responsīvs dizains
- Optimizēts gan datoriem, gan mobilajām ierīcēm
- Mūsdienīgs, tīrs dizains
- Viegla navigācija

## 🔧 Pielāgošana

### Datu avotu maiņa
Ja vēlaties izmantot citu datu avotu, rediģējiet `data_loader.py` failu un pielāgojiet `load_bhajan_data_from_excel()` funkciju.

### Dizaina pielāgošana
CSS stili ir definēti `bhajan_streamlit_app.py` failā. Varat tos pielāgot savām vajadzībām.

### Jaunu funkciju pievienošana
Aplikācija ir modulāri uzbudēta, tāpēc jūs viegli varat pievienot jaunas funkcijas, piemēram:
- Meklēšana pēc atslēgvārdiem
- Favorītu sistēma
- Audio atskaņošana
- PDF eksports

## 🚀 Izvietošana (Deployment)

### Streamlit Community Cloud
1. Ielieciet kodu GitHub repozitorijā
2. Dodieties uz [share.streamlit.io](https://share.streamlit.io)
3. Izveidojiet kontu un savienojiet ar GitHub
4. Izvēlieties savu repozitoriju un palaidiet

### Heroku
1. Izveidojiet `Procfile` ar saturu: `web: streamlit run bhajan_streamlit_app.py --server.port=$PORT --server.address=0.0.0.0`
2. Izvietojiet kā parasto Heroku aplikāciju

### Docker
Varat izveidot Docker konteineru ar Python un Streamlit vidi.

## 📞 Atbalsts

Ja jums ir jautājumi vai problēmas, lūdzu:
1. Pārbaudiet failu formātus
2. Pārliecinieties, ka visas bibliotēkas ir instalētas
3. Pārbaudiet kļūdu ziņojumus terminālā

## 🙏 Pateicības

Šī aplikācija ir veidota, lai palīdzētu bhakti kopienu dalīties un meklēt svētās dziesmas un mantras. Izmantojiet ar mīlestību un godu pret tradīciju.

**Hare Kṛṣṇa! 🕉️**
