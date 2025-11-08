import streamlit as st
import pandas as pd
import os
from pathlib import Path

# Import data loader
from data_loader import load_bhajan_data_from_excel

# Page configuration
st.set_page_config(
    page_title="Śrī Gauḍīya Gīti-guccha",
    page_icon="🕉️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for elegant design with proper fonts
st.markdown("""
<style>
    /* Import elegant fonts with better Unicode support */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Crimson+Text:ital,wght@0,400;0,600;1,400&family=Cormorant+Garamond:wght@300;400;500;600&family=Noto+Serif:wght@300;400;500;600&display=swap');
    
    /* Main container styling */
    .main {
        padding: 1rem;
        font-family: 'Crimson Text', serif;
        max-width: 800px;
        margin: 0 auto;
    }
    
    /* Title styling */
    .main-title {
        font-family: 'Playfair Display', serif;
        font-size: 2.5rem;
        font-weight: 600;
        text-align: center;
        color: #2c1810;
        margin: 1rem 0 0.5rem 0;
        line-height: 1.2;
    }
    
    .subtitle {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.2rem;
        font-style: italic;
        text-align: center;
        color: #5d4e37;
        margin: 0.5rem 0;
        line-height: 1.4;
    }
    
    .language-note {
        font-family: 'Cormorant Garamond', serif;
        font-size: 0.95rem;
        text-align: center;
        color: #8b7355;
        margin: 0.25rem 0 2rem 0;
        font-weight: 500;
        letter-spacing: 0.5px;
    }
    
    /* Header styling */
    .header {
        background: linear-gradient(135deg, #ea580c 0%, #fb923c 100%);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(234, 88, 12, 0.3);
    }
    
    .header h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 600;
    }
    
    .header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 1rem;
    }
    
    /* Bhajan item styling */
    .bhajan-item {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        transition: all 0.2s ease;
    }
    
    .bhajan-item:hover {
        background: #fff7ed;
        border-color: #ea580c;
    }
    
    .bhajan-title {
        color: #1f2937;
        font-weight: 600;
        margin-bottom: 0.3rem;
        font-size: 1.1rem;
    }
    
    .bhajan-author {
        color: #6b7280;
        font-size: 0.9rem;
    }
    
    /* Verse styling */
    .verse-container {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 0.75rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .verse-original {
        font-family: 'Noto Serif', 'Cormorant Garamond', serif;
        line-height: 1.4;
        font-size: 1.2rem;
        color: #000000;
        white-space: pre-line;
        font-weight: 400;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        text-rendering: optimizeLegibility;
        font-feature-settings: "kern" 1, "liga" 1;
        font-variant-ligatures: common-ligatures;
    }
    
    .verse-english {
        font-family: 'Crimson Text', serif;
        line-height: 1.5;
        font-size: 1.05rem;
        color: #000000;
        white-space: pre-line;
    }
    
    /* Russian and Latvian text styling */
    .verse-russian {
        font-family: 'Crimson Text', serif;
        line-height: 1.5;
        font-size: 1.05rem;
        color: #000000;
        white-space: pre-line;
    }
    
    .verse-latvian {
        font-family: 'Crimson Text', serif;
        line-height: 1.5;
        font-size: 1.05rem;
        color: #000000;
        white-space: pre-line;
    }
    
    /* Song Index alphabet navigation */
    .alphabet-nav {
        text-align: center;
        font-size: 1.2rem;
        margin: 1.5rem 0;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
    }
    
    .alphabet-nav a {
        color: #ea580c;
        text-decoration: underline;
        font-weight: bold;
        margin: 0 0.2rem;
    }
    
    .alphabet-inactive {
        color: #9ca3af;
        margin: 0 0.2rem;
    }
    
    /* Letter section headers */
    .letter-header {
        font-size: 2rem;
        font-weight: bold;
        color: #1f2937;
        text-align: center;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #ea580c;
    }
    
    .category-section {
        background: #f8fafc;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Responsive design for mobile */
    @media (max-width: 768px) {
        .main-title {
            font-size: 1.8rem;
        }
        
        .subtitle {
            font-size: 1rem;
        }
        
        .language-note {
            font-size: 0.85rem;
        }
        
        /* Mobile bhajan title styling */
        .stMarkdown h1 {
            font-size: 1.5rem !important;
            line-height: 1.3 !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* Mobile verse containers */
        .verse-container {
            padding: 0.5rem;
            margin: 0.3rem 0;
        }
        
        .verse-original {
            font-size: 1.1rem;
        }
        
        .verse-english, .verse-russian, .verse-latvian {
            font-size: 1rem;
        }
        
        /* Mobile statistics styling */
        .stats-container {
            padding: 1rem !important;
        }
        
        .stats-grid {
            gap: 0.3rem !important;
        }
        
        .stats-number {
            font-size: 1.4rem !important;
        }
        
        .stats-label {
            font-size: 0.8rem !important;
        }
    }
    
    /* Remove Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        border-radius: 6px;
        border: 1px solid #d1c4b0;
        background: #fefcf8;
        color: #5d4e37;
        padding: 0.75rem 1rem;
        transition: all 0.3s ease;
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.05rem;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        background: #f8f4e6;
        border-color: #a0956b;
        color: #2c1810;
        box-shadow: 0 2px 8px rgba(93, 78, 55, 0.1);
    }
    
    /* Stats container */
    .stats-container {
        background: #f8fafc;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid #e2e8f0;
    }
    
    /* Mobile responsive */
    @media (max-width: 768px) {
        .main {
            padding: 0.5rem;
        }
        
        .header h1 {
            font-size: 1.5rem;
        }
        
        .verse-container {
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state with URL parameter support
if 'page' not in st.session_state:
    # Check URL parameters first
    query_params = st.query_params
    if 'page' in query_params:
        st.session_state.page = query_params['page']
    else:
        st.session_state.page = 'home'
if 'selected_bhajan' not in st.session_state:
    st.session_state.selected_bhajan = None
if 'selected_category' not in st.session_state:
    st.session_state.selected_category = None
if 'selected_author' not in st.session_state:
    st.session_state.selected_author = None
if 'show_english' not in st.session_state:
    st.session_state.show_english = False
if 'selected_language' not in st.session_state:
    st.session_state.selected_language = 'original'  # original, english, russian, latvian

# Function to update URL when navigation changes
def update_url_params():
    """Update URL parameters to reflect current state for browser navigation"""
    params = {'page': st.session_state.page}
    if st.session_state.selected_category:
        params['category'] = st.session_state.selected_category
    if st.session_state.selected_author:
        params['author'] = st.session_state.selected_author
    if st.session_state.selected_bhajan and st.session_state.selected_bhajan.get('title'):
        params['bhajan'] = st.session_state.selected_bhajan['title']
    
    st.query_params.update(params)

def go_home():
    st.session_state.page = 'home'
    st.session_state.selected_bhajan = None
    st.session_state.selected_category = None
    st.session_state.selected_author = None
    st.session_state.show_english = False
    update_url_params()

def show_titles():
    st.session_state.page = 'titles'
    update_url_params()

def show_categories():
    st.session_state.page = 'categories'
    update_url_params()

def show_authors():
    st.session_state.page = 'authors'
    update_url_params()

def show_category_bhajans(category):
    st.session_state.page = 'category_bhajans'
    st.session_state.selected_category = category
    update_url_params()

def show_author_bhajans(author):
    st.session_state.page = 'author_bhajans'
    st.session_state.selected_author = author
    update_url_params()

def show_bhajan(bhajan):
    # Store current page as previous for back navigation
    st.session_state.previous_page = st.session_state.page
    st.session_state.page = 'bhajan'
    st.session_state.selected_bhajan = bhajan
    
    # Force complete page refresh to reset scroll
    st.session_state.bhajan_just_opened = True
    
    update_url_params()

# Load bhajan data from fixed Excel file
@st.cache_data
def load_data():
    # Try to load from the fixed Excel file
    excel_file_path = "Bhajans.xlsx"
    if os.path.exists(excel_file_path):
        return load_bhajan_data_from_excel(excel_file_path)
    else:
        # If file doesn't exist, use default data
        return load_bhajan_data_from_excel()

# Check URL parameters and restore state if needed
def restore_state_from_url():
    """Restore session state from URL parameters when user uses browser back/forward"""
    query_params = st.query_params
    
    if 'page' in query_params:
        page = query_params['page']
        
        # Restore page state
        if page != st.session_state.page:
            st.session_state.page = page
            
        # Restore category if specified
        if 'category' in query_params and page == 'category_bhajans':
            st.session_state.selected_category = query_params['category']
            
        # Restore author if specified  
        if 'author' in query_params and page == 'author_bhajans':
            st.session_state.selected_author = query_params['author']
            
        # Restore bhajan if specified
        if 'bhajan' in query_params and page == 'bhajan':
            bhajan_title = query_params['bhajan']
            # Find the bhajan by title
            bhajan_data = load_data()
            for bhajan in bhajan_data:
                if bhajan['title'] == bhajan_title:
                    st.session_state.selected_bhajan = bhajan
                    break

# Restore state from URL parameters
restore_state_from_url()

# Header
st.markdown("""
<div class="main-title">
    Śrī Gauḍīya Gīti-guccha
</div>
<div class="subtitle">
    An Anthology of Gauḍīya Vaiṣṇava Songs
</div>
<div class="language-note">
    IN BENGALI, SANSKRIT, HINDI AND ORIYA
</div>
""", unsafe_allow_html=True)

# Load data
bhajan_data = load_data()

# Safety check - ensure bhajan_data is not empty and has valid data
if not bhajan_data:
    st.error("⚠️ No bhajan data found! Please check your Excel file format.")
    st.stop()

# Get unique categories and authors with safety checks
try:
    categories = sorted(list(set(bhajan['category'] for bhajan in bhajan_data if bhajan.get('category'))))
    authors = sorted(list(set(bhajan['author'] for bhajan in bhajan_data if bhajan.get('author'))))
    sorted_titles = sorted(bhajan_data, key=lambda x: x['title'])
except Exception as e:
    st.error(f"⚠️ Error processing bhajan data: {e}")
    st.error("Please check that your Excel file has the correct format with columns: Category, Bhajan_Title, Author, Verse_Number, Original, English")
    st.stop()

# Navigation
if st.session_state.page != 'home':
    if st.button("🏠 Back to Home", key="home_btn", help="Return to main menu"):
        go_home()
        st.rerun()

# Page content
if st.session_state.page == 'home':
    # Home page
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🎵\nSong Index", key="titles_btn", help="Browse all bhajans alphabetically", use_container_width=True):
            show_titles()
            st.rerun()
    
    with col2:
        if st.button("📝\nBy First Line", key="first_line_btn", help="Browse bhajans by first line", use_container_width=True):
            st.session_state.page = 'first_line'
            update_url_params()
            st.rerun()
    
    with col3:
        if st.button("📁\nBy Category", key="categories_btn", help="Explore by devotional themes", use_container_width=True):
            show_categories()
            st.rerun()
    
    with col4:
        if st.button("👤\nBy Author", key="authors_btn", help="Find bhajans by their composers", use_container_width=True):
            show_authors()
            st.rerun()
    
    # Show elegant statistics
    st.markdown("---")
    
    # Calculate total verses for more interesting statistics
    total_verses = sum(len(bhajan['verses']) for bhajan in bhajan_data)
    
    # Custom CSS for statistics
    st.markdown("""
    <style>
    .stats-box {
        background: linear-gradient(135deg, #fefcf8 0%, #f8f4e6 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border: 1px solid #d1c4b0;
        box-shadow: 0 4px 12px rgba(160, 149, 107, 0.1);
        text-align: center;
    }
    .stats-title {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.1rem;
        font-weight: 600;
        color: #5d4e37;
        letter-spacing: 0.5px;
        margin-bottom: 1rem;
    }
    .stat-number {
        font-family: 'Playfair Display', serif;
        font-size: 1.8rem;
        font-weight: 600;
        color: #2c1810;
        margin-bottom: 0.2rem;
    }
    .stat-label {
        font-family: 'Cormorant Garamond', serif;
        font-size: 0.9rem;
        color: #8b7355;
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Statistics container
    st.markdown('<div class="stats-box">', unsafe_allow_html=True)
    st.markdown('<div class="stats-title">📊 Collection Overview</div>', unsafe_allow_html=True)
    
    # Use Streamlit columns for layout
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'<div class="stat-number">{len(bhajan_data)}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Bhajans</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'<div class="stat-number">{total_verses}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Verses</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'<div class="stat-number">{len(categories)}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Categories</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown(f'<div class="stat-number">{len(authors)}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Authors</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == 'titles':
    # Song Index page
    st.markdown("## 🎵 Song Index")
    
    # Group bhajans by first letter
    from collections import defaultdict
    import re
    
    bhajans_by_letter = defaultdict(list)
    for bhajan in sorted_titles:
        # Get first letter, handle special characters
        title = bhajan['title']
        # Remove common prefixes and get first meaningful letter
        clean_title = re.sub(r'^[\(\)\-\s]*', '', title)
        if clean_title:
            first_char = clean_title[0].upper()
            
            # Normalize Sanskrit/Bengali characters to closest ASCII
            char_map = {
                'Ś': 'S', 'Ṣ': 'S', 'Ṥ': 'S', 'Ŝ': 'S',
                'Ṛ': 'R', 'Ṝ': 'R', 'Ṟ': 'R', 'Ŗ': 'R',
                'Ṇ': 'N', 'Ṅ': 'N', 'Ñ': 'N', 'Ṉ': 'N',
                'Ṭ': 'T', 'Ṫ': 'T',
                'Ḍ': 'D', 'Ḑ': 'D',
                'Ṁ': 'M', 'Ṃ': 'M',
                'Ā': 'A', 'Á': 'A', 'À': 'A', 'Ä': 'A', 'Â': 'A',
                'Ī': 'I', 'Í': 'I', 'Ì': 'I', 'Ï': 'I', 'Î': 'I',
                'Ū': 'U', 'Ú': 'U', 'Ù': 'U', 'Ü': 'U', 'Û': 'U',
                'Ē': 'E', 'É': 'E', 'È': 'E', 'Ë': 'E', 'Ê': 'E',
                'Ō': 'O', 'Ó': 'O', 'Ò': 'O', 'Ö': 'O', 'Ô': 'O',
                'Ṟ': 'R', 'Ř': 'R'
            }
            
            # Convert to ASCII equivalent
            first_letter = char_map.get(first_char, first_char)
            
            # Ensure it's a valid ASCII letter
            if first_letter.isalpha():
                bhajans_by_letter[first_letter].append(bhajan)
    
    # Get available letters and sort them
    available_letters = sorted(bhajans_by_letter.keys())
    
    # Create alphabet navigation with clickable and non-clickable letters
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    nav_items = []
    
    for letter in alphabet:
        if letter in available_letters:
            nav_items.append(f'<a href="#{letter.lower()}" style="color: #ea580c; text-decoration: underline; font-weight: bold; margin: 0 0.3rem;">{letter}</a>')
        else:
            nav_items.append(f'<span style="color: #9ca3af; margin: 0 0.3rem;">{letter}</span>')
    
    # Display alphabet navigation
    st.markdown(
        f'<div class="alphabet-nav">{" - ".join(nav_items)}</div>', 
        unsafe_allow_html=True
    )
    
    # Display bhajans grouped by letter
    for letter in available_letters:
        # Letter header
        st.markdown(f'<div class="letter-header" id="{letter.lower()}">{letter}</div>', unsafe_allow_html=True)
        
        # Bhajans for this letter
        for bhajan in bhajans_by_letter[letter]:
            # Create clickable title as a styled link
            if st.button(bhajan['title'], key=f"index_{letter}_{bhajan['title']}", use_container_width=True):
                show_bhajan(bhajan)
                st.rerun()
        
        # Space between sections
        st.markdown("<br>", unsafe_allow_html=True)

elif st.session_state.page == 'first_line':
    # Song Index by First Line page
    st.markdown("## 📝 Song Index by First Line")
    
    # Extract first lines and group by letter
    from collections import defaultdict
    import re
    
    bhajans_by_first_line = []
    for bhajan in sorted_titles:
        if bhajan['verses']:
            # Get the first verse
            first_verse = bhajan['verses'][0]
            first_line_text = first_verse.get('original', '')
            
            # Extract the first line (until first newline)
            if first_line_text:
                first_line = first_line_text.split('\n')[0].strip()
                # Remove verse numbers if present
                first_line = re.sub(r'\s*\(\d+\)\s*$', '', first_line)
                
                # Handle cases where line starts with parentheses - extract the first word
                if first_line.startswith('('):
                    # Extract content within parentheses or first meaningful word
                    match = re.match(r'\(([^)]+)\)', first_line)
                    if match:
                        first_meaningful = match.group(1).strip()
                        if first_meaningful:
                            first_line = first_meaningful + first_line[first_line.find(')') + 1:].strip()
                
                bhajans_by_first_line.append({
                    'first_line': first_line,
                    'bhajan': bhajan
                })
    
    # Sort by first line
    bhajans_by_first_line.sort(key=lambda x: x['first_line'])
    
    # Group by first letter
    first_lines_by_letter = defaultdict(list)
    for item in bhajans_by_first_line:
        first_line = item['first_line']
        if first_line:
            # Get first character and normalize
            first_char = first_line[0].upper()
            
            # Normalize Sanskrit/Bengali characters to closest ASCII
            char_map = {
                'Ś': 'S', 'Ṣ': 'S', 'Ṥ': 'S', 'Ŝ': 'S',
                'Ṛ': 'R', 'Ṝ': 'R', 'Ṟ': 'R', 'Ŗ': 'R',
                'Ṇ': 'N', 'Ṅ': 'N', 'Ñ': 'N', 'Ṉ': 'N',
                'Ṭ': 'T', 'Ṫ': 'T',
                'Ḍ': 'D', 'Ḑ': 'D',
                'Ṁ': 'M', 'Ṃ': 'M',
                'Ā': 'A', 'Á': 'A', 'À': 'A', 'Ä': 'A', 'Â': 'A',
                'Ī': 'I', 'Í': 'I', 'Ì': 'I', 'Ï': 'I', 'Î': 'I',
                'Ū': 'U', 'Ú': 'U', 'Ù': 'U', 'Ü': 'U', 'Û': 'U',
                'Ē': 'E', 'É': 'E', 'È': 'E', 'Ë': 'E', 'Ê': 'E',
                'Ō': 'O', 'Ó': 'O', 'Ò': 'O', 'Ö': 'O', 'Ô': 'O',
                'Ṟ': 'R', 'Ř': 'R'
            }
            
            # Convert to ASCII equivalent
            first_letter = char_map.get(first_char, first_char)
            
            # Handle special cases that aren't letters
            if not first_letter.isalpha():
                # Try to find first alphabetic character
                for char in first_line:
                    if char.isalpha():
                        first_letter = char_map.get(char.upper(), char.upper())
                        break
                else:
                    first_letter = 'OTHER'  # Fallback for non-alphabetic starts
            
            # Ensure it's a valid ASCII letter
            if first_letter.isalpha():
                first_lines_by_letter[first_letter].append(item)
    
    # Get available letters and sort them
    available_letters = sorted(first_lines_by_letter.keys())
    
    # Create alphabet navigation
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    nav_items = []
    
    for letter in alphabet:
        if letter in available_letters:
            nav_items.append(f'<a href="#{letter.lower()}" style="color: #ea580c; text-decoration: underline; font-weight: bold; margin: 0 0.3rem;">{letter}</a>')
        else:
            nav_items.append(f'<span style="color: #9ca3af; margin: 0 0.3rem;">{letter}</span>')
    
    # Display alphabet navigation
    st.markdown(
        f'<div class="alphabet-nav">{" - ".join(nav_items)}</div>', 
        unsafe_allow_html=True
    )
    
    # Display bhajans grouped by first letter of first line
    for letter in available_letters:
        # Letter header
        st.markdown(f'<div class="letter-header" id="{letter.lower()}">{letter}</div>', unsafe_allow_html=True)
        
        # First lines for this letter
        for item in first_lines_by_letter[letter]:
            first_line = item['first_line']
            bhajan = item['bhajan']
            
            # Create clickable first line as button
            if st.button(first_line, key=f"firstline_{letter}_{bhajan['title']}", use_container_width=True):
                show_bhajan(bhajan)
                st.rerun()
        
        # Space between sections
        st.markdown("<br>", unsafe_allow_html=True)

elif st.session_state.page == 'categories':
    # Categories page
    st.markdown("## 📁 Categories")
    
    for category in categories:
        count = len([b for b in bhajan_data if b['category'] == category])
        # Create clickable category
        category_clicked = st.button(f"{category} ({count} bhajan{'s' if count != 1 else ''})", 
                                   key=f"cat_{category}", 
                                   use_container_width=True)
        if category_clicked:
            show_category_bhajans(category)
            st.rerun()

elif st.session_state.page == 'authors':
    # Authors page
    st.markdown("## 👤 Authors")
    
    for author in authors:
        count = len([b for b in bhajan_data if b['author'] == author])
        # Create clickable author
        author_clicked = st.button(f"{author} ({count} bhajan{'s' if count != 1 else ''})", 
                                 key=f"auth_{author}", 
                                 use_container_width=True)
        if author_clicked:
            show_author_bhajans(author)
            st.rerun()

elif st.session_state.page == 'category_bhajans':
    # Category bhajans page
    if st.button("← Back to Categories", key="back_to_cats"):
        show_categories()
        st.rerun()
    
    st.markdown(f"## 📁 {st.session_state.selected_category}")
    
    category_bhajans = [b for b in bhajan_data if b['category'] == st.session_state.selected_category]
    category_bhajans.sort(key=lambda x: x['title'])
    
    for bhajan in category_bhajans:
        # Create clickable title
        title_clicked = st.button(bhajan['title'], key=f"cat_title_{bhajan['title']}", use_container_width=True)
        if title_clicked:
            show_bhajan(bhajan)
            st.rerun()
        
        # Create clickable author link
        author_clicked = st.button(f"👤 {bhajan['author']}", key=f"cat_author_{bhajan['title']}", use_container_width=True, type="secondary")
        if author_clicked:
            show_author_bhajans(bhajan['author'])
            st.rerun()
        
        st.markdown("---")

elif st.session_state.page == 'author_bhajans':
    # Author bhajans page
    if st.button("← Back to Authors", key="back_to_auths"):
        show_authors()
        st.rerun()
    
    st.markdown(f"## 👤 {st.session_state.selected_author}")
    
    author_bhajans = [b for b in bhajan_data if b['author'] == st.session_state.selected_author]
    author_bhajans.sort(key=lambda x: x['title'])
    
    for bhajan in author_bhajans:
        # Create clickable title
        title_clicked = st.button(bhajan['title'], key=f"auth_title_{bhajan['title']}", use_container_width=True)
        if title_clicked:
            show_bhajan(bhajan)
            st.rerun()
        
        # Add spacing between bhajans (like in other pages)
        st.markdown("")

elif st.session_state.page == 'bhajan':
    # MEGA TEST: Confirm this version is running
    st.error("🔴 TEST VERSION 5.0 - ANCHOR FIX LOADED")
    st.write(f"Current query params: {dict(st.query_params)}")
    
    # Bhajan display page with query params routing fix
    bhajan = st.session_state.selected_bhajan
    
    if bhajan:
        # Force query params update to avoid anchor preservation
        current_params = dict(st.query_params)
        if current_params.get('view') != 'bhajan' or current_params.get('id') != bhajan['title']:
            st.query_params.update({
                "view": "bhajan", 
                "id": bhajan['title'],
                "page": "bhajan"
            })
            st.rerun()
        
        # Create container at the very top
        top_container = st.container()
        
        with top_container:
            # Back button at the top with unique key
            if st.button("← Back", key=f"bhajan_back_{bhajan['title'][:10]}"):
                # Clear bhajan-specific query params
                st.query_params.update({"view": "list", "page": st.session_state.previous_page})
                if hasattr(st.session_state, 'previous_page'):
                    st.session_state.page = st.session_state.previous_page
                else:
                    st.session_state.page = 'home'
                st.rerun()
            
            st.markdown("")  # Small space
            
            # Title and author - non-focusable elements first
            st.markdown(f"# {bhajan['title']}")
            st.markdown(f"**{bhajan['author']}**")
            st.markdown(f"*Category: {bhajan['category']}*")
            st.markdown("---")
        
        # Language toggle with unique keys
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("📜 Original", 
                        key=f"bhajan_original_{bhajan['title'][:10]}",
                        help="Show original text",
                        type="primary" if st.session_state.selected_language == 'original' else "secondary",
                        use_container_width=True):
                st.session_state.selected_language = 'original'
                st.rerun()
        
        with col2:
            if st.button("🇬🇧 English", 
                        key=f"bhajan_english_{bhajan['title'][:10]}",
                        help="Show English translation",
                        type="primary" if st.session_state.selected_language == 'english' else "secondary",
                        use_container_width=True):
                st.session_state.selected_language = 'english'
                st.rerun()
        
        with col3:
            if st.button("🇷🇺 Русский", 
                        key=f"bhajan_russian_{bhajan['title'][:10]}",
                        help="Show Russian translation",
                        type="primary" if st.session_state.selected_language == 'russian' else "secondary",
                        use_container_width=True):
                st.session_state.selected_language = 'russian'
                st.rerun()
        
        with col4:
            if st.button("🇱🇻 Latviešu", 
                        key=f"bhajan_latvian_{bhajan['title'][:10]}",
                        help="Show Latvian translation",
                        type="primary" if st.session_state.selected_language == 'latvian' else "secondary",
                        use_container_width=True):
                st.session_state.selected_language = 'latvian'
                st.rerun()
        
        st.markdown("---")
        
        # Sort verses by number to ensure correct order
        sorted_verses = sorted(bhajan['verses'], key=lambda x: x.get('number', 0))
        
        # Display verses
        for i, verse in enumerate(sorted_verses):
            # Determine which text to show based on selected language
            if st.session_state.selected_language == 'english':
                text_content = verse['english']
                text_class = "verse-english"
            elif st.session_state.selected_language == 'russian':
                text_content = verse.get('russian', 'Перевод недоступен')
                text_class = "verse-russian"
            elif st.session_state.selected_language == 'latvian':
                text_content = verse.get('latvian', 'Tulkojums nav pieejams')
                text_class = "verse-latvian"
            else:  # original
                text_content = verse['original']
                text_class = "verse-original"
            
            # Add verse number to the text if it exists and text is available
            verse_number = verse.get('number', i + 1)
            if text_content and text_content not in ['Перевод недоступен', 'Tulkojums nav pieejams']:
                # Only add number if not already present in text
                if f'({verse_number})' not in text_content:
                    text_content = f"{text_content}\n\n({verse_number})"
            
            st.markdown(f"""
            <div class="verse-container">
                <div class="{text_class}">{text_content}</div>
            </div>
            """, unsafe_allow_html=True)


