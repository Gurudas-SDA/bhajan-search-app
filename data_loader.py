import pandas as pd
import json
import streamlit as st
from pathlib import Path

@st.cache_data
def load_bhajan_data_from_excel(excel_file_path=None):
    """
    Load bhajan data from Excel file or use default data
    
    Args:
        excel_file_path (str): Path to the Excel file containing bhajan data
    
    Returns:
        list: List of bhajan dictionaries
    """
    
    if excel_file_path and Path(excel_file_path).exists():
        try:
            # Read Excel file
            df = pd.read_excel(excel_file_path)
            
            # Clean the data - remove rows with missing critical data
            df = df.dropna(subset=['Bhajan_Title', 'Author', 'Category'])
            
            # Fill missing values with empty strings for text fields
            df['Original'] = df['Original'].fillna('')
            df['English'] = df['English'].fillna('')
            
            # Ensure Verse_Number is numeric and handle missing values
            df['Verse_Number'] = pd.to_numeric(df['Verse_Number'], errors='coerce')
            df = df.dropna(subset=['Verse_Number'])
            df['Verse_Number'] = df['Verse_Number'].astype(int)
            
            # Process the data
            bhajans = {}
            for _, row in df.iterrows():
                title = str(row['Bhajan_Title']).strip()
                author = str(row['Author']).strip()
                category = str(row['Category']).strip()
                
                # Skip if any critical field is empty
                if not title or not author or not category or title.lower() == 'nan' or author.lower() == 'nan':
                    continue
                    
                if title not in bhajans:
                    bhajans[title] = {
                        'title': title,
                        'author': author,
                        'category': category,
                        'verses': []
                    }
                
                bhajans[title]['verses'].append({
                    'number': int(row['Verse_Number']),
                    'original': str(row['Original']).strip(),
                    'english': str(row['English']).strip()
                })
            
            # Sort verses by number for each bhajan
            for title in bhajans:
                bhajans[title]['verses'].sort(key=lambda x: x['number'])
            
            # Convert to list and filter out empty bhajans
            result = [bhajan for bhajan in bhajans.values() if bhajan['verses']]
            return result
            
        except Exception as e:
            st.error(f"Error reading Excel file: {e}")
            return get_default_data()
    
    else:
        # Use default sample data
        return get_default_data()

def get_default_data():
    """
    Return default sample bhajan data
    """
    return [
        {
            "title": "Śrī Guru-paramparā",
            "author": "Śrīla Bhaktisiddhānta Sarasvatī Gosvāmī Prabhupāda",
            "category": "Śrī Guru",
            "verses": [
                {
                    "number": 1,
                    "original": "kṛṣṇa hôite catur-mukha, haya kṛṣṇa-sevonmukha,\nbrahmā hôite nāradera mati\nnārada hôite vyāsa, madhva kahe vyāsa-dāsa,\npūrṇaprajña padmanābha-gati (1)",
                    "english": "In the beginning of creation Śrī Kṛṣṇa spoke the science of devotional service to Lord Brahmā. He in turn passed these teachings on to Śrī Nārada Muni, who accepted Śrī Kṛṣṇa Dvaipāyana Vyāsadeva as his disciple. Śrī Vyāsa transmitted this knowledge to Śrī Madhvācārya, who is also known as Pūrṇaprajña Tīrtha and who is the sole refuge for his disciple Śrī Padmanābha Tīrtha."
                },
                {
                    "number": 2,
                    "original": "nṛhari-mādhava-vaṁśe, akṣobhya-paramahaṁse,\nśiṣya bôli' aṅgīkāra kare\nakṣobhyera śiṣya 'jaya-tīrtha' nāme paricaya,\ntā̃'ra dāsye jñānasindhu tare (2)",
                    "english": "Following forth from Śrī Madhvācārya were Nṛhari Tīrtha, Śrī Mādhava Tīrtha, and then the swan-like Śrī Akṣobhya Tīrtha. The principal disciple of Śrī Akṣobhyatīrtha was known as Śrī Jayatīrtha, and Śrī Jñānasindhu was his servant."
                },
                {
                    "number": 3,
                    "original": "tā̃hā hôite dayānidhi, tā̃'ra dāsa vidyānidhi,\nrājendra hôilô tā̃hā ha'te\ntā̃hāra kiṅkara 'jaya-dharma' nāme paricaya,\nparamparā jānô bhālô-mate (3)",
                    "english": "The paramparā continued with Śrī Dayānidhi, then his disciple Śrī Vidyānidhi, and next with Śrī Rājendra Tīrtha, whose servant was Śrī Jayadharma, also known as Śrī Vijayadhvaja Tīrtha. Know well that this is the guru-paramparā."
                },
                {
                    "number": 4,
                    "original": "jayadharma-dāsye khyāti, śrī puruṣottama-ĵati,\ntā̃' ha'te brahmaṇya-tīrtha-sūri\nvyāsa-tīrtha tā̃'ra dāsa, lakṣmīpati vyāsa-dāsa,\ntā̃hā ha'te mādhavendra-purī (4)",
                    "english": "The sannyāsī Śrī Puruṣottama Tīrtha, a renowned disciple in the service of Śrī Jayadharma, was succeeded by the erudite Śrī Brahmaṇya Tīrtha. Next in succession was Śrī Vyāsa Tīrtha, who was succeeded by Śrī Lakṣmīpati, who in turn was succeeded by Śrī Mādhavendra Purī."
                },
                {
                    "number": 5,
                    "original": "mādhavendra-purī-varaśiṣya-vara śrī īśvara,\nnityānanda, śrī advaita vibhu\nīśvara purīke dhanya, kôrilena śrī caitanya,\njagad-guru gaura mahāprabhu (5)",
                    "english": "The most prominent disciples of the great Śrī Mādhavendra Purī were Śrī Īśvara Purī and the avatāras Śrī Nityānanda Prabhu and Śrī Advaita Ācārya. Śrī Caitanya Mahāprabhu, the Golden Lord and spiritual preceptor of all the worlds, made Īśvara Purī greatly fortunate by accepting him as His dīkṣā-guru."
                },
                {
                    "number": 6,
                    "original": "mahāprabhu śrī caitanya, rādhā-kṛṣṇa nahe anya,\nrūpānuga-janera jīvana\nviśvambhara-priyaṅkara, śrī svarūpa-dāmodara,\nśrī gosvāmī rūpa, sanātana (6)",
                    "english": "Śrī Caitanya Mahāprabhu, who is Rādhā and Kṛṣṇa combined, is the very life of the rūpānuga Vaiṣṇavas (those who follow Śrī Rūpa Gosvāmī). Śrī Svarūpa Dāmodara Gosvāmī, Śrī Rūpa, and Śrī Sanātana Gosvāmīs were the dearmost servants of Lord Viśvambhara (Śrī Caitanya)."
                },
                {
                    "number": 7,
                    "original": "rūpa-priya mahājana, jīva, raghunātha hana,\ntā̃'ra priya kavi kṛṣṇadāsa\nkṛṣṇadāsa-priya-vara, narottama sevā-para,\nĵā̃'ra pada viśvanātha-āśa (7)",
                    "english": "Dear to Śrī Rūpa Gosvāmī were the great saintly personalities Śrī Jīva Gosvāmī and Śrī Raghunātha dāsa Gosvāmī, whose intimate disciple was the great poet Śrī Kṛṣṇadāsa Kavirāja. The dearmost of Kṛṣṇadāsa was Śrīla Narottama dāsa Ṭhākura, who was always engaged in guru-sevā. His lotus feet were the only hope and aspiration of Śrī Viśvanātha Cakravartī Ṭhākura."
                },
                {
                    "number": 8,
                    "original": "viśvanātha bhakta-sātha, baladeva, jagannātha,\ntā̃'ra priya śrī bhaktivinoda\nmahā-bhāgavata-vara, śrī gaurakiśora-vara,\nhari-bhajanete ĵā̃'ra moda (8)",
                    "english": "Prominent among the associates of Śrī Viśvanātha Cakravartī Ṭhākura was Śrī Baladeva Vidyābhūṣaṇa. After him, the line descended to Śrīla Jagannātha dāsa Bābājī Mahārāja, who was the beloved śikṣā-guru of Śrī Bhaktivinoda Ṭhākura. Bhaktivinoda was the intimate friend of the great mahā-bhāgavata Śrīla Gaura-kiśora dāsa Bābājī Mahārāja, whose sole delight was hari-bhajana."
                },
                {
                    "number": 9,
                    "original": "śrī vārṣabhānavī-varā, sadā sevya-sevā-parā,\ntā̃hāra 'dayita-dāsa' nāma (9)",
                    "english": "Śrī Vārṣabhānavī, the daughter of Śrī Vṛṣabhānu Mahārāja, is the best of Śrī Kṛṣṇa's beloveds, as She is forever engaged in loving service to Her worshipful Lord. Śrī Vārṣabhānavī-dayita dāsa, the servant (dāsa) of Her beloved (dayita) is the name of Śrīla Bhaktisiddhānta Sarasvatī Ṭhākura Prabhupāda."
                },
                {
                    "number": 10,
                    "original": "prabhupāda-antaraṅga, śrī svarūpa-rūpānuga,\nśrī keśava bhakati-prajñāna\ngauḓīya vedānta-vettā, māyāvāda-tamohantā,\ngauravāṇī-pracārācār-dhāma (10)",
                    "english": "A confidential disciple of Śrīla Prabhupāda, Śrīla Bhakti Prajñāna Keśava Gosvāmī Mahārāja, was a faithful follower of Śrī Svarūpa Dāmodara and Śrī Rūpa Gosvāmī. Through his knowledge of Gauḓīya Vedānta, he annihilated the darkness of ignorance spread by māyāvāda. He was the abode of preaching and practicing Śrī Gaurāṅga's teachings (gauravāṇī) in his own life."
                },
                {
                    "number": 11,
                    "original": "pracārilô gauravāṇī, bhakativedānta svāmī,\npūrāilô prabhupāder kāma (11)",
                    "english": "Śrīla Bhaktivedānta Svāmī Mahārāja extensively preached this gauravāṇī and thus completely fulfilled the inner-heart's desire of Śrīla Bhaktisiddhānta Sarasvatī Prabhupāda."
                },
                {
                    "number": 12,
                    "original": "keśav priya mahājana, vāmana, nārāyaṇ hana,\ngauravāṇī tā̃'der prāṇa-dhana (12)",
                    "english": "Most dear to Śrī Bhakti Prajñāna Keśava Gosvāmī are the saintly personalities Śrī Bhaktivedānta Vāmana Gosvāmī and Śrī Bhaktivedānta Nārāyaṇa Gosvāmī, whose life's treasure is gauravāṇī."
                },
                {
                    "number": 13,
                    "original": "ei saba harijana, gaurāṅgera nija-jana,\ntā̃'dera ucchiṣṭe mora kāma (13)",
                    "english": "All of these devotees are the personal associates of Śrī Gaurāṅga. I desire to honor their ucchiṣṭa [the remnants of their lips, namely their mahā-prasāda as well as their instructions]."
                }
            ]
        },
        {
            "title": "Śrī Kṛṣṇa Janmāṣṭamī",
            "author": "Traditional",
            "category": "Śrī Kṛṣṇa",
            "verses": [
                {
                    "number": 1,
                    "original": "kṛṣṇera janama āj madhurāṭe\nbajāy karatāla, gāy rādhikā-gāna\nśrī kṛṣṇa-janama khūśī manane\nbhakta-gaṇa kare nṛtya gāna",
                    "english": "Today is Kṛṣṇa's birth in Mathurā, cymbals are playing, singing songs of Rādhikā. The devotees dance and sing in joyful celebration of Śrī Kṛṣṇa's birth."
                },
                {
                    "number": 2,
                    "original": "gokula-dhāme janama laila\ngovinda gopāla nanda-lāla\nbaṁśī bajāy vraja-vāsī\nsaba jana kare ānandamayī",
                    "english": "Govinda Gopāla, the beloved of Nanda, took birth in Gokula-dhāma. He plays the flute, and all the residents of Vraja become filled with bliss."
                }
            ]
        },
        {
            "title": "Rādhā-kṛṣṇa Praṇaya-vikṛti",
            "author": "Śrīla Bhaktivinoda Ṭhākura",
            "category": "Rādhā-Kṛṣṇa",
            "verses": [
                {
                    "number": 1,
                    "original": "rādhā-kṛṣṇa praṇaya-vikṛti hlādinī śakti āśrita\nhlādinī karāy kṛṣṇa-rasā-svādana\nśuddha-bhāve sudṛḍha-rase pūrṇa-sukhāsvādana",
                    "english": "The love affairs of Rādhā and Kṛṣṇa are transformations of the pleasure potency, hlādinī śakti. This pleasure potency causes Kṛṣṇa to taste transcendental mellows in pure sentiment with strong rasa and complete happiness."
                },
                {
                    "number": 2,
                    "original": "sei śakti gauracandre, prakāśita bhagavante\nśrī-kṛṣṇa-caitanya-rūpe āveśa\nvṛndāvana vilāsa-sthāne, priya-sakhīgaṇa-sane\nrāsa-keli karaye sadācāra",
                    "english": "That same potency has manifested in Gauracandra, revealed in the Supreme Lord who has appeared in the form of Śrī Kṛṣṇa Caitanya. In the place of Vṛndāvana pastimes, with the beloved sakhīs, He performs the rāsa dance in proper conduct."
                }
            ]
        },
        {
            "title": "Vrajera Gopāla",
            "author": "Śrīla Narottama dāsa Ṭhākura",
            "category": "Śrī Kṛṣṇa",
            "verses": [
                {
                    "number": 1,
                    "original": "vrajera gopāla, nanda-dulāla\ngopi-gaṇa-mana-cora\nśyāma-rāṅga sundara-mukha\nmohana-mūrati mora",
                    "english": "The cowherd boy of Vraja, the beloved son of Nanda, stealer of the hearts of the gopis. His dark complexion and beautiful face - this enchanting form is mine."
                },
                {
                    "number": 2,
                    "original": "yamunā-kūle keli-vihāra\ngopi-saṅge rāsa-rāṅga\nbaṁśī-madhura-dhvani śuni'\nmugdha haila vraja-nāga",
                    "english": "On the banks of the Yamunā He sports and plays, dancing the rāsa with the gopis. Hearing the sweet sound of His flute, all the people of Vraja become enchanted."
                }
            ]
        },
        {
            "title": "Dayāla Nitāi",
            "author": "Śrīla Locana dāsa Ṭhākura",
            "category": "Śrī Nityānanda",
            "verses": [
                {
                    "number": 1,
                    "original": "dayāla nitāi caitanya\nsundar mor gaurāṅga\ndīna-hīna patita pāmara\nsabāre karila uddhāra",
                    "english": "Merciful Nitāi and Caitanya, my beautiful Gaurāṅga. They delivered all the fallen, wretched, degraded and sinful souls."
                },
                {
                    "number": 2,
                    "original": "avadhūta nitāi, parama-karuṇāmaya\npatita-pāvana nāma dhāma\nlocana bole, nitāi bine\nbhaja keha nāhi kṛṣṇa-nāma",
                    "english": "The avadhūta Nitāi is supremely merciful, the deliverer of the fallen, the holy name and abode. Locana says, without Nitāi, no one can chant the holy name of Kṛṣṇa."
                }
            ]
        }
    ]

def save_bhajan_data_to_json(bhajan_data, filename="bhajan_data.json"):
    """
    Save bhajan data to JSON file for backup
    
    Args:
        bhajan_data (list): List of bhajan dictionaries
        filename (str): Output JSON filename
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(bhajan_data, f, ensure_ascii=False, indent=2)
    
    return f"Data saved to {filename}"
