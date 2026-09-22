# ============================================================
# ARTHROSONIC v2.0
# AI-Assisted Osteoarthritis Risk Screening
# SIH 2026 Prototype
# ============================================================

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
import io
import textwrap
import re

def load_pdf_font(font_path, size):
    font_path = Path(font_path)

    if not font_path.exists():
        raise FileNotFoundError(
            f"Required PDF font not found: {font_path}"
        )

    if font_path.stat().st_size < 10000:
        raise RuntimeError(
            f"PDF font appears invalid or incomplete: {font_path}"
        )

    try:
        return ImageFont.truetype(str(font_path), size)
    except Exception as e:
        raise RuntimeError(
            f"Could not load PDF font: {font_path}\n"
            f"Original error: {e}"
        ) from e

# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

LOGO_PATH = BASE_DIR / "Assets" / "logo.png"
if not LOGO_PATH.exists():
    LOGO_PATH = BASE_DIR / "assets" / "logo.png"

FONT_DIR = BASE_DIR / "Assets" / "fonts"

# ============================================================
# MULTILINGUAL UI
# ============================================================

LANGUAGES = {
    # Only languages with a complete local UI pack are offered.
    "English": "en",
    "हिन्दी (Hindi)": "hi",
    "অসমীয়া (Assamese)": "as",
    "বাংলা (Bengali)": "bn",
    "नेपाली (Nepali)": "ne",
}

# Core field labels and workflow text. English remains the fallback so the
# prototype stays usable even where a language pack is intentionally partial.
TRANSLATIONS = {
    "hi": {
        "Confirm the identity first. ArthroSonic can then reconnect the current assessment with previous screening records available in the prototype session.": "पहले पहचान की पुष्टि करें। इसके बाद वर्तमान मूल्यांकन को प्रोटोटाइप सत्र में उपलब्ध पिछले स्क्रीनिंग रिकॉर्ड से जोड़ा जा सकता है।",
        "Upload any recent reports that may help the healthcare worker review the patient's history. These can include X-rays, MRI scans, CT scans, ultrasound reports, blood work, prescriptions, or other relevant documents.": "हाल की रिपोर्टें अपलोड करें जो स्वास्थ्यकर्मी को रोगी का इतिहास देखने में मदद कर सकती हैं। इनमें X-ray, MRI, CT, अल्ट्रासाउंड, रक्त जाँच या अन्य संबंधित दस्तावेज़ शामिल हो सकते हैं।",
        "🏠 Overview": "🏠 अवलोकन",
        "👤 Patient Profile": "👤 रोगी प्रोफ़ाइल",
        "📡 Assessment": "📡 मूल्यांकन",
        "🧠 AI Analysis": "🧠 AI विश्लेषण",
        "🧬 Digital Twin": "🧬 डिजिटल ट्विन",
        "📋 Patient History": "📋 रोगी इतिहास",
        "Overview":"अवलोकन", "Patient Profile":"रोगी प्रोफ़ाइल", "Assessment":"मूल्यांकन", "AI Analysis":"AI विश्लेषण", "Digital Twin":"डिजिटल ट्विन", "Patient History":"रोगी इतिहास",
        "NAVIGATION":"नेविगेशन", "SYSTEM STATUS":"सिस्टम स्थिति", "DEPLOYMENT":"परिनियोजन", "AI-Assisted Osteoarthritis Risk Screening":"AI-सहायित ऑस्टियोआर्थराइटिस जोखिम स्क्रीनिंग",
        "Patient Information":"रोगी जानकारी", "Full Name":"पूरा नाम", "Age":"आयु", "Sex":"लिंग", "Location":"स्थान", "Occupation":"पेशा", "Physical Activity":"शारीरिक गतिविधि", "Phone Number":"फ़ोन नंबर", "Address":"पता",
        "Connect Patient Record":"रोगी रिकॉर्ड जोड़ें", "Connect to previous patient data":"पिछले रोगी डेटा से जोड़ें", "CONFIRM PATIENT":"रोगी की पुष्टि करें", "Latest Reports & Medical Documents":"नवीनतम रिपोर्ट और चिकित्सा दस्तावेज़",
        "Upload latest reports":"नवीनतम रिपोर्ट अपलोड करें", "OA Risk Factors & Symptoms":"OA जोखिम कारक और लक्षण", "Previous Knee Injury":"पिछली घुटने की चोट", "Family History of OA":"OA का पारिवारिक इतिहास", "Terrain Exposure":"भू-भाग का संपर्क", "Pain Level":"दर्द का स्तर", "Stiffness":"जकड़न", "Mobility Difficulty":"चलने-फिरने में कठिनाई",
        "Knee":"घुटना", "Knee only":"केवल घुटना", "Screening Grade":"स्क्रीनिंग ग्रेड", "What Do the Grades Mean?":"ग्रेड का क्या अर्थ है?", "What Did the System Find?":"सिस्टम ने क्या पाया?", "Movement & Patient-Reported Findings":"गतिशीलता और रोगी द्वारा बताए गए निष्कर्ष", "Joint Signal Analysis":"घुटने के सिग्नल का विश्लेषण", "Explainable Screening Factors":"व्याख्यायोग्य स्क्रीनिंग कारक", "Longitudinal Risk Monitoring":"दीर्घकालिक जोखिम निगरानी", "What Does This Mean for You?":"इसका आपके लिए क्या अर्थ है?",
        "DOWNLOAD SCREENING REPORT":"स्क्रीनिंग रिपोर्ट डाउनलोड करें", "START SENSOR RECORDING":"सेंसर रिकॉर्डिंग शुरू करें", "CONTINUE TO AI ANALYSIS →":"AI विश्लेषण पर जाएँ →", "SAVE & CONTINUE TO ASSESSMENT →":"सहेजें और मूल्यांकन पर जाएँ →", "NEXT →":"अगला →",
        "LOW":"कम", "MEDIUM":"मध्यम", "HIGH":"उच्च", "Risk Index":"जोखिम सूचकांक", "Data Quality":"डेटा गुणवत्ता", "Report Date":"रिपोर्ट तिथि", "Patient ID":"रोगी ID", "Joint Screened":"स्क्रीन किया गया जोड़",
    },
    "as": {
        "Confirm the identity first. ArthroSonic can then reconnect the current assessment with previous screening records available in the prototype session.": "প্ৰথমে পৰিচয় নিশ্চিত কৰক। তাৰ পিছত বৰ্তমান মূল্যায়নক প্ৰ’টোটাইপ অধিবেশনত থকা পূৰ্বৰ স্ক্ৰিনিং ৰেকৰ্ডৰ সৈতে সংযোগ কৰিব পাৰি।",
        "Upload any recent reports that may help the healthcare worker review the patient's history. These can include X-rays, MRI scans, CT scans, ultrasound reports, blood work, prescriptions, or other relevant documents.": "শেহতীয়া প্ৰতিবেদন আপলোড কৰক যিয়ে স্বাস্থ্যকৰ্মীক ৰোগীৰ ইতিহাস পৰ্যালোচনা কৰাত সহায় কৰিব পাৰে। ইয়াত X-ray, MRI, CT, আল্ট্ৰাছাউণ্ড, ৰক্ত পৰীক্ষা বা আন নথি থাকিব পাৰে।",
        "🏠 Overview": "🏠 অভাৰভিউ",
        "👤 Patient Profile": "👤 ৰোগীৰ প্ৰ’ফাইল",
        "📡 Assessment": "📡 মূল্যায়ন",
        "🧠 AI Analysis": "🧠 AI বিশ্লেষণ",
        "🧬 Digital Twin": "🧬 ডিজিটেল টুইন",
        "📋 Patient History": "📋 ৰোগীৰ ইতিহাস",
        "Overview":"অভাৰভিউ", "Patient Profile":"ৰোগীৰ প্ৰ'ফাইল", "Assessment":"মূল্যায়ন", "AI Analysis":"AI বিশ্লেষণ", "Digital Twin":"ডিজিটেল টুইন", "Patient History":"ৰোগীৰ ইতিহাস",
        "NAVIGATION":"নেভিগেশ্যন", "SYSTEM STATUS":"চিষ্টেমৰ স্থিতি", "DEPLOYMENT":"ডিপ্লয়মেণ্ট", "AI-Assisted Osteoarthritis Risk Screening":"AI-সহায়ক অষ্টিঅ'আৰ্থ্ৰাইটিছ ঝুঁকি স্ক্ৰিনিং",
        "Patient Information":"ৰোগীৰ তথ্য", "Full Name":"সম্পূৰ্ণ নাম", "Age":"বয়স", "Sex":"লিংগ", "Location":"স্থান", "Occupation":"পেচা", "Physical Activity":"শাৰীৰিক কাৰ্যকলাপ", "Phone Number":"ফোন নম্বৰ", "Address":"ঠিকনা",
        "Connect Patient Record":"ৰোগীৰ ৰেকৰ্ড সংযোগ কৰক", "Connect to previous patient data":"পূৰ্বৰ ৰোগীৰ তথ্য সংযোগ কৰক", "CONFIRM PATIENT":"ৰোগী নিশ্চিত কৰক", "Latest Reports & Medical Documents":"শেহতীয়া প্ৰতিবেদন আৰু চিকিৎসা নথি",
        "Upload latest reports":"শেহতীয়া প্ৰতিবেদন আপলোড কৰক", "OA Risk Factors & Symptoms":"OA ঝুঁকি কাৰক আৰু লক্ষণ", "Previous Knee Injury":"পূৰ্বৰ আঁঠুৰ আঘাত", "Family History of OA":"OA-ৰ পাৰিবাৰিক ইতিহাস", "Terrain Exposure":"ভূখণ্ডৰ সংস্পৰ্শ", "Pain Level":"বিষৰ মাত্ৰা", "Stiffness":"জড়তা", "Mobility Difficulty":"চলাচলৰ অসুবিধা",
        "Knee":"আঁঠু", "Knee only":"কেৱল আঁঠু", "Screening Grade":"স্ক্ৰিনিং গ্ৰেড", "What Do the Grades Mean?":"গ্ৰেডসমূহৰ অৰ্থ কি?", "What Did the System Find?":"চিষ্টেমে কি পাইছে?", "Movement & Patient-Reported Findings":"চলাচল আৰু ৰোগীয়ে জনোৱা ফলাফল", "Joint Signal Analysis":"আঁঠুৰ সংকেত বিশ্লেষণ", "Explainable Screening Factors":"ব্যাখ্যাযোগ্য স্ক্ৰিনিং কাৰক", "Longitudinal Risk Monitoring":"দীৰ্ঘম্যাদী ঝুঁকি নিৰীক্ষণ", "What Does This Mean for You?":"ইয়াৰ আপোনাৰ বাবে অৰ্থ কি?",
        "DOWNLOAD SCREENING REPORT":"স্ক্ৰিনিং প্ৰতিবেদন ডাউনলোড কৰক", "START SENSOR RECORDING":"চেন্সৰ ৰেকৰ্ডিং আৰম্ভ কৰক", "CONTINUE TO AI ANALYSIS →":"AI বিশ্লেষণলৈ যাওক →", "SAVE & CONTINUE TO ASSESSMENT →":"সংৰক্ষণ কৰি মূল্যায়নলৈ যাওক →", "NEXT →":"পৰৱৰ্তী →",
        "LOW":"কম", "MEDIUM":"মধ্যম", "HIGH":"উচ্চ", "Risk Index":"ঝুঁকি সূচক", "Data Quality":"তথ্যৰ গুণমান", "Report Date":"প্ৰতিবেদনৰ তাৰিখ", "Patient ID":"ৰোগী ID", "Joint Screened":"স্ক্ৰিন কৰা জোড়",
    },
    "bn": {
        "Confirm the identity first. ArthroSonic can then reconnect the current assessment with previous screening records available in the prototype session.": "প্রথমে পরিচয় নিশ্চিত করুন। এরপর বর্তমান মূল্যায়নকে প্রোটোটাইপ সেশনে থাকা পূর্বের স্ক্রিনিং রেকর্ডের সঙ্গে যুক্ত করা যাবে।",
        "Upload any recent reports that may help the healthcare worker review the patient's history. These can include X-rays, MRI scans, CT scans, ultrasound reports, blood work, prescriptions, or other relevant documents.": "সাম্প্রতিক রিপোর্ট আপলোড করুন যা স্বাস্থ্যকর্মীকে রোগীর ইতিহাস পর্যালোচনায় সহায়তা করতে পারে। এতে X-ray, MRI, CT, আল্ট্রাসাউন্ড, রক্ত পরীক্ষা বা অন্যান্য নথি থাকতে পারে।",
        "🏠 Overview": "🏠 ওভারভিউ",
        "👤 Patient Profile": "👤 রোগীর প্রোফাইল",
        "📡 Assessment": "📡 মূল্যায়ন",
        "🧠 AI Analysis": "🧠 AI বিশ্লেষণ",
        "🧬 Digital Twin": "🧬 ডিজিটাল টুইন",
        "📋 Patient History": "📋 রোগীর ইতিহাস",
        "Overview":"ওভারভিউ", "Patient Profile":"রোগীর প্রোফাইল", "Assessment":"মূল্যায়ন", "AI Analysis":"AI বিশ্লেষণ", "Digital Twin":"ডিজিটাল টুইন", "Patient History":"রোগীর ইতিহাস",
        "NAVIGATION":"নেভিগেশন", "SYSTEM STATUS":"সিস্টেম স্ট্যাটাস", "DEPLOYMENT":"ডিপ্লয়মেন্ট", "AI-Assisted Osteoarthritis Risk Screening":"AI-সহায়িত অস্টিওআর্থ্রাইটিস ঝুঁকি স্ক্রিনিং",
        "Patient Information":"রোগীর তথ্য", "Full Name":"পূর্ণ নাম", "Age":"বয়স", "Sex":"লিঙ্গ", "Location":"অবস্থান", "Occupation":"পেশা", "Physical Activity":"শারীরিক কার্যকলাপ", "Phone Number":"ফোন নম্বর", "Address":"ঠিকানা",
        "Connect Patient Record":"রোগীর রেকর্ড সংযুক্ত করুন", "Connect to previous patient data":"পূর্বের রোগীর তথ্য সংযুক্ত করুন", "CONFIRM PATIENT":"রোগী নিশ্চিত করুন", "Latest Reports & Medical Documents":"সাম্প্রতিক রিপোর্ট ও চিকিৎসা নথি",
        "Upload latest reports":"সাম্প্রতিক রিপোর্ট আপলোড করুন", "OA Risk Factors & Symptoms":"OA ঝুঁকির কারণ ও উপসর্গ", "Previous Knee Injury":"পূর্বের হাঁটুর আঘাত", "Family History of OA":"OA-এর পারিবারিক ইতিহাস", "Terrain Exposure":"ভূখণ্ডের সংস্পর্শ", "Pain Level":"ব্যথার মাত্রা", "Stiffness":"জড়তা", "Mobility Difficulty":"চলাচলে অসুবিধা",
        "Knee":"হাঁটু", "Knee only":"শুধু হাঁটু", "Screening Grade":"স্ক্রিনিং গ্রেড", "What Do the Grades Mean?":"গ্রেডগুলির অর্থ কী?", "What Did the System Find?":"সিস্টেম কী পেয়েছে?", "Movement & Patient-Reported Findings":"চলাচল ও রোগীর জানানো ফলাফল", "Joint Signal Analysis":"হাঁটুর সিগন্যাল বিশ্লেষণ", "Explainable Screening Factors":"ব্যাখ্যাযোগ্য স্ক্রিনিং কারণ", "Longitudinal Risk Monitoring":"দীর্ঘমেয়াদি ঝুঁকি পর্যবেক্ষণ", "What Does This Mean for You?":"এর অর্থ কী?",
        "DOWNLOAD SCREENING REPORT":"স্ক্রিনিং রিপোর্ট ডাউনলোড করুন", "START SENSOR RECORDING":"সেন্সর রেকর্ডিং শুরু করুন", "CONTINUE TO AI ANALYSIS →":"AI বিশ্লেষণে যান →", "SAVE & CONTINUE TO ASSESSMENT →":"সংরক্ষণ করে মূল্যায়নে যান →", "NEXT →":"পরবর্তী →",
        "LOW":"কম", "MEDIUM":"মাঝারি", "HIGH":"উচ্চ", "Risk Index":"ঝুঁকি সূচক", "Data Quality":"ডেটার গুণমান", "Report Date":"রিপোর্টের তারিখ", "Patient ID":"রোগী ID", "Joint Screened":"স্ক্রিন করা জয়েন্ট",
    },
    "ne": {
        "Confirm the identity first. ArthroSonic can then reconnect the current assessment with previous screening records available in the prototype session.": "पहिले पहिचान पुष्टि गर्नुहोस्। त्यसपछि हालको मूल्याङ्कनलाई प्रोटोटाइप सत्रमा उपलब्ध अघिल्लो स्क्रिनिङ रेकर्डसँग जोड्न सकिन्छ।",
        "Upload any recent reports that may help the healthcare worker review the patient's history. These can include X-rays, MRI scans, CT scans, ultrasound reports, blood work, prescriptions, or other relevant documents.": "स्वास्थ्यकर्मीलाई बिरामीको इतिहास समीक्षा गर्न सहयोग गर्ने नयाँ रिपोर्टहरू अपलोड गर्नुहोस्। यसमा X-ray, MRI, CT, अल्ट्रासाउन्ड, रगत परीक्षण वा अन्य सम्बन्धित कागजात हुन सक्छन्।",
        "🏠 Overview": "🏠 अवलोकन",
        "👤 Patient Profile": "👤 बिरामी प्रोफाइल",
        "📡 Assessment": "📡 मूल्याङ्कन",
        "🧠 AI Analysis": "🧠 AI विश्लेषण",
        "🧬 Digital Twin": "🧬 डिजिटल ट्विन",
        "📋 Patient History": "📋 बिरामी इतिहास",
        "Overview":"अवलोकन", "Patient Profile":"बिरामी प्रोफाइल", "Assessment":"मूल्याङ्कन", "AI Analysis":"AI विश्लेषण", "Digital Twin":"डिजिटल ट्विन", "Patient History":"बिरामी इतिहास",
        "NAVIGATION":"नेभिगेसन", "SYSTEM STATUS":"प्रणाली स्थिति", "DEPLOYMENT":"प्रयोग", "Patient Information":"बिरामी जानकारी", "Full Name":"पूरा नाम", "Age":"उमेर", "Sex":"लिङ्ग", "Location":"स्थान", "Occupation":"पेशा", "Physical Activity":"शारीरिक गतिविधि", "Phone Number":"फोन नम्बर", "Address":"ठेगाना", "Connect Patient Record":"बिरामी रेकर्ड जोड्नुहोस्", "Connect to previous patient data":"अघिल्लो बिरामी डेटा जोड्नुहोस्", "CONFIRM PATIENT":"बिरामी पुष्टि गर्नुहोस्", "Latest Reports & Medical Documents":"नयाँ रिपोर्ट र चिकित्सा कागजात", "Upload latest reports":"नयाँ रिपोर्ट अपलोड गर्नुहोस्", "OA Risk Factors & Symptoms":"OA जोखिम कारक र लक्षण", "Previous Knee Injury":"अघिल्लो घुँडाको चोट", "Family History of OA":"OA को पारिवारिक इतिहास", "Pain Level":"दुखाइ स्तर", "Stiffness":"कडापन", "Mobility Difficulty":"गतिशीलता कठिनाइ", "Knee":"घुँडा", "Knee only":"घुँडा मात्र", "Screening Grade":"स्क्रिनिङ ग्रेड", "What Do the Grades Mean?":"ग्रेडको अर्थ के हो?", "What Did the System Find?":"प्रणालीले के पायो?", "Movement & Patient-Reported Findings":"गतिशीलता र बिरामीले बताएका निष्कर्ष", "Joint Signal Analysis":"घुँडा संकेत विश्लेषण", "Explainable Screening Factors":"व्याख्यायोग्य स्क्रिनिङ कारक", "Longitudinal Risk Monitoring":"दीर्घकालीन जोखिम निगरानी", "What Does This Mean for You?":"यसको अर्थ के हो?", "DOWNLOAD SCREENING REPORT":"स्क्रिनिङ रिपोर्ट डाउनलोड गर्नुहोस्", "START SENSOR RECORDING":"सेन्सर रेकर्डिङ सुरु गर्नुहोस्", "CONTINUE TO AI ANALYSIS →":"AI विश्लेषणमा जानुहोस् →", "SAVE & CONTINUE TO ASSESSMENT →":"सुरक्षित गरेर मूल्याङ्कनमा जानुहोस् →", "NEXT →":"अर्को →", "LOW":"कम", "MEDIUM":"मध्यम", "HIGH":"उच्च",
    },
}

# For the NER language packs not yet fully localized, the selector is still
# available and core medical labels remain in English rather than inventing
# unreliable medical translations. These packs can be expanded later.


# Extended visible-UI translations.  These cover the complete prototype workflow
# used on the six pages; English remains the fallback for technical/prototype-only
# terms where a validated translation is not available.
EXTRA_TRANSLATIONS = {
    "hi": {
        "DEPLOYMENT":"परिनियोजन", "AI Engine — Ready":"AI इंजन — तैयार", "Joint Signal Sensor — Connected":"जॉइंट सिग्नल सेंसर — कनेक्टेड", "IMU Module — Connected":"IMU मॉड्यूल — कनेक्टेड", "Local Database — Ready":"स्थानीय डेटाबेस — तैयार",
        "NER / Rural Healthcare":"NER / ग्रामीण स्वास्थ्य सेवा", "Offline-ready architecture":"ऑफलाइन-रेडी आर्किटेक्चर", "Secure patient records":"सुरक्षित रोगी रिकॉर्ड", "ArthroSonic Prototype • SIH 2026":"ArthroSonic प्रोटोटाइप • SIH 2026",
        "AI-Assisted Osteoarthritis Screening":"AI-सहायित ऑस्टियोआर्थराइटिस स्क्रीनिंग", "Portable multimodal assessment platform for early OA risk identification":"प्रारंभिक OA जोखिम पहचान के लिए पोर्टेबल मल्टीमॉडल मूल्यांकन प्लेटफ़ॉर्म",
        "Live System Overview":"लाइव सिस्टम अवलोकन", "ACTIVE PATIENT":"सक्रिय रोगी", "Assessment ready":"मूल्यांकन तैयार", "SENSOR STATUS":"सेंसर स्थिति", "ONLINE":"ऑनलाइन", "PZT + Microphone + IMU":"PZT + माइक्रोफ़ोन + IMU", "SIGNAL QUALITY":"सिग्नल गुणवत्ता", "Suitable for analysis":"विश्लेषण के लिए उपयुक्त", "ASSESSMENT MODE":"मूल्यांकन मोड", "MULTIMODAL":"मल्टीमॉडल", "PZT + microphone + gait + symptoms":"PZT + माइक्रोफ़ोन + चाल + लक्षण",
        "Multimodal Patient Profile":"मल्टीमॉडल रोगी प्रोफ़ाइल", "CURRENT SCREENING":"वर्तमान स्क्रीनिंग", "OA-associated risk markers":"OA-संबंधित जोखिम संकेतक", "DEMO OUTPUT":"डेमो आउटपुट", "MODERATE":"मध्यम", "Prototype multimodal analysis indicates":"प्रोटोटाइप मल्टीमॉडल विश्लेषण दर्शाता है", "a moderate level of OA-associated markers.":"OA-संबंधित संकेतकों का मध्यम स्तर।",
        "OA HUMAN DIGITAL TWIN":"OA ह्यूमन डिजिटल ट्विन", "Patient Movement State":"रोगी की गति स्थिति", "Longitudinal representation of":"दीर्घकालिक प्रतिनिधित्व", "movement, sound-pattern and symptom":"गति, ध्वनि-पैटर्न और लक्षणों की", "characteristics.":"विशेषताओं का।", "Knee ROM":"घुटने की गति सीमा", "Symmetry":"समरूपता", "Gait m/s":"चाल m/s",
        "Screening Workflow":"स्क्रीनिंग कार्यप्रवाह", "Symptoms + history":"लक्षण + इतिहास", "Joint sound + movement":"जोड़ की ध्वनि + गति", "Feature extraction":"फीचर निष्कर्षण", "Personalized output":"व्यक्तिगत आउटपुट", "Risk Report":"जोखिम रिपोर्ट",
        "START PATIENT PROFILE →":"रोगी प्रोफ़ाइल शुरू करें →", "Create or reconnect a patient record before assessment":"मूल्यांकन से पहले रोगी रिकॉर्ड बनाएँ या पुनः जोड़ें", "Patient record confirmed":"रोगी रिकॉर्ड की पुष्टि हो गई", "Current screening can now be linked with the patient's longitudinal record.":"वर्तमान स्क्रीनिंग को अब रोगी के दीर्घकालिक रिकॉर्ड से जोड़ा जा सकता है।", "Prototype only: files are available during the current app session.":"केवल प्रोटोटाइप: फ़ाइलें वर्तमान ऐप सत्र में उपलब्ध हैं।", "Attached for this assessment:":"इस मूल्यांकन के लिए संलग्न:",
        "KNEE-ONLY SCREENING":"केवल घुटने की स्क्रीनिंग", "The ArthroSonic prototype measures the":"ArthroSonic प्रोटोटाइप केवल", "knee joint only":"घुटने के जोड़ को मापता है", "The screening site is fixed and cannot be changed.":"स्क्रीनिंग साइट निश्चित है और बदली नहीं जा सकती।", "Confirm the patient record to unlock document upload and the next step.":"दस्तावेज़ अपलोड और अगले चरण को सक्रिय करने के लिए रोगी रिकॉर्ड की पुष्टि करें।",
        "Sensor Assessment":"सेंसर मूल्यांकन", "Guided acquisition of joint sound and movement signals":"जोड़ की ध्वनि और गति संकेतों का निर्देशित अधिग्रहण", "SCREENING SITE: KNEE ONLY":"स्क्रीनिंग साइट: केवल घुटना", "ArthroSonic is configured specifically for knee assessment.":"ArthroSonic विशेष रूप से घुटने के मूल्यांकन के लिए कॉन्फ़िगर किया गया है।", "Sensor Network":"सेंसर नेटवर्क", "Knee vibration + joint sound":"घुटने का कंपन + जोड़ की ध्वनि", "Movement + posture + gait":"गति + मुद्रा + चाल", "Gait assessment":"चाल मूल्यांकन", "Excellent acquisition":"उत्कृष्ट अधिग्रहण",
        "Guided Assessment Protocol":"निर्देशित मूल्यांकन प्रोटोकॉल", "Joint Signal":"जोड़ संकेत", "Place the PZT and microphone module over the":"PZT और माइक्रोफ़ोन मॉड्यूल को", "knee joint and perform controlled":"घुटने के जोड़ पर रखें और नियंत्रित", "flexion-extension movements.":"फ्लेक्शन-एक्सटेंशन गति करें।", "Movement":"गति", "Capture knee movement, gait,":"घुटने की गति, चाल,", "range of motion and left-right":"गति सीमा और बाएँ-दाएँ", "movement symmetry.":"गति समरूपता रिकॉर्ड करें।", "Symptoms":"लक्षण", "Combine patient-reported pain,":"रोगी द्वारा बताए गए दर्द,", "stiffness, mobility and relevant":"जकड़न, गतिशीलता और संबंधित", "risk factors.":"जोखिम कारकों को मिलाएँ।", "Joint Signal Acquisition":"जोड़ संकेत अधिग्रहण", "READY":"तैयार", "START SENSOR RECORDING":"सेंसर रिकॉर्डिंग शुरू करें", "Joint-signal and movement sequence captured successfully.":"जोड़-सिग्नल और गति अनुक्रम सफलतापूर्वक रिकॉर्ड किया गया।", "Acquisition Complete":"अधिग्रहण पूर्ण", "Signal quality is suitable for":"सिग्नल गुणवत्ता उपयुक्त है", "feature extraction and prototype":"फीचर निष्कर्षण और प्रोटोटाइप", "AI analysis.":"AI विश्लेषण के लिए।", "Live Joint Signal":"लाइव जॉइंट सिग्नल", "Time-Frequency Analysis":"समय-आवृत्ति विश्लेषण", "RUN MULTIMODAL AI ANALYSIS":"मल्टीमॉडल AI विश्लेषण चलाएँ", "Prototype multimodal analysis completed.":"प्रोटोटाइप मल्टीमॉडल विश्लेषण पूरा हुआ।",
        "AI Risk Analysis":"AI जोखिम विश्लेषण", "Screening grade, risk markers and supporting assessment findings":"स्क्रीनिंग ग्रेड, जोखिम संकेतक और सहायक मूल्यांकन निष्कर्ष", "PROTOTYPE / SIMULATED AI OUTPUT":"प्रोटोटाइप / सिम्युलेटेड AI आउटपुट", "This page presents a preliminary screening interpretation for demonstration. It does not establish a medical diagnosis.":"यह पृष्ठ प्रदर्शन के लिए प्रारंभिक स्क्रीनिंग व्याख्या प्रस्तुत करता है। यह चिकित्सीय निदान स्थापित नहीं करता।", "Screening Grade":"स्क्रीनिंग ग्रेड", "RISK":"जोखिम", "OA-ASSOCIATED RISK SCORE":"OA-संबंधित जोखिम स्कोर", "Prototype screening index":"प्रोटोटाइप स्क्रीनिंग सूचकांक", "DATA QUALITY":"डेटा गुणवत्ता", "Good input quality; not OA probability":"इनपुट गुणवत्ता अच्छी; यह OA की संभावना नहीं है", "What Do the Grades Mean?":"ग्रेड का क्या अर्थ है?", "RISK LEVEL":"जोखिम स्तर", "IN SIMPLE WORDS":"सरल शब्दों में", "Few OA-related risk markers detected.":"कुछ OA-संबंधित जोखिम संकेतक पाए गए।", "Some OA-related risk markers detected.":"कुछ OA-संबंधित जोखिम संकेतक पाए गए।", "More OA-related risk markers detected.":"अधिक OA-संबंधित जोखिम संकेतक पाए गए।", "Grades describe screening risk only. They do not confirm OA or show the amount of joint damage. Grade boundaries must be defined and validated for the AI model.":"ग्रेड केवल स्क्रीनिंग जोखिम बताते हैं। वे OA की पुष्टि या जोड़ की क्षति की मात्रा नहीं बताते। ग्रेड सीमाएँ AI मॉडल के लिए परिभाषित और मान्य की जानी चाहिए।",
        "What Did the System Find?":"सिस्टम ने क्या पाया?", "SCREENING DETAIL":"स्क्रीनिंग विवरण", "RESULT":"परिणाम", "WHAT IT MEANS":"इसका अर्थ", "Data quality":"डेटा गुणवत्ता", "Sound patterns detected":"ध्वनि पैटर्न पाए गए", "Patterns picked up during screening.":"स्क्रीनिंग के दौरान पैटर्न पाए गए।", "The system captured the input clearly; this is not the chance of having OA.":"सिस्टम ने इनपुट स्पष्ट रूप से रिकॉर्ड किया; यह OA होने की संभावना नहीं है।",
        "Movement & Patient-Reported Findings":"गति और रोगी द्वारा बताए गए निष्कर्ष", "Movement range":"गति सीमा", "Left-right symmetry":"बाएँ-दाएँ समरूपता", "Patient reported":"रोगी द्वारा बताया गया", "Joint Signal Analysis":"जोड़ संकेत विश्लेषण", "Explainable Screening Factors":"व्याख्यायोग्य स्क्रीनिंग कारक", "Sound + vibration events":"ध्वनि + कंपन घटनाएँ", "17 patterns detected during the prototype movement sequence.":"प्रोटोटाइप गति अनुक्रम में 17 पैटर्न पाए गए।", "Movement symmetry":"गति समरूपता", "Mild left-right movement asymmetry is present in the demonstration profile.":"डेमो प्रोफ़ाइल में हल्की बाएँ-दाएँ गति असममिति है।", "Range of motion":"गति की सीमा", "The recorded knee range of motion is 108° in the demonstration profile.":"डेमो प्रोफ़ाइल में दर्ज घुटने की गति सीमा 108° है।", "Reported symptoms":"बताए गए लक्षण", "Pain and stiffness inputs contribute to the multimodal screening profile.":"दर्द और जकड़न इनपुट मल्टीमॉडल स्क्रीनिंग प्रोफ़ाइल में योगदान करते हैं।", "Longitudinal Risk Monitoring":"दीर्घकालिक जोखिम निगरानी", "Assessment Date":"मूल्यांकन तिथि", "Risk Index":"जोखिम सूचकांक", "What Does This Mean for You?":"इसका आपके लिए क्या अर्थ है?", "Predictive screening only. This system does not diagnose OA or prescribe treatment.":"केवल पूर्वानुमानात्मक स्क्रीनिंग। यह सिस्टम OA का निदान या उपचार निर्धारित नहीं करता।", "DOWNLOAD SCREENING REPORT":"स्क्रीनिंग रिपोर्ट डाउनलोड करें", "CONTINUE TO OA HUMAN DIGITAL TWIN →":"OA ह्यूमन डिजिटल ट्विन पर जाएँ →",
        "OA Human Digital Twin":"OA ह्यूमन डिजिटल ट्विन", "Longitudinal digital representation of patient-specific OA-related characteristics":"रोगी-विशिष्ट OA-संबंधित विशेषताओं का दीर्घकालिक डिजिटल प्रतिनिधित्व", "PATIENT DIGITAL REPRESENTATION":"रोगी का डिजिटल प्रतिनिधित्व", "From one-time screening":"एक बार की स्क्रीनिंग से", "to longitudinal monitoring.":"दीर्घकालिक निगरानी तक।", "The ArthroSonic Digital Twin organizes sound,":"ArthroSonic डिजिटल ट्विन ध्वनि,", "movement, symptom and contextual measurements":"गति, लक्षण और संदर्भित मापों को", "into a patient-specific longitudinal profile.":"रोगी-विशिष्ट दीर्घकालिक प्रोफ़ाइल में व्यवस्थित करता है।", "Patient Twin State":"रोगी ट्विन स्थिति", "DIGITAL PATIENT MODEL":"डिजिटल रोगी मॉडल", "Right Knee Profile":"दाएँ घुटने की प्रोफ़ाइल", "MODERATE MARKER STATE":"मध्यम संकेतक स्थिति", "Patient-Specific State Variables":"रोगी-विशिष्ट स्थिति चर", "These variables form the current":"ये चर वर्तमान", "demonstration state of the digital twin.":"डिजिटल ट्विन की डेमो स्थिति बनाते हैं।", "Knee Sound + Vibration Signature":"घुटने की ध्वनि + कंपन हस्ताक्षर", "events":"घटनाएँ", "Knee Range of Motion":"घुटने की गति सीमा", "Gait Symmetry":"चाल समरूपता", "Reported Pain":"बताया गया दर्द", "Gait Speed":"चाल गति", "Signal Quality":"सिग्नल गुणवत्ता", "Digital Twin Timeline":"डिजिटल ट्विन समयरेखा", "Baseline Assessment":"बेसलाइन मूल्यांकन", "Initial patient movement and joint-signal profile recorded.":"प्रारंभिक रोगी गति और जोड़-सिग्नल प्रोफ़ाइल रिकॉर्ड की गई।", "Follow-up Assessment":"फॉलो-अप मूल्यांकन", "Longitudinal measurements added to patient profile.":"दीर्घकालिक माप रोगी प्रोफ़ाइल में जोड़े गए।", "Movement Assessment":"गति मूल्यांकन", "Updated gait and knee movement characteristics.":"चाल और घुटने की गति की विशेषताएँ अपडेट की गईं।", "Current Assessment":"वर्तमान मूल्यांकन", "Latest multimodal screening profile generated.":"नवीनतम मल्टीमॉडल स्क्रीनिंग प्रोफ़ाइल तैयार की गई।", "Why a Digital Twin?":"डिजिटल ट्विन क्यों?", "Longitudinal":"दीर्घकालिक", "Compare future measurements against the patient's own baseline.":"भविष्य के मापों की तुलना रोगी की अपनी बेसलाइन से करें।", "Multimodal":"मल्टीमॉडल", "Combine sound, movement and symptom information.":"ध्वनि, गति और लक्षणों की जानकारी मिलाएँ।", "Personalized":"व्यक्तिगत", "Represent patient-specific characteristics rather than relying only on population averages.":"केवल जनसंख्या औसत पर निर्भर रहने के बजाय रोगी-विशिष्ट विशेषताओं को दर्शाएँ।", "VIEW PATIENT HISTORY →":"रोगी इतिहास देखें →",
        "Longitudinal screening records and personalized baseline tracking":"दीर्घकालिक स्क्रीनिंग रिकॉर्ड और व्यक्तिगत बेसलाइन ट्रैकिंग", "PATIENT RECORD":"रोगी रिकॉर्ड", "Previous Assessments":"पिछले मूल्यांकन", "Risk Markers":"जोखिम संकेतक", "Sound Events":"ध्वनि घटनाएँ", "Longitudinal Trends":"दीर्घकालिक रुझान", "Prototype Risk Index":"प्रोटोटाइप जोखिम सूचकांक", "Sound Event Trend":"ध्वनि घटना रुझान", "Personalized Baseline":"व्यक्तिगत बेसलाइन", "BASELINE ROM":"बेसलाइन ROM", "CURRENT ROM":"वर्तमान ROM", "BASELINE EVENTS":"बेसलाइन घटनाएँ", "CURRENT EVENTS":"वर्तमान घटनाएँ", "Screening Interpretation":"स्क्रीनिंग व्याख्या", "Longitudinal monitoring":"दीर्घकालिक निगरानी", "ArthroSonic stores repeated screening measurements":"ArthroSonic बार-बार की गई स्क्रीनिंग माप संग्रहीत करता है", "so that future assessments can be compared with":"ताकि भविष्य के मूल्यांकन की तुलना", "the patient's own historical baseline.":"रोगी की अपनी ऐतिहासिक बेसलाइन से की जा सके।", "Changes in sound-pattern features, movement characteristics,":"ध्वनि-पैटर्न विशेषताओं, गति विशेषताओं,", "symptoms and other recorded variables can therefore":"लक्षणों और अन्य रिकॉर्ड किए गए चर में बदलाव को", "be visualized over time.":"समय के साथ देखा जा सके।", "PERSONALIZED MONITORING":"व्यक्तिगत निगरानी",
        "No":"नहीं", "Yes":"हाँ", "Female":"महिला", "Male":"पुरुष", "Other":"अन्य", "Low":"कम", "Moderate":"मध्यम", "High":"उच्च", "House / village / town / district / state":"घर / गाँव / शहर / जिला / राज्य", "e.g. +91 98765 43210":"उदा. +91 98765 43210",
        "Not provided":"उपलब्ध नहीं", "Page 1 of 1":"पृष्ठ 1 / 1", "NOT A MEDICAL DIAGNOSIS":"चिकित्सीय निदान नहीं", "Patient":"रोगी", "Phone":"फ़ोन", "Address":"पता", "Knee Screen":"घुटना स्क्रीन", "Fixed — Knee":"स्थिर — घुटना", "Screening Type":"स्क्रीनिंग प्रकार", "Multimodal predictive risk screening":"मल्टीमॉडल पूर्वानुमानात्मक जोखिम स्क्रीनिंग", "Status":"स्थिति", "Preliminary":"प्रारंभिक", "System":"सिस्टम", "Grade Reference":"ग्रेड संदर्भ", "Predictive Screening Result":"पूर्वानुमानात्मक स्क्रीनिंग परिणाम", "What the System Found":"सिस्टम ने क्या पाया", "Predictive Interpretation":"पूर्वानुमानात्मक व्याख्या", "Important Information":"महत्वपूर्ण जानकारी"
    },
    "as": {
        "DEPLOYMENT":"ডিপ্লয়মেণ্ট", "AI Engine — Ready":"AI ইঞ্জিন — সাজু", "Joint Signal Sensor — Connected":"জইণ্ট চিগনেল ছেন্সৰ — সংযুক্ত", "IMU Module — Connected":"IMU মডিউল — সংযুক্ত", "Local Database — Ready":"স্থানীয় ডাটাবেছ — সাজু", "NER / Rural Healthcare":"NER / গ্ৰাম্য স্বাস্থ্যসেৱা", "Offline-ready architecture":"অফলাইন-ৰেডি আৰ্হি", "Secure patient records":"সুৰক্ষিত ৰোগী ৰেকৰ্ড", "ArthroSonic Prototype • SIH 2026":"ArthroSonic প্ৰ’টোটাইপ • SIH 2026",
        "AI-Assisted Osteoarthritis Screening":"AI-সহায়ক অষ্টিঅ’আৰ্থ্ৰাইটিছ স্ক্ৰিনিং", "Portable multimodal assessment platform for early OA risk identification":"আৰম্ভণিৰ OA ঝুঁকি চিনাক্তকৰণৰ বাবে প’ৰ্টেবল মাল্টিম’ডেল মূল্যায়ন প্লেটফৰ্ম", "Live System Overview":"লাইভ চিষ্টেমৰ অভাৰভিউ", "ACTIVE PATIENT":"সক্ৰিয় ৰোগী", "Assessment ready":"মূল্যায়ন সাজু", "SENSOR STATUS":"ছেন্সৰৰ স্থিতি", "ONLINE":"অনলাইন", "SIGNAL QUALITY":"চিগনেলৰ গুণমান", "Suitable for analysis":"বিশ্লেষণৰ বাবে উপযুক্ত", "ASSESSMENT MODE":"মূল্যায়ন মোড", "MULTIMODAL":"মাল্টিম’ডেল", "Multimodal Patient Profile":"মাল্টিম’ডেল ৰোগীৰ প্ৰ’ফাইল", "CURRENT SCREENING":"বৰ্তমান স্ক্ৰিনিং", "OA-associated risk markers":"OA-সম্পৰ্কীয় ঝুঁকি সূচক", "DEMO OUTPUT":"ডেম’ আউটপুট", "MODERATE":"মধ্যম", "Screening Workflow":"স্ক্ৰিনিং কাৰ্যপ্ৰবাহ", "Symptoms + history":"লক্ষণ + ইতিহাস", "Joint sound + movement":"জইণ্টৰ শব্দ + চলাচল", "Feature extraction":"ফিচাৰ নিষ্কাশন", "Personalized output":"ব্যক্তিগত আউটপুট", "Risk Report":"ঝুঁকি প্ৰতিবেদন",
        "START PATIENT PROFILE →":"ৰোগীৰ প্ৰ’ফাইল আৰম্ভ কৰক →", "Create or reconnect a patient record before assessment":"মূল্যায়নৰ আগতে ৰোগীৰ ৰেকৰ্ড সৃষ্টি বা পুনৰ সংযোগ কৰক", "Patient record confirmed":"ৰোগীৰ ৰেকৰ্ড নিশ্চিত কৰা হৈছে", "Current screening can now be linked with the patient's longitudinal record.":"বৰ্তমান স্ক্ৰিনিং এতিয়া ৰোগীৰ দীৰ্ঘম্যাদী ৰেকৰ্ডৰ সৈতে সংযোগ কৰিব পাৰি।", "Prototype only: files are available during the current app session.":"কেৱল প্ৰ’টোটাইপ: ফাইলসমূহ বৰ্তমান এপ ছেছনত উপলব্ধ।", "Attached for this assessment:":"এই মূল্যায়নৰ বাবে সংলগ্ন:", "KNEE-ONLY SCREENING":"কেৱল আঁঠুৰ স্ক্ৰিনিং", "Confirm the patient record to unlock document upload and the next step.":"নথি আপলোড আৰু পৰৱৰ্তী ধাপ মুকলি কৰিবলৈ ৰোগীৰ ৰেকৰ্ড নিশ্চিত কৰক।", "Sensor Assessment":"ছেন্সৰ মূল্যায়ন", "Guided acquisition of joint sound and movement signals":"জইণ্টৰ শব্দ আৰু চলাচলৰ চিগনেল নিৰ্দেশিতভাৱে সংগ্ৰহ", "SCREENING SITE: KNEE ONLY":"স্ক্ৰিনিং স্থান: কেৱল আঁঠু", "Sensor Network":"ছেন্সৰ নেটৱৰ্ক", "Guided Assessment Protocol":"নিৰ্দেশিত মূল্যায়ন প্ৰট’কল", "Joint Signal":"জইণ্ট চিগনেল", "Movement":"চলাচল", "Symptoms":"লক্ষণ", "Joint Signal Acquisition":"জইণ্ট চিগনেল সংগ্ৰহ", "READY":"সাজু", "START SENSOR RECORDING":"ছেন্সৰ ৰেকৰ্ডিং আৰম্ভ কৰক", "Joint-signal and movement sequence captured successfully.":"জইণ্ট চিগনেল আৰু চলাচলৰ ক্ৰম সফলভাৱে ৰেকৰ্ড কৰা হৈছে।", "Acquisition Complete":"সংগ্ৰহ সম্পূৰ্ণ", "Live Joint Signal":"লাইভ জইণ্ট চিগনেল", "Time-Frequency Analysis":"সময়-কম্পাঙ্ক বিশ্লেষণ", "RUN MULTIMODAL AI ANALYSIS":"মাল্টিম’ডেল AI বিশ্লেষণ চলাওক", "Prototype multimodal analysis completed.":"প্ৰ’টোটাইপ মাল্টিম’ডেল বিশ্লেষণ সম্পূৰ্ণ হৈছে।",
        "AI Risk Analysis":"AI ঝুঁকি বিশ্লেষণ", "Screening grade, risk markers and supporting assessment findings":"স্ক্ৰিনিং গ্ৰেড, ঝুঁকি সূচক আৰু সহায়ক মূল্যায়ন ফলাফল", "PROTOTYPE / SIMULATED AI OUTPUT":"প্ৰ’টোটাইপ / অনুকৰণ কৰা AI আউটপুট", "Screening Grade":"স্ক্ৰিনিং গ্ৰেড", "RISK LEVEL":"ঝুঁকি স্তৰ", "IN SIMPLE WORDS":"সহজ ভাষাত", "What Did the System Find?":"চিষ্টেমে কি পাইছে?", "SCREENING DETAIL":"স্ক্ৰিনিং বিৱৰণ", "RESULT":"ফলাফল", "WHAT IT MEANS":"ইয়াৰ অৰ্থ", "Data quality":"তথ্যৰ গুণমান", "Sound patterns detected":"শব্দৰ পেটাৰ্ণ পোৱা গৈছে", "Movement & Patient-Reported Findings":"চলাচল আৰু ৰোগীয়ে জনোৱা ফলাফল", "Movement range":"চলাচলৰ পৰিসৰ", "Left-right symmetry":"বাওঁ-সোঁ সমমিতি", "Patient reported":"ৰোগীয়ে জনোৱা", "Joint Signal Analysis":"আঁঠুৰ চিগনেল বিশ্লেষণ", "Explainable Screening Factors":"ব্যাখ্যাযোগ্য স্ক্ৰিনিং কাৰক", "Longitudinal Risk Monitoring":"দীৰ্ঘম্যাদী ঝুঁকি নিৰীক্ষণ", "Assessment Date":"মূল্যায়নৰ তাৰিখ", "Risk Index":"ঝুঁকি সূচক", "What Does This Mean for You?":"ইয়াৰ আপোনাৰ বাবে অৰ্থ কি?", "Predictive screening only. This system does not diagnose OA or prescribe treatment.":"কেৱল পূৰ্বানুমানমূলক স্ক্ৰিনিং। এই চিষ্টেমে OA নিৰ্ণয় বা চিকিৎসা নিৰ্ধাৰণ নকৰে।", "DOWNLOAD SCREENING REPORT":"স্ক্ৰিনিং প্ৰতিবেদন ডাউনলোড কৰক", "CONTINUE TO OA HUMAN DIGITAL TWIN →":"OA হিউমেন ডিজিটেল টুইনলৈ যাওক →",
        "OA Human Digital Twin":"OA হিউমেন ডিজিটেল টুইন", "Patient Twin State":"ৰোগীৰ টুইন অৱস্থা", "DIGITAL PATIENT MODEL":"ডিজিটেল ৰোগী মডেল", "Right Knee Profile":"সোঁ আঁঠুৰ প্ৰ’ফাইল", "MODERATE MARKER STATE":"মধ্যম সূচক অৱস্থা", "Patient-Specific State Variables":"ৰোগী-নিৰ্দিষ্ট অৱস্থা চলক", "Digital Twin Timeline":"ডিজিটেল টুইনৰ সময়ৰেখা", "Baseline Assessment":"বেচলাইন মূল্যায়ন", "Follow-up Assessment":"ফ’ল’-আপ মূল্যায়ন", "Movement Assessment":"চলাচল মূল্যায়ন", "Current Assessment":"বৰ্তমান মূল্যায়ন", "Why a Digital Twin?":"ডিজিটেল টুইন কিয়?", "Longitudinal":"দীৰ্ঘম্যাদী", "Multimodal":"মাল্টিম’ডেল", "Personalized":"ব্যক্তিগত", "VIEW PATIENT HISTORY →":"ৰোগীৰ ইতিহাস চাওক →", "Longitudinal screening records and personalized baseline tracking":"দীৰ্ঘম্যাদী স্ক্ৰিনিং ৰেকৰ্ড আৰু ব্যক্তিগত বেচলাইন ট্ৰেকিং", "Previous Assessments":"পূৰ্বৰ মূল্যায়ন", "Risk Markers":"ঝুঁকি সূচক", "Sound Events":"শব্দৰ ঘটনা", "Longitudinal Trends":"দীৰ্ঘম্যাদী প্ৰৱণতা", "Prototype Risk Index":"প্ৰ’টোটাইপ ঝুঁকি সূচক", "Sound Event Trend":"শব্দ ঘটনা প্ৰৱণতা", "Personalized Baseline":"ব্যক্তিগত বেচলাইন", "BASELINE ROM":"বেচলাইন ROM", "CURRENT ROM":"বৰ্তমান ROM", "BASELINE EVENTS":"বেচলাইন ঘটনা", "CURRENT EVENTS":"বৰ্তমান ঘটনা", "Screening Interpretation":"স্ক্ৰিনিং ব্যাখ্যা", "PERSONALIZED MONITORING":"ব্যক্তিগত নিৰীক্ষণ", "No":"নহয়", "Yes":"হয়", "Female":"মহিলা", "Male":"পুৰুষ", "Other":"অন্য", "Low":"কম", "Moderate":"মধ্যম", "High":"উচ্চ", "Patient":"ৰোগী", "Phone":"ফোন", "Address":"ঠিকনা", "Knee Screen":"আঁঠু স্ক্ৰিন", "Fixed — Knee":"স্থিৰ — আঁঠু", "Screening Type":"স্ক্ৰিনিং প্ৰকাৰ", "Multimodal predictive risk screening":"মাল্টিম’ডেল পূৰ্বানুমানমূলক ঝুঁকি স্ক্ৰিনিং", "Status":"স্থিতি", "Preliminary":"প্ৰাথমিক", "System":"চিষ্টেম", "Grade Reference":"গ্ৰেডৰ অৰ্থ", "Predictive Screening Result":"পূৰ্বানুমানমূলক স্ক্ৰিনিং ফলাফল", "What the System Found":"চিষ্টেমে কি পাইছে", "Predictive Interpretation":"পূৰ্বানুমানমূলক ব্যাখ্যা", "Important Information":"গুৰুত্বপূৰ্ণ তথ্য"
    },
    "bn": {
        "DEPLOYMENT":"ডিপ্লয়মেন্ট", "AI Engine — Ready":"AI ইঞ্জিন — প্রস্তুত", "Joint Signal Sensor — Connected":"জয়েন্ট সিগন্যাল সেন্সর — সংযুক্ত", "IMU Module — Connected":"IMU মডিউল — সংযুক্ত", "Local Database — Ready":"স্থানীয় ডেটাবেস — প্রস্তুত", "NER / Rural Healthcare":"NER / গ্রামীণ স্বাস্থ্যসেবা", "Offline-ready architecture":"অফলাইন-রেডি আর্কিটেকচার", "Secure patient records":"নিরাপদ রোগী রেকর্ড", "ArthroSonic Prototype • SIH 2026":"ArthroSonic প্রোটোটাইপ • SIH 2026", "AI-Assisted Osteoarthritis Screening":"AI-সহায়িত অস্টিওআর্থ্রাইটিস স্ক্রিনিং", "Portable multimodal assessment platform for early OA risk identification":"প্রাথমিক OA ঝুঁকি শনাক্তকরণের জন্য পোর্টেবল মাল্টিমোডাল মূল্যায়ন প্ল্যাটফর্ম", "Live System Overview":"লাইভ সিস্টেম ওভারভিউ", "ACTIVE PATIENT":"সক্রিয় রোগী", "Assessment ready":"মূল্যায়ন প্রস্তুত", "SENSOR STATUS":"সেন্সর স্ট্যাটাস", "ONLINE":"অনলাইন", "SIGNAL QUALITY":"সিগন্যালের মান", "Suitable for analysis":"বিশ্লেষণের জন্য উপযুক্ত", "ASSESSMENT MODE":"মূল্যায়ন মোড", "MULTIMODAL":"মাল্টিমোডাল", "Multimodal Patient Profile":"মাল্টিমোডাল রোগীর প্রোফাইল", "CURRENT SCREENING":"বর্তমান স্ক্রিনিং", "OA-associated risk markers":"OA-সম্পর্কিত ঝুঁকি সূচক", "DEMO OUTPUT":"ডেমো আউটপুট", "MODERATE":"মাঝারি", "Screening Workflow":"স্ক্রিনিং কার্যপ্রবাহ", "Symptoms + history":"উপসর্গ + ইতিহাস", "Joint sound + movement":"জয়েন্টের শব্দ + নড়াচড়া", "Feature extraction":"ফিচার নিষ্কাশন", "Personalized output":"ব্যক্তিগত আউটপুট", "Risk Report":"ঝুঁকি রিপোর্ট", "START PATIENT PROFILE →":"রোগীর প্রোফাইল শুরু করুন →", "Create or reconnect a patient record before assessment":"মূল্যায়নের আগে রোগীর রেকর্ড তৈরি বা পুনরায় সংযুক্ত করুন", "Patient record confirmed":"রোগীর রেকর্ড নিশ্চিত হয়েছে", "Current screening can now be linked with the patient's longitudinal record.":"বর্তমান স্ক্রিনিং এখন রোগীর দীর্ঘমেয়াদি রেকর্ডের সঙ্গে যুক্ত করা যাবে।", "Prototype only: files are available during the current app session.":"শুধু প্রোটোটাইপ: বর্তমান অ্যাপ সেশনে ফাইলগুলো উপলব্ধ।", "Attached for this assessment:":"এই মূল্যায়নের জন্য সংযুক্ত:", "KNEE-ONLY SCREENING":"শুধু হাঁটুর স্ক্রিনিং", "Confirm the patient record to unlock document upload and the next step.":"ডকুমেন্ট আপলোড ও পরবর্তী ধাপ চালু করতে রোগীর রেকর্ড নিশ্চিত করুন।", "Sensor Assessment":"সেন্সর মূল্যায়ন", "Guided acquisition of joint sound and movement signals":"জয়েন্টের শব্দ ও নড়াচড়ার সিগন্যাল নির্দেশিতভাবে সংগ্রহ", "SCREENING SITE: KNEE ONLY":"স্ক্রিনিং সাইট: শুধু হাঁটু", "Sensor Network":"সেন্সর নেটওয়ার্ক", "Guided Assessment Protocol":"নির্দেশিত মূল্যায়ন প্রোটোকল", "Joint Signal":"জয়েন্ট সিগন্যাল", "Movement":"নড়াচড়া", "Symptoms":"উপসর্গ", "Joint Signal Acquisition":"জয়েন্ট সিগন্যাল সংগ্রহ", "READY":"প্রস্তুত", "START SENSOR RECORDING":"সেন্সর রেকর্ডিং শুরু করুন", "Joint-signal and movement sequence captured successfully.":"জয়েন্ট সিগন্যাল ও নড়াচড়ার ক্রম সফলভাবে রেকর্ড হয়েছে।", "Acquisition Complete":"সংগ্রহ সম্পূর্ণ", "Live Joint Signal":"লাইভ জয়েন্ট সিগন্যাল", "Time-Frequency Analysis":"সময়-ফ্রিকোয়েন্সি বিশ্লেষণ", "RUN MULTIMODAL AI ANALYSIS":"মাল্টিমোডাল AI বিশ্লেষণ চালান", "Prototype multimodal analysis completed.":"প্রোটোটাইপ মাল্টিমোডাল বিশ্লেষণ সম্পূর্ণ হয়েছে।", "AI Risk Analysis":"AI ঝুঁকি বিশ্লেষণ", "Screening grade, risk markers and supporting assessment findings":"স্ক্রিনিং গ্রেড, ঝুঁকি সূচক ও সহায়ক মূল্যায়ন ফলাফল", "PROTOTYPE / SIMULATED AI OUTPUT":"প্রোটোটাইপ / সিমুলেটেড AI আউটপুট", "Screening Grade":"স্ক্রিনিং গ্রেড", "RISK LEVEL":"ঝুঁকির স্তর", "IN SIMPLE WORDS":"সহজ ভাষায়", "What Did the System Find?":"সিস্টেম কী পেয়েছে?", "SCREENING DETAIL":"স্ক্রিনিং বিবরণ", "RESULT":"ফলাফল", "WHAT IT MEANS":"এর অর্থ", "Data quality":"ডেটার মান", "Sound patterns detected":"শব্দের প্যাটার্ন শনাক্ত হয়েছে", "Movement & Patient-Reported Findings":"নড়াচড়া ও রোগীর জানানো ফলাফল", "Movement range":"নড়াচড়ার পরিসর", "Left-right symmetry":"বাম-ডান সমতা", "Patient reported":"রোগীর জানানো", "Joint Signal Analysis":"জয়েন্ট সিগন্যাল বিশ্লেষণ", "Explainable Screening Factors":"ব্যাখ্যাযোগ্য স্ক্রিনিং কারণ", "Longitudinal Risk Monitoring":"দীর্ঘমেয়াদি ঝুঁকি পর্যবেক্ষণ", "Assessment Date":"মূল্যায়নের তারিখ", "Risk Index":"ঝুঁকি সূচক", "What Does This Mean for You?":"এর অর্থ কী?", "Predictive screening only. This system does not diagnose OA or prescribe treatment.":"শুধু পূর্বাভাসভিত্তিক স্ক্রিনিং। এই সিস্টেম OA নির্ণয় বা চিকিৎসা নির্ধারণ করে না।", "DOWNLOAD SCREENING REPORT":"স্ক্রিনিং রিপোর্ট ডাউনলোড করুন", "CONTINUE TO OA HUMAN DIGITAL TWIN →":"OA হিউম্যান ডিজিটাল টুইনে যান →", "OA Human Digital Twin":"OA হিউম্যান ডিজিটাল টুইন", "Patient Twin State":"রোগীর টুইন অবস্থা", "DIGITAL PATIENT MODEL":"ডিজিটাল রোগী মডেল", "Right Knee Profile":"ডান হাঁটুর প্রোফাইল", "MODERATE MARKER STATE":"মাঝারি সূচক অবস্থা", "Patient-Specific State Variables":"রোগী-নির্দিষ্ট অবস্থা ভেরিয়েবল", "Digital Twin Timeline":"ডিজিটাল টুইন টাইমলাইন", "Baseline Assessment":"বেসলাইন মূল্যায়ন", "Follow-up Assessment":"ফলো-আপ মূল্যায়ন", "Movement Assessment":"নড়াচড়ার মূল্যায়ন", "Current Assessment":"বর্তমান মূল্যায়ন", "Why a Digital Twin?":"ডিজিটাল টুইন কেন?", "Longitudinal":"দীর্ঘমেয়াদি", "Multimodal":"মাল্টিমোডাল", "Personalized":"ব্যক্তিগতকৃত", "VIEW PATIENT HISTORY →":"রোগীর ইতিহাস দেখুন →", "Longitudinal screening records and personalized baseline tracking":"দীর্ঘমেয়াদি স্ক্রিনিং রেকর্ড ও ব্যক্তিগত বেসলাইন ট্র্যাকিং", "Previous Assessments":"পূর্ববর্তী মূল্যায়ন", "Risk Markers":"ঝুঁকি সূচক", "Sound Events":"শব্দের ঘটনা", "Longitudinal Trends":"দীর্ঘমেয়াদি প্রবণতা", "Prototype Risk Index":"প্রোটোটাইপ ঝুঁকি সূচক", "Sound Event Trend":"শব্দ ঘটনার প্রবণতা", "Personalized Baseline":"ব্যক্তিগত বেসলাইন", "BASELINE ROM":"বেসলাইন ROM", "CURRENT ROM":"বর্তমান ROM", "BASELINE EVENTS":"বেসলাইন ঘটনা", "CURRENT EVENTS":"বর্তমান ঘটনা", "Screening Interpretation":"স্ক্রিনিং ব্যাখ্যা", "PERSONALIZED MONITORING":"ব্যক্তিগত পর্যবেক্ষণ", "No":"না", "Yes":"হ্যাঁ", "Female":"মহিলা", "Male":"পুরুষ", "Other":"অন্যান্য", "Low":"কম", "Moderate":"মাঝারি", "High":"উচ্চ", "Patient":"রোগী", "Phone":"ফোন", "Address":"ঠিকানা", "Knee Screen":"হাঁটু স্ক্রিন", "Fixed — Knee":"স্থির — হাঁটু", "Screening Type":"স্ক্রিনিংয়ের ধরন", "Multimodal predictive risk screening":"মাল্টিমোডাল পূর্বাভাসভিত্তিক ঝুঁকি স্ক্রিনিং", "Status":"স্ট্যাটাস", "Preliminary":"প্রাথমিক", "System":"সিস্টেম", "Grade Reference":"গ্রেডের রেফারেন্স", "Predictive Screening Result":"পূর্বাভাসভিত্তিক স্ক্রিনিং ফলাফল", "What the System Found":"সিস্টেম কী পেয়েছে", "Predictive Interpretation":"পূর্বাভাসভিত্তিক ব্যাখ্যা", "Important Information":"গুরুত্বপূর্ণ তথ্য"
    },
    "ne": {
        "DEPLOYMENT":"प्रयोग", "AI Engine — Ready":"AI इन्जिन — तयार", "Joint Signal Sensor — Connected":"जोइन्ट सिग्नल सेन्सर — जडान भएको", "IMU Module — Connected":"IMU मोड्युल — जडान भएको", "Local Database — Ready":"स्थानीय डाटाबेस — तयार", "NER / Rural Healthcare":"NER / ग्रामीण स्वास्थ्य सेवा", "Offline-ready architecture":"अफलाइन-रेडी संरचना", "Secure patient records":"सुरक्षित बिरामी अभिलेख", "ArthroSonic Prototype • SIH 2026":"ArthroSonic प्रोटोटाइप • SIH 2026", "AI-Assisted Osteoarthritis Screening":"AI-सहायित अस्टियोआर्थराइटिस स्क्रिनिङ", "Portable multimodal assessment platform for early OA risk identification":"प्रारम्भिक OA जोखिम पहिचानका लागि पोर्टेबल मल्टिमोडल मूल्याङ्कन प्लेटफर्म", "Live System Overview":"लाइभ प्रणाली अवलोकन", "ACTIVE PATIENT":"सक्रिय बिरामी", "Assessment ready":"मूल्याङ्कन तयार", "SENSOR STATUS":"सेन्सर स्थिति", "ONLINE":"अनलाइन", "SIGNAL QUALITY":"सिग्नल गुणस्तर", "Suitable for analysis":"विश्लेषणका लागि उपयुक्त", "ASSESSMENT MODE":"मूल्याङ्कन मोड", "MULTIMODAL":"मल्टिमोडल", "Multimodal Patient Profile":"मल्टिमोडल बिरामी प्रोफाइल", "CURRENT SCREENING":"हालको स्क्रिनिङ", "OA-associated risk markers":"OA-सम्बन्धी जोखिम सूचक", "DEMO OUTPUT":"डेमो आउटपुट", "MODERATE":"मध्यम", "Screening Workflow":"स्क्रिनिङ कार्यप्रवाह", "Symptoms + history":"लक्षण + इतिहास", "Joint sound + movement":"जोइन्ट ध्वनि + चाल", "Feature extraction":"फिचर निष्कर्षण", "Personalized output":"व्यक्तिगत आउटपुट", "Risk Report":"जोखिम रिपोर्ट", "START PATIENT PROFILE →":"बिरामी प्रोफाइल सुरु गर्नुहोस् →", "Create or reconnect a patient record before assessment":"मूल्याङ्कनअघि बिरामी अभिलेख बनाउनुहोस् वा पुनः जडान गर्नुहोस्", "Patient record confirmed":"बिरामी अभिलेख पुष्टि भयो", "Current screening can now be linked with the patient's longitudinal record.":"हालको स्क्रिनिङ अब बिरामीको दीर्घकालीन अभिलेखसँग जोड्न सकिन्छ।", "Prototype only: files are available during the current app session.":"प्रोटोटाइप मात्र: हालको एप सत्रमा फाइलहरू उपलब्ध छन्।", "Attached for this assessment:":"यस मूल्याङ्कनका लागि संलग्न:", "KNEE-ONLY SCREENING":"घुँडा मात्र स्क्रिनिङ", "Confirm the patient record to unlock document upload and the next step.":"कागजात अपलोड र अर्को चरण खोल्न बिरामी अभिलेख पुष्टि गर्नुहोस्।", "Sensor Assessment":"सेन्सर मूल्याङ्कन", "Guided acquisition of joint sound and movement signals":"जोइन्ट ध्वनि र चालका सिग्नलको निर्देशित सङ्कलन", "SCREENING SITE: KNEE ONLY":"स्क्रिनिङ स्थान: घुँडा मात्र", "Sensor Network":"सेन्सर नेटवर्क", "Guided Assessment Protocol":"निर्देशित मूल्याङ्कन प्रोटोकल", "Joint Signal":"जोइन्ट सिग्नल", "Movement":"चाल", "Symptoms":"लक्षण", "Joint Signal Acquisition":"जोइन्ट सिग्नल सङ्कलन", "READY":"तयार", "START SENSOR RECORDING":"सेन्सर रेकर्डिङ सुरु गर्नुहोस्", "Joint-signal and movement sequence captured successfully.":"जोइन्ट सिग्नल र चालको क्रम सफलतापूर्वक रेकर्ड भयो।", "Acquisition Complete":"सङ्कलन पूरा", "Live Joint Signal":"लाइभ जोइन्ट सिग्नल", "Time-Frequency Analysis":"समय-फ्रिक्वेन्सी विश्लेषण", "RUN MULTIMODAL AI ANALYSIS":"मल्टिमोडल AI विश्लेषण चलाउनुहोस्", "Prototype multimodal analysis completed.":"प्रोटोटाइप मल्टिमोडल विश्लेषण पूरा भयो।", "AI Risk Analysis":"AI जोखिम विश्लेषण", "Screening grade, risk markers and supporting assessment findings":"स्क्रिनिङ ग्रेड, जोखिम सूचक र सहायक मूल्याङ्कन निष्कर्ष", "PROTOTYPE / SIMULATED AI OUTPUT":"प्रोटोटाइप / सिमुलेटेड AI आउटपुट", "Screening Grade":"स्क्रिनिङ ग्रेड", "RISK LEVEL":"जोखिम स्तर", "IN SIMPLE WORDS":"सरल शब्दमा", "What Did the System Find?":"प्रणालीले के पत्ता लगायो?", "SCREENING DETAIL":"स्क्रिनिङ विवरण", "RESULT":"नतिजा", "WHAT IT MEANS":"यसको अर्थ", "Data quality":"डाटा गुणस्तर", "Sound patterns detected":"ध्वनि प्याटर्न पत्ता लाग्यो", "Movement & Patient-Reported Findings":"चाल र बिरामीले बताएका निष्कर्ष", "Movement range":"चालको दायरा", "Left-right symmetry":"बायाँ-दायाँ सममिति", "Patient reported":"बिरामीले बताएका", "Joint Signal Analysis":"जोइन्ट सिग्नल विश्लेषण", "Explainable Screening Factors":"व्याख्यायोग्य स्क्रिनिङ कारक", "Longitudinal Risk Monitoring":"दीर्घकालीन जोखिम निगरानी", "Assessment Date":"मूल्याङ्कन मिति", "Risk Index":"जोखिम सूचक", "What Does This Mean for You?":"यसको तपाईंका लागि के अर्थ छ?", "Predictive screening only. This system does not diagnose OA or prescribe treatment.":"केवल पूर्वानुमानात्मक स्क्रिनिङ। यो प्रणालीले OA निदान वा उपचार निर्धारण गर्दैन।", "DOWNLOAD SCREENING REPORT":"स्क्रिनिङ रिपोर्ट डाउनलोड गर्नुहोस्", "CONTINUE TO OA HUMAN DIGITAL TWIN →":"OA ह्युमन डिजिटल ट्विनमा जानुहोस् →", "OA Human Digital Twin":"OA ह्युमन डिजिटल ट्विन", "Patient Twin State":"बिरामी ट्विन अवस्था", "DIGITAL PATIENT MODEL":"डिजिटल बिरामी मोडेल", "Right Knee Profile":"दायाँ घुँडाको प्रोफाइल", "MODERATE MARKER STATE":"मध्यम सूचक अवस्था", "Patient-Specific State Variables":"बिरामी-विशिष्ट अवस्था चर", "Digital Twin Timeline":"डिजिटल ट्विन समयरेखा", "Baseline Assessment":"बेसलाइन मूल्याङ्कन", "Follow-up Assessment":"फलो-अप मूल्याङ्कन", "Movement Assessment":"चाल मूल्याङ्कन", "Current Assessment":"हालको मूल्याङ्कन", "Why a Digital Twin?":"डिजिटल ट्विन किन?", "Longitudinal":"दीर्घकालीन", "Multimodal":"मल्टिमोडल", "Personalized":"व्यक्तिगत", "VIEW PATIENT HISTORY →":"बिरामी इतिहास हेर्नुहोस् →", "Longitudinal screening records and personalized baseline tracking":"दीर्घकालीन स्क्रिनिङ अभिलेख र व्यक्तिगत बेसलाइन ट्र्याकिङ", "Previous Assessments":"अघिल्ला मूल्याङ्कन", "Risk Markers":"जोखिम सूचक", "Sound Events":"ध्वनि घटनाहरू", "Longitudinal Trends":"दीर्घकालीन प्रवृत्ति", "Prototype Risk Index":"प्रोटोटाइप जोखिम सूचक", "Sound Event Trend":"ध्वनि घटना प्रवृत्ति", "Personalized Baseline":"व्यक्तिगत बेसलाइन", "BASELINE ROM":"बेसलाइन ROM", "CURRENT ROM":"हालको ROM", "BASELINE EVENTS":"बेसलाइन घटनाहरू", "CURRENT EVENTS":"हालका घटनाहरू", "Screening Interpretation":"स्क्रिनिङ व्याख्या", "PERSONALIZED MONITORING":"व्यक्तिगत निगरानी", "No":"होइन", "Yes":"हो", "Female":"महिला", "Male":"पुरुष", "Other":"अन्य", "Low":"कम", "Moderate":"मध्यम", "High":"उच्च", "Patient":"बिरामी", "Phone":"फोन", "Address":"ठेगाना", "Knee Screen":"घुँडा स्क्रिन", "Fixed — Knee":"स्थिर — घुँडा", "Screening Type":"स्क्रिनिङ प्रकार", "Multimodal predictive risk screening":"मल्टिमोडल पूर्वानुमानात्मक जोखिम स्क्रिनिङ", "Status":"स्थिति", "Preliminary":"प्रारम्भिक", "System":"प्रणाली", "Grade Reference":"ग्रेड सन्दर्भ", "Predictive Screening Result":"पूर्वानुमानात्मक स्क्रिनिङ नतिजा", "What the System Found":"प्रणालीले के पत्ता लगायो", "Predictive Interpretation":"पूर्वानुमानात्मक व्याख्या", "Important Information":"महत्त्वपूर्ण जानकारी"
    }
}
for _lang, _pack in EXTRA_TRANSLATIONS.items():
    TRANSLATIONS.setdefault(_lang, {}).update(_pack)

# Exact longer phrases prevent partial/word-level replacements from leaving
# mixed-language sentences in cards and hero sections.
_EXTRA_EXACT = {
    "hi": {
        "Turning joint signals into actionable risk markers.": "जोड़ संकेतों को उपयोगी जोखिम संकेतकों में बदलना।",
        "ArthroSonic combines joint sound emissions, movement analysis, patient-reported symptoms and longitudinal data to support preliminary osteoarthritis risk screening in low-resource healthcare environments.": "ArthroSonic जोड़ की ध्वनि, गति विश्लेषण, रोगी द्वारा बताए गए लक्षण और दीर्घकालिक डेटा को जोड़कर सीमित संसाधनों वाले स्वास्थ्य वातावरण में प्रारंभिक ऑस्टियोआर्थराइटिस जोखिम स्क्रीनिंग में सहायता करता है।",
        "Prototype multimodal analysis indicates a moderate level of OA-associated markers.": "प्रोटोटाइप मल्टीमॉडल विश्लेषण OA-संबंधित संकेतकों के मध्यम स्तर को दर्शाता है।",
        "The screening joint is fixed and cannot be changed.": "स्क्रीनिंग जोड़ निश्चित है और बदला नहीं जा सकता।",
        "The ArthroSonic prototype measures the knee joint only.": "ArthroSonic प्रोटोटाइप केवल घुटने के जोड़ को मापता है।",
        "ArthroSonic is configured specifically for knee assessment.": "ArthroSonic विशेष रूप से घुटने के मूल्यांकन के लिए कॉन्फ़िगर किया गया है।",
        "Place the PZT and microphone module over the knee joint and perform controlled flexion-extension movements.": "PZT और माइक्रोफ़ोन मॉड्यूल को घुटने के जोड़ पर रखें और नियंत्रित फ्लेक्शन-एक्सटेंशन गति करें।",
        "Capture knee movement, gait, range of motion and left-right movement symmetry.": "घुटने की गति, चाल, गति सीमा और बाएँ-दाएँ गति समरूपता रिकॉर्ड करें।",
        "Combine patient-reported pain, stiffness, mobility and relevant risk factors.": "रोगी द्वारा बताए गए दर्द, जकड़न, गतिशीलता और संबंधित जोखिम कारकों को मिलाएँ।",
        "Signal quality is suitable for feature extraction and prototype AI analysis.": "सिग्नल गुणवत्ता फीचर निष्कर्षण और प्रोटोटाइप AI विश्लेषण के लिए उपयुक्त है।",
        "This page presents a preliminary screening interpretation for demonstration. It does not establish a medical diagnosis.": "यह पृष्ठ प्रदर्शन के लिए प्रारंभिक स्क्रीनिंग व्याख्या प्रस्तुत करता है। यह चिकित्सीय निदान स्थापित नहीं करता।",
        "From one-time screening to longitudinal monitoring.": "एक बार की स्क्रीनिंग से दीर्घकालिक निगरानी तक।",
        "The ArthroSonic Digital Twin organizes sound, movement, symptom and contextual measurements into a patient-specific longitudinal profile.": "ArthroSonic डिजिटल ट्विन ध्वनि, गति, लक्षण और संदर्भित मापों को रोगी-विशिष्ट दीर्घकालिक प्रोफ़ाइल में व्यवस्थित करता है।",
        "These variables form the current demonstration state of the digital twin.": "ये चर डिजिटल ट्विन की वर्तमान डेमो स्थिति बनाते हैं।",
        "ArthroSonic stores repeated screening measurements so that future assessments can be compared with the patient's own historical baseline.": "ArthroSonic बार-बार की गई स्क्रीनिंग माप संग्रहीत करता है ताकि भविष्य के मूल्यांकन की तुलना रोगी की अपनी ऐतिहासिक बेसलाइन से की जा सके।",
        "Changes in sound-pattern features, movement characteristics, symptoms and other recorded variables can therefore be visualized over time.": "ध्वनि-पैटर्न विशेषताओं, गति विशेषताओं, लक्षणों और अन्य रिकॉर्ड किए गए चर में बदलाव को समय के साथ देखा जा सकता है।",
        "Prototype for screening research and demonstration.": "स्क्रीनिंग अनुसंधान और प्रदर्शन के लिए प्रोटोटाइप।",
        "Not a medical diagnostic system.": "चिकित्सीय निदान प्रणाली नहीं है।",
        "AI-Assisted OA Risk Screening": "AI-सहायित OA जोखिम स्क्रीनिंग",
    },
    "as": {
        "Turning joint signals into actionable risk markers.": "জইণ্ট চিগনেলক ব্যৱহাৰযোগ্য ঝুঁকি সূচকলৈ ৰূপান্তৰ কৰা।",
        "ArthroSonic combines joint sound emissions, movement analysis, patient-reported symptoms and longitudinal data to support preliminary osteoarthritis risk screening in low-resource healthcare environments.": "ArthroSonic-এ জইণ্টৰ শব্দ, চলাচল বিশ্লেষণ, ৰোগীয়ে জনোৱা লক্ষণ আৰু দীৰ্ঘম্যাদী তথ্য একত্ৰ কৰি সীমিত সম্পদৰ স্বাস্থ্য পৰিৱেশত প্ৰাথমিক অষ্টিঅ’আৰ্থ্ৰাইটিছ ঝুঁকি স্ক্ৰিনিংত সহায় কৰে।",
        "Prototype multimodal analysis indicates a moderate level of OA-associated markers.": "প্ৰ’টোটাইপ মাল্টিম’ডেল বিশ্লেষণে OA-সম্পৰ্কীয় সূচকৰ মধ্যম স্তৰ দেখুৱায়।",
        "The screening joint is fixed and cannot be changed.": "স্ক্ৰিনিং জইণ্ট স্থিৰ আৰু সলনি কৰিব নোৱাৰি।",
        "The ArthroSonic prototype measures the knee joint only.": "ArthroSonic প্ৰ’টোটাইপে কেৱল আঁঠুৰ জইণ্ট মাপে।",
        "ArthroSonic is configured specifically for knee assessment.": "ArthroSonic বিশেষভাৱে আঁঠুৰ মূল্যায়নৰ বাবে কনফিগাৰ কৰা হৈছে।",
        "Place the PZT and microphone module over the knee joint and perform controlled flexion-extension movements.": "PZT আৰু মাইক্ৰ’ফোন মডিউল আঁঠুৰ জইণ্টৰ ওপৰত ৰাখি নিয়ন্ত্ৰিত ফ্লেক্সন-এক্সটেনচন চলাচল কৰক।",
        "Capture knee movement, gait, range of motion and left-right movement symmetry.": "আঁঠুৰ চলাচল, গেইট, চলাচলৰ পৰিসৰ আৰু বাওঁ-সোঁ সমমিতি ৰেকৰ্ড কৰক।",
        "Combine patient-reported pain, stiffness, mobility and relevant risk factors.": "ৰোগীয়ে জনোৱা বিষ, জড়তা, চলাচল আৰু প্ৰাসংগিক ঝুঁকি কাৰক একত্ৰ কৰক।",
        "Signal quality is suitable for feature extraction and prototype AI analysis.": "চিগনেলৰ গুণমান ফিচাৰ নিষ্কাশন আৰু প্ৰ’টোটাইপ AI বিশ্লেষণৰ বাবে উপযুক্ত।",
        "This page presents a preliminary screening interpretation for demonstration. It does not establish a medical diagnosis.": "এই পৃষ্ঠাই প্ৰদৰ্শনৰ বাবে প্ৰাথমিক স্ক্ৰিনিং ব্যাখ্যা দেখুৱায়। ই চিকিৎসাগত নিৰ্ণয় স্থাপন নকৰে।",
        "From one-time screening to longitudinal monitoring.": "এবাৰ কৰা স্ক্ৰিনিঙৰ পৰা দীৰ্ঘম্যাদী নিৰীক্ষণলৈ।",
        "The ArthroSonic Digital Twin organizes sound, movement, symptom and contextual measurements into a patient-specific longitudinal profile.": "ArthroSonic ডিজিটেল টুইনে শব্দ, চলাচল, লক্ষণ আৰু প্ৰাসংগিক মাপসমূহক ৰোগী-নিৰ্দিষ্ট দীৰ্ঘম্যাদী প্ৰ’ফাইলত সংগঠিত কৰে।",
        "These variables form the current demonstration state of the digital twin.": "এই চলকসমূহে ডিজিটেল টুইনৰ বৰ্তমান প্ৰদৰ্শন অৱস্থা গঠন কৰে।",
        "ArthroSonic stores repeated screening measurements so that future assessments can be compared with the patient's own historical baseline.": "ArthroSonic-এ পুনৰাবৃত্তি স্ক্ৰিনিং মাপ সংৰক্ষণ কৰে যাতে ভৱিষ্যতৰ মূল্যায়নক ৰোগীৰ নিজৰ ঐতিহাসিক বেচলাইনৰ সৈতে তুলনা কৰিব পাৰি।",
        "Changes in sound-pattern features, movement characteristics, symptoms and other recorded variables can therefore be visualized over time.": "শব্দ-পেটাৰ্ণ বৈশিষ্ট্য, চলাচলৰ বৈশিষ্ট্য, লক্ষণ আৰু আন ৰেকৰ্ড কৰা চলকসমূহৰ পৰিৱৰ্তন সময়ৰ সৈতে দেখা যাব পাৰে।",
        "Prototype for screening research and demonstration.": "স্ক্ৰিনিং গৱেষণা আৰু প্ৰদৰ্শনৰ বাবে প্ৰ’টোটাইপ।",
        "Not a medical diagnostic system.": "চিকিৎসাগত নিৰ্ণয় ব্যৱস্থা নহয়।",
    },
    "bn": {
        "Turning joint signals into actionable risk markers.": "জয়েন্ট সিগন্যালকে ব্যবহারযোগ্য ঝুঁকি সূচকে রূপান্তর করা।",
        "ArthroSonic combines joint sound emissions, movement analysis, patient-reported symptoms and longitudinal data to support preliminary osteoarthritis risk screening in low-resource healthcare environments.": "ArthroSonic জয়েন্টের শব্দ, নড়াচড়া বিশ্লেষণ, রোগীর জানানো উপসর্গ এবং দীর্ঘমেয়াদি ডেটা একত্র করে সীমিত সম্পদের স্বাস্থ্যসেবা পরিবেশে প্রাথমিক অস্টিওআর্থ্রাইটিস ঝুঁকি স্ক্রিনিংয়ে সহায়তা করে।",
        "Prototype multimodal analysis indicates a moderate level of OA-associated markers.": "প্রোটোটাইপ মাল্টিমোডাল বিশ্লেষণ OA-সম্পর্কিত সূচকের মাঝারি স্তর দেখায়।",
        "The screening joint is fixed and cannot be changed.": "স্ক্রিনিং জয়েন্ট স্থির এবং পরিবর্তন করা যাবে না।",
        "The ArthroSonic prototype measures the knee joint only.": "ArthroSonic প্রোটোটাইপ শুধু হাঁটুর জয়েন্ট মাপে।",
        "ArthroSonic is configured specifically for knee assessment.": "ArthroSonic বিশেষভাবে হাঁটুর মূল্যায়নের জন্য কনফিগার করা হয়েছে।",
        "Place the PZT and microphone module over the knee joint and perform controlled flexion-extension movements.": "PZT ও মাইক্রোফোন মডিউল হাঁটুর জয়েন্টের উপর রেখে নিয়ন্ত্রিত ফ্লেক্সন-এক্সটেনশন নড়াচড়া করুন।",
        "Capture knee movement, gait, range of motion and left-right movement symmetry.": "হাঁটুর নড়াচড়া, গেইট, নড়াচড়ার পরিসর এবং বাম-ডান সমতা রেকর্ড করুন।",
        "Combine patient-reported pain, stiffness, mobility and relevant risk factors.": "রোগীর জানানো ব্যথা, জড়তা, চলাচল এবং প্রাসঙ্গিক ঝুঁকির কারণ একত্র করুন।",
        "Signal quality is suitable for feature extraction and prototype AI analysis.": "সিগন্যালের মান ফিচার নিষ্কাশন ও প্রোটোটাইপ AI বিশ্লেষণের জন্য উপযুক্ত।",
        "This page presents a preliminary screening interpretation for demonstration. It does not establish a medical diagnosis.": "এই পৃষ্ঠাটি প্রদর্শনের জন্য প্রাথমিক স্ক্রিনিং ব্যাখ্যা দেখায়। এটি চিকিৎসাগত রোগনির্ণয় স্থাপন করে না।",
        "From one-time screening to longitudinal monitoring.": "একবারের স্ক্রিনিং থেকে দীর্ঘমেয়াদি পর্যবেক্ষণে।",
        "The ArthroSonic Digital Twin organizes sound, movement, symptom and contextual measurements into a patient-specific longitudinal profile.": "ArthroSonic ডিজিটাল টুইন শব্দ, নড়াচড়া, উপসর্গ ও প্রাসঙ্গিক মাপকে রোগী-নির্দিষ্ট দীর্ঘমেয়াদি প্রোফাইলে সাজায়।",
        "These variables form the current demonstration state of the digital twin.": "এই ভেরিয়েবলগুলো ডিজিটাল টুইনের বর্তমান প্রদর্শন অবস্থা তৈরি করে।",
        "ArthroSonic stores repeated screening measurements so that future assessments can be compared with the patient's own historical baseline.": "ArthroSonic বারবার করা স্ক্রিনিং মাপ সংরক্ষণ করে, যাতে ভবিষ্যৎ মূল্যায়ন রোগীর নিজস্ব ঐতিহাসিক বেসলাইনের সঙ্গে তুলনা করা যায়।",
        "Changes in sound-pattern features, movement characteristics, symptoms and other recorded variables can therefore be visualized over time.": "শব্দ-প্যাটার্ন বৈশিষ্ট্য, নড়াচড়ার বৈশিষ্ট্য, উপসর্গ ও অন্যান্য রেকর্ড করা ভেরিয়েবলের পরিবর্তন সময়ের সঙ্গে দেখা যায়।",
        "Prototype for screening research and demonstration.": "স্ক্রিনিং গবেষণা ও প্রদর্শনের জন্য প্রোটোটাইপ।",
        "Not a medical diagnostic system.": "এটি চিকিৎসাগত রোগনির্ণয় ব্যবস্থা নয়।",
    },
    "ne": {
        "Turning joint signals into actionable risk markers.": "जोइन्ट सिग्नललाई उपयोगी जोखिम सूचकमा रूपान्तरण गर्दै।",
        "ArthroSonic combines joint sound emissions, movement analysis, patient-reported symptoms and longitudinal data to support preliminary osteoarthritis risk screening in low-resource healthcare environments.": "ArthroSonic ले जोइन्ट ध्वनि, चाल विश्लेषण, बिरामीले बताएका लक्षण र दीर्घकालीन डाटा जोडेर सीमित स्रोत भएका स्वास्थ्य वातावरणमा प्रारम्भिक अस्टियोआर्थराइटिस जोखिम स्क्रिनिङमा सहयोग गर्छ।",
        "Prototype multimodal analysis indicates a moderate level of OA-associated markers.": "प्रोटोटाइप मल्टिमोडल विश्लेषणले OA-सम्बन्धी सूचकको मध्यम स्तर देखाउँछ।",
        "The screening joint is fixed and cannot be changed.": "स्क्रिनिङ जोइन्ट स्थिर छ र परिवर्तन गर्न सकिँदैन।",
        "The ArthroSonic prototype measures the knee joint only.": "ArthroSonic प्रोटोटाइपले घुँडाको जोइन्ट मात्र मापन गर्छ।",
        "ArthroSonic is configured specifically for knee assessment.": "ArthroSonic विशेष रूपमा घुँडा मूल्याङ्कनका लागि कन्फिगर गरिएको छ।",
        "Place the PZT and microphone module over the knee joint and perform controlled flexion-extension movements.": "PZT र माइक्रोफोन मोड्युल घुँडाको जोइन्टमाथि राखेर नियन्त्रित फ्लेक्सन-एक्सटेन्सन चाल गर्नुहोस्।",
        "Capture knee movement, gait, range of motion and left-right movement symmetry.": "घुँडाको चाल, गेट, चालको दायरा र बायाँ-दायाँ चाल सममिति रेकर्ड गर्नुहोस्।",
        "Combine patient-reported pain, stiffness, mobility and relevant risk factors.": "बिरामीले बताएका दुखाइ, कडापन, गतिशीलता र सम्बन्धित जोखिम कारकहरू जोड्नुहोस्।",
        "Signal quality is suitable for feature extraction and prototype AI analysis.": "सिग्नल गुणस्तर फिचर निष्कर्षण र प्रोटोटाइप AI विश्लेषणका लागि उपयुक्त छ।",
        "This page presents a preliminary screening interpretation for demonstration. It does not establish a medical diagnosis.": "यो पृष्ठले प्रदर्शनका लागि प्रारम्भिक स्क्रिनिङ व्याख्या देखाउँछ। यसले चिकित्सकीय निदान स्थापित गर्दैन।",
        "From one-time screening to longitudinal monitoring.": "एकपटकको स्क्रिनिङबाट दीर्घकालीन निगरानीसम्म।",
        "The ArthroSonic Digital Twin organizes sound, movement, symptom and contextual measurements into a patient-specific longitudinal profile.": "ArthroSonic डिजिटल ट्विनले ध्वनि, चाल, लक्षण र सन्दर्भित मापनलाई बिरामी-विशिष्ट दीर्घकालीन प्रोफाइलमा व्यवस्थित गर्छ।",
        "These variables form the current demonstration state of the digital twin.": "यी चरहरूले डिजिटल ट्विनको हालको प्रदर्शन अवस्था बनाउँछन्।",
        "ArthroSonic stores repeated screening measurements so that future assessments can be compared with the patient's own historical baseline.": "ArthroSonic ले दोहोरिएका स्क्रिनिङ मापनहरू भण्डारण गर्छ, ताकि भविष्यका मूल्याङ्कन बिरामीको आफ्नै ऐतिहासिक बेसलाइनसँग तुलना गर्न सकियोस्।",
        "Changes in sound-pattern features, movement characteristics, symptoms and other recorded variables can therefore be visualized over time.": "ध्वनि-प्याटर्न, चालका विशेषता, लक्षण र अन्य रेकर्ड गरिएका चरका परिवर्तन समयसँगै देखाउन सकिन्छ।",
        "Prototype for screening research and demonstration.": "स्क्रिनिङ अनुसन्धान र प्रदर्शनका लागि प्रोटोटाइप।",
        "Not a medical diagnostic system.": "यो चिकित्सकीय निदान प्रणाली होइन।",
    }
}
for _lang, _pack in _EXTRA_EXACT.items():
    TRANSLATIONS.setdefault(_lang, {}).update(_pack)


# Exact UI phrase pack.  These phrases are intentionally complete sentences/labels
# rather than word-by-word substitutions, so the UI never becomes a mixed-language
# sentence when a local language is selected.
EXTRA_UI_TRANSLATIONS = {
"hi": {
"AI-Assisted Osteoarthritis Screening":"AI-सहायित ऑस्टियोआर्थराइटिस स्क्रीनिंग",
"Portable multimodal assessment platform for early OA risk identification":"प्रारंभिक OA जोखिम पहचान के लिए पोर्टेबल मल्टीमॉडल मूल्यांकन प्लेटफ़ॉर्म",
"ARTHROSONIC • FIELD SCREENING PLATFORM":"ARTHROSONIC • फील्ड स्क्रीनिंग प्लेटफ़ॉर्म",
"Turning joint signals into":"जोड़ के संकेतों को बदलना",
"actionable risk markers.":"कार्रवाई योग्य जोखिम संकेतकों में।",
"ArthroSonic combines joint sound emissions, movement analysis, patient-reported symptoms and longitudinal data to support preliminary osteoarthritis risk screening in low-resource healthcare environments.":"ArthroSonic जोड़ की ध्वनि उत्सर्जन, गति विश्लेषण, रोगी द्वारा बताए गए लक्षण और दीर्घकालिक डेटा को मिलाकर सीमित संसाधनों वाले स्वास्थ्य वातावरण में प्रारंभिक ऑस्टियोआर्थराइटिस जोखिम स्क्रीनिंग में सहायता करता है।",
"Live System Overview":"लाइव सिस्टम अवलोकन",
"Multimodal Patient Profile":"मल्टीमॉडल रोगी प्रोफ़ाइल",
"Screening Workflow":"स्क्रीनिंग कार्यप्रवाह",
"ACTIVE PATIENT":"सक्रिय रोगी",
"Assessment ready":"मूल्यांकन तैयार है",
"SENSOR STATUS":"सेंसर स्थिति",
"PZT + Microphone + IMU":"PZT + माइक्रोफ़ोन + IMU",
"SIGNAL QUALITY":"सिग्नल गुणवत्ता",
"Suitable for analysis":"विश्लेषण के लिए उपयुक्त",
"ASSESSMENT MODE":"मूल्यांकन मोड",
"MULTIMODAL":"मल्टीमॉडल",
"PZT + microphone + gait + symptoms":"PZT + माइक्रोफ़ोन + चाल + लक्षण",
"CURRENT SCREENING":"वर्तमान स्क्रीनिंग",
"OA-associated risk markers":"OA-संबंधित जोखिम संकेतक",
"DEMO OUTPUT":"डेमो आउटपुट",
"MODERATE":"मध्यम",
"Prototype multimodal analysis indicates a moderate level of OA-associated markers.":"प्रोटोटाइप मल्टीमॉडल विश्लेषण OA-संबंधित संकेतकों का मध्यम स्तर दर्शाता है।",
"OA HUMAN DIGITAL TWIN":"OA ह्यूमन डिजिटल ट्विन",
"Patient Movement State":"रोगी की गति स्थिति",
"Longitudinal representation of movement, sound-pattern and symptom characteristics.":"गति, ध्वनि-पैटर्न और लक्षण संबंधी विशेषताओं का दीर्घकालिक प्रतिनिधित्व।",
"Knee ROM":"घुटने की गति सीमा",
"Symmetry":"समरूपता",
"Gait m/s":"चाल मी/से",
"STEP":"चरण",
"Patient Profile":"रोगी प्रोफ़ाइल",
"Symptoms + history":"लक्षण + इतिहास",
"Sensor Capture":"सेंसर कैप्चर",
"Joint sound + movement":"जोड़ की ध्वनि + गति",
"AI Fusion":"AI फ्यूज़न",
"Feature extraction":"फीचर निष्कर्षण",
"Risk Report":"जोखिम रिपोर्ट",
"Personalized output":"व्यक्तिगत आउटपुट",
"Create or reconnect a patient record before assessment":"मूल्यांकन से पहले रोगी रिकॉर्ड बनाएँ या पुनः कनेक्ट करें",
"1. Patient Information":"1. रोगी जानकारी",
"2. Connect Patient Record":"2. रोगी रिकॉर्ड कनेक्ट करें",
"✓ Patient record confirmed":"✓ रोगी रिकॉर्ड की पुष्टि हो गई",
"Current screening can now be linked with the patient's longitudinal record.":"वर्तमान स्क्रीनिंग अब रोगी के दीर्घकालिक रिकॉर्ड से जोड़ी जा सकती है।",
"3. Latest Reports & Medical Documents":"3. नवीनतम रिपोर्ट और चिकित्सा दस्तावेज़",
"4. OA Risk Factors & Symptoms":"4. OA जोखिम कारक और लक्षण",
"Attached for this assessment:":"इस मूल्यांकन के लिए संलग्न:",
"🦵 KNEE-ONLY SCREENING":"🦵 केवल घुटने की स्क्रीनिंग",
"The ArthroSonic prototype measures the":"ArthroSonic प्रोटोटाइप केवल",
"knee joint only":"घुटने के जोड़ को मापता है",
"The screening site is fixed and cannot be changed.":"स्क्रीनिंग साइट निश्चित है और बदली नहीं जा सकती।",
"Sensor Assessment":"सेंसर मूल्यांकन",
"Guided acquisition of joint sound and movement signals":"जोड़ की ध्वनि और गति संकेतों का निर्देशित अधिग्रहण",
"🦵 SCREENING SITE: KNEE ONLY":"🦵 स्क्रीनिंग साइट: केवल घुटना",
"ArthroSonic is configured specifically for knee assessment. The screening joint is fixed and cannot be changed.":"ArthroSonic विशेष रूप से घुटने के मूल्यांकन के लिए कॉन्फ़िगर किया गया है। स्क्रीनिंग जोड़ निश्चित है और बदला नहीं जा सकता।",
"Sensor Network":"सेंसर नेटवर्क",
"Knee vibration + joint sound":"घुटने का कंपन + जोड़ की ध्वनि",
"Movement + posture + gait":"गति + मुद्रा + चाल",
"Gait assessment":"चाल मूल्यांकन",
"Excellent acquisition":"उत्कृष्ट अधिग्रहण",
"Guided Assessment Protocol":"निर्देशित मूल्यांकन प्रोटोकॉल",
"01 · Joint Signal":"01 · जोड़ संकेत",
"Place the PZT and microphone module over the knee joint and perform controlled flexion-extension movements.":"PZT और माइक्रोफ़ोन मॉड्यूल को घुटने के जोड़ पर रखें और नियंत्रित फ्लेक्शन-एक्सटेंशन गति करें।",
"02 · Movement":"02 · गति",
"Capture knee movement, gait, range of motion and left-right movement symmetry.":"घुटने की गति, चाल, गति सीमा और बाएँ-दाएँ गति समरूपता रिकॉर्ड करें।",
"03 · Symptoms":"03 · लक्षण",
"Combine patient-reported pain, stiffness, mobility and relevant risk factors.":"रोगी द्वारा बताए गए दर्द, जकड़न, गतिशीलता और संबंधित जोखिम कारकों को मिलाएँ।",
"Joint Signal Acquisition":"जोड़ संकेत अधिग्रहण",
"READY":"तैयार",
"Acquisition Complete":"अधिग्रहण पूर्ण",
"Signal quality is suitable for feature extraction and prototype AI analysis.":"सिग्नल गुणवत्ता फीचर निष्कर्षण और प्रोटोटाइप AI विश्लेषण के लिए उपयुक्त है।",
"Live Joint Signal":"लाइव जोड़ संकेत",
"Time-Frequency Analysis":"समय-आवृत्ति विश्लेषण",
"DURATION":"अवधि",
"Recording":"रिकॉर्डिंग",
"EVENTS":"घटनाएँ",
"Detected sound events":"पता चली ध्वनि घटनाएँ",
"SAMPLING":"सैंपलिंग",
"Acquisition rate":"अधिग्रहण दर",
"QUALITY":"गुणवत्ता",
"Signal quality index":"सिग्नल गुणवत्ता सूचकांक",
"AI Risk Analysis":"AI जोखिम विश्लेषण",
"Screening grade, risk markers and supporting assessment findings":"स्क्रीनिंग ग्रेड, जोखिम संकेतक और सहायक मूल्यांकन निष्कर्ष",
"PROTOTYPE / SIMULATED AI OUTPUT":"प्रोटोटाइप / सिम्युलेटेड AI आउटपुट",
"This page presents a preliminary screening interpretation for demonstration. It does not establish a medical diagnosis.":"यह पृष्ठ प्रदर्शन के लिए प्रारंभिक स्क्रीनिंग व्याख्या प्रस्तुत करता है। यह चिकित्सीय निदान स्थापित नहीं करता।",
"Screening Grade":"स्क्रीनिंग ग्रेड",
"OA-ASSOCIATED RISK SCORE":"OA-संबंधित जोखिम स्कोर",
"Prototype screening index":"प्रोटोटाइप स्क्रीनिंग सूचकांक",
"DATA QUALITY":"डेटा गुणवत्ता",
"Good input quality; not OA probability":"इनपुट गुणवत्ता अच्छी है; यह OA की संभावना नहीं है",
"What Do the Grades Mean?":"ग्रेड का क्या अर्थ है?",
"What Did the System Find?":"सिस्टम ने क्या पाया?",
"SCREENING DETAIL":"स्क्रीनिंग विवरण",
"RESULT":"परिणाम",
"WHAT IT MEANS":"इसका अर्थ",
"Movement & Patient-Reported Findings":"गति और रोगी द्वारा बताए गए निष्कर्ष",
"KNEE ROM":"घुटने की गति सीमा",
"GAIT SYMMETRY":"चाल समरूपता",
"Left-right symmetry":"बाएँ-दाएँ समरूपता",
"PAIN":"दर्द",
"Patient reported":"रोगी द्वारा बताया गया",
"STIFFNESS":"जकड़न",
"Joint Signal Analysis":"जोड़ संकेत विश्लेषण",
"Explainable Screening Factors":"व्याख्यायोग्य स्क्रीनिंग कारक",
"Sound + vibration events":"ध्वनि + कंपन घटनाएँ",
"17 patterns detected during the prototype movement sequence.":"प्रोटोटाइप गति अनुक्रम के दौरान 17 पैटर्न पाए गए।",
"Movement symmetry":"गति समरूपता",
"Mild left-right movement asymmetry is present in the demonstration profile.":"डेमो प्रोफ़ाइल में हल्की बाएँ-दाएँ गति असममिति मौजूद है।",
"Range of motion":"गति सीमा",
"The recorded knee range of motion is 108° in the demonstration profile.":"डेमो प्रोफ़ाइल में दर्ज घुटने की गति सीमा 108° है।",
"Reported symptoms":"बताए गए लक्षण",
"Pain and stiffness inputs contribute to the multimodal screening profile.":"दर्द और जकड़न इनपुट मल्टीमॉडल स्क्रीनिंग प्रोफ़ाइल में योगदान करते हैं।",
"Longitudinal Risk Monitoring":"दीर्घकालिक जोखिम निगरानी",
"What Does This Mean for You?":"आपके लिए इसका क्या अर्थ है?",
"Your result is Grade 1 (Low Risk). This does not mean you definitely do not have osteoarthritis. It means the system found few OA-related risk markers. If you have joint pain, stiffness, swelling, or trouble moving, share this with a doctor.":"आपका परिणाम ग्रेड 1 (कम जोखिम) है। इसका अर्थ यह नहीं है कि आपको निश्चित रूप से ऑस्टियोआर्थराइटिस नहीं है। इसका अर्थ है कि सिस्टम ने कुछ OA-संबंधित जोखिम संकेतक पाए। यदि आपको जोड़ में दर्द, जकड़न, सूजन या चलने-फिरने में कठिनाई है, तो इसे डॉक्टर के साथ साझा करें।",
"Your result is Grade 2 (Medium Risk). This does not mean you definitely have osteoarthritis. It means the system found some signs that may need further checking. If you have joint pain, stiffness, swelling, or trouble moving, share this with a doctor.":"आपका परिणाम ग्रेड 2 (मध्यम जोखिम) है। इसका अर्थ यह नहीं है कि आपको निश्चित रूप से ऑस्टियोआर्थराइटिस है। इसका अर्थ है कि सिस्टम ने कुछ ऐसे संकेत पाए हैं जिनकी आगे जाँच की आवश्यकता हो सकती है। यदि आपको जोड़ में दर्द, जकड़न, सूजन या चलने-फिरने में कठिनाई है, तो इसे डॉक्टर के साथ साझा करें।",
"Your result is Grade 3 (High Risk). This does not mean you definitely have osteoarthritis. It means the system found more OA-related risk markers that may need further checking. If you have joint pain, stiffness, swelling, or trouble moving, share this with a doctor.":"आपका परिणाम ग्रेड 3 (उच्च जोखिम) है। इसका अर्थ यह नहीं है कि आपको निश्चित रूप से ऑस्टियोआर्थराइटिस है। इसका अर्थ है कि सिस्टम ने अधिक OA-संबंधित जोखिम संकेतक पाए हैं जिनकी आगे जाँच की आवश्यकता हो सकती है। यदि आपको जोड़ में दर्द, जकड़न, सूजन या चलने-फिरने में कठिनाई है, तो इसे डॉक्टर के साथ साझा करें।",
"Predictive screening only. This system does not diagnose OA or prescribe treatment.":"केवल पूर्वानुमानात्मक स्क्रीनिंग। यह सिस्टम OA का निदान या उपचार निर्धारित नहीं करता।",
"OA Human Digital Twin":"OA ह्यूमन डिजिटल ट्विन",
"Longitudinal digital representation of patient-specific OA-related characteristics":"रोगी-विशिष्ट OA-संबंधित विशेषताओं का दीर्घकालिक डिजिटल प्रतिनिधित्व",
"PATIENT DIGITAL REPRESENTATION":"रोगी का डिजिटल प्रतिनिधित्व",
"From one-time screening to longitudinal monitoring.":"एक बार की स्क्रीनिंग से दीर्घकालिक निगरानी तक।",
"The ArthroSonic Digital Twin organizes sound, movement, symptom and contextual measurements into a patient-specific longitudinal profile.":"ArthroSonic डिजिटल ट्विन ध्वनि, गति, लक्षण और संदर्भ संबंधी मापों को रोगी-विशिष्ट दीर्घकालिक प्रोफ़ाइल में व्यवस्थित करता है।",
"Patient Twin State":"रोगी ट्विन स्थिति",
"DIGITAL PATIENT MODEL":"डिजिटल रोगी मॉडल",
"Right Knee Profile":"दाएँ घुटने की प्रोफ़ाइल",
"MODERATE MARKER STATE":"मध्यम संकेतक स्थिति",
"Patient-Specific State Variables":"रोगी-विशिष्ट स्थिति चर",
"These variables form the current demonstration state of the digital twin.":"ये चर डिजिटल ट्विन की वर्तमान डेमो स्थिति बनाते हैं।",
"Knee Sound + Vibration Signature":"घुटने की ध्वनि + कंपन सिग्नेचर",
"17 events":"17 घटनाएँ",
"Knee Range of Motion":"घुटने की गति सीमा",
"Gait Symmetry":"चाल समरूपता",
"Reported Pain":"बताया गया दर्द",
"Gait Speed":"चाल की गति",
"Digital Twin Timeline":"डिजिटल ट्विन समयरेखा",
"Baseline Assessment":"बेसलाइन मूल्यांकन",
"Initial patient movement and joint-signal profile recorded.":"प्रारंभिक रोगी गति और जोड़-सिग्नल प्रोफ़ाइल रिकॉर्ड की गई।",
"Follow-up Assessment":"फॉलो-अप मूल्यांकन",
"Longitudinal measurements added to patient profile.":"दीर्घकालिक माप रोगी प्रोफ़ाइल में जोड़े गए।",
"Movement Assessment":"गति मूल्यांकन",
"Updated gait and knee movement characteristics.":"चाल और घुटने की गति की विशेषताएँ अपडेट की गईं।",
"Current Assessment":"वर्तमान मूल्यांकन",
"Latest multimodal screening profile generated.":"नवीनतम मल्टीमॉडल स्क्रीनिंग प्रोफ़ाइल तैयार की गई।",
"Why a Digital Twin?":"डिजिटल ट्विन क्यों?",
"Longitudinal":"दीर्घकालिक",
"Compare future measurements against the patient's own baseline.":"भविष्य के मापों की तुलना रोगी की अपनी बेसलाइन से करें।",
"Multimodal":"मल्टीमॉडल",
"Combine sound, movement and symptom information.":"ध्वनि, गति और लक्षणों की जानकारी को मिलाएँ।",
"Personalized":"व्यक्तिगत",
"Represent patient-specific characteristics rather than relying only on population averages.":"केवल जनसंख्या औसत पर निर्भर रहने के बजाय रोगी-विशिष्ट विशेषताओं का प्रतिनिधित्व करें।",
"Patient History":"रोगी इतिहास",
"Longitudinal screening records and personalized baseline tracking":"दीर्घकालिक स्क्रीनिंग रिकॉर्ड और व्यक्तिगत बेसलाइन ट्रैकिंग",
"PATIENT RECORD":"रोगी रिकॉर्ड",
"Previous Assessments":"पिछले मूल्यांकन",
"Longitudinal Trends":"दीर्घकालिक रुझान",
"Personalized Baseline":"व्यक्तिगत बेसलाइन",
"Screening Interpretation":"स्क्रीनिंग व्याख्या",
"Longitudinal monitoring":"दीर्घकालिक निगरानी",
"ArthroSonic stores repeated screening measurements so that future assessments can be compared with the patient's own historical baseline.":"ArthroSonic बार-बार की गई स्क्रीनिंग मापों को संग्रहीत करता है ताकि भविष्य के मूल्यांकन की तुलना रोगी की अपनी ऐतिहासिक बेसलाइन से की जा सके।",
"Changes in sound-pattern features, movement characteristics, symptoms and other recorded variables can therefore be visualized over time.":"इस प्रकार ध्वनि-पैटर्न फीचर, गति विशेषताओं, लक्षणों और अन्य रिकॉर्ड किए गए चरों में बदलावों को समय के साथ देखा जा सकता है।",
"PERSONALIZED MONITORING":"व्यक्तिगत निगरानी",
"BASELINE ROM":"बेसलाइन गति सीमा",
"CURRENT ROM":"वर्तमान गति सीमा",
"BASELINE EVENTS":"बेसलाइन घटनाएँ",
"CURRENT EVENTS":"वर्तमान घटनाएँ",
"AI Engine — Ready":"AI इंजन — तैयार",
"Joint Signal Sensor — Connected":"जोड़ सिग्नल सेंसर — कनेक्टेड",
"IMU Module — Connected":"IMU मॉड्यूल — कनेक्टेड",
"Local Database — Ready":"स्थानीय डेटाबेस — तैयार",
"NER / Rural Healthcare":"NER / ग्रामीण स्वास्थ्य सेवा",
"Offline-ready architecture":"ऑफ़लाइन-तैयार आर्किटेक्चर",
"Secure patient records":"सुरक्षित रोगी रिकॉर्ड",
"ArthroSonic Prototype • SIH 2026":"ArthroSonic प्रोटोटाइप • SIH 2026",
"STEP 01":"चरण 01","STEP 02":"चरण 02","STEP 03":"चरण 03","STEP 04":"चरण 04",
},
"as": {
"AI-Assisted Osteoarthritis Screening":"AI-সহায়িত অষ্টিঅ’আৰ্থ্ৰাইটিছ স্ক্ৰিনিং",
"Portable multimodal assessment platform for early OA risk identification":"আৰম্ভণিৰ OA ঝুঁকি চিনাক্তকৰণৰ বাবে প’ৰ্টেবল মাল্টিম’ডেল মূল্যায়ন প্লেটফৰ্ম",
"ARTHROSONIC • FIELD SCREENING PLATFORM":"ARTHROSONIC • ফিল্ড স্ক্ৰিনিং প্লেটফৰ্ম",
"Turning joint signals into":"জইণ্টৰ সংকেতক ৰূপান্তৰ কৰা",
"actionable risk markers.":"কাৰ্যকৰী ঝুঁকি সূচকলৈ।",
"ArthroSonic combines joint sound emissions, movement analysis, patient-reported symptoms and longitudinal data to support preliminary osteoarthritis risk screening in low-resource healthcare environments.":"ArthroSonic-এ জইণ্টৰ শব্দ নিৰ্গমন, চলাচল বিশ্লেষণ, ৰোগীয়ে জনোৱা লক্ষণ আৰু দীৰ্ঘম্যাদী তথ্য একত্ৰ কৰি সীমিত সম্পদৰ স্বাস্থ্যসেৱা পৰিৱেশত প্ৰাথমিক অষ্টিঅ’আৰ্থ্ৰাইটিছ ঝুঁকি স্ক্ৰিনিংত সহায় কৰে।",
"Live System Overview":"লাইভ চিষ্টেমৰ অভাৰভিউ","Multimodal Patient Profile":"মাল্টিম’ডেল ৰোগী প্ৰ’ফাইল","Screening Workflow":"স্ক্ৰিনিং কাৰ্যপ্ৰবাহ","ACTIVE PATIENT":"সক্ৰিয় ৰোগী","Assessment ready":"মূল্যায়ন সাজু","SENSOR STATUS":"ছেন্সৰৰ স্থিতি","SIGNAL QUALITY":"চিগনেলৰ গুণমান","Suitable for analysis":"বিশ্লেষণৰ বাবে উপযুক্ত","ASSESSMENT MODE":"মূল্যায়ন মোড","MULTIMODAL":"মাল্টিম’ডেল","CURRENT SCREENING":"বৰ্তমান স্ক্ৰিনিং","OA-associated risk markers":"OA-সম্পৰ্কীয় ঝুঁকি সূচক","DEMO OUTPUT":"ডেম’ আউটপুট","MODERATE":"মধ্যম","Prototype multimodal analysis indicates a moderate level of OA-associated markers.":"প্ৰ’টোটাইপ মাল্টিম’ডেল বিশ্লেষণে OA-সম্পৰ্কীয় সূচকৰ মধ্যম স্তৰ দেখুৱায়।","OA HUMAN DIGITAL TWIN":"OA হিউমেন ডিজিটেল টুইন","Patient Movement State":"ৰোগীৰ চলাচলৰ অৱস্থা","Longitudinal representation of movement, sound-pattern and symptom characteristics.":"চলাচল, শব্দ-পেটাৰ্ণ আৰু লক্ষণৰ বৈশিষ্ট্যৰ দীৰ্ঘম্যাদী প্ৰতিনিধিত্ব।","Knee ROM":"আঁঠুৰ গতি পৰিসৰ","Symmetry":"সমমিতি","Gait m/s":"গেইট মি/ছে","Patient Profile":"ৰোগীৰ প্ৰ’ফাইল","Symptoms + history":"লক্ষণ + ইতিহাস","Sensor Capture":"ছেন্সৰ কেপচাৰ","Joint sound + movement":"জইণ্টৰ শব্দ + চলাচল","AI Fusion":"AI ফিউজন","Feature extraction":"ফিচাৰ নিষ্কাশন","Risk Report":"ঝুঁকি প্ৰতিবেদন","Personalized output":"ব্যক্তিগত আউটপুট",
"Create or reconnect a patient record before assessment":"মূল্যায়নৰ আগতে ৰোগীৰ ৰেকৰ্ড সৃষ্টি বা পুনৰ সংযোগ কৰক","1. Patient Information":"1. ৰোগীৰ তথ্য","2. Connect Patient Record":"2. ৰোগীৰ ৰেকৰ্ড সংযোগ কৰক","✓ Patient record confirmed":"✓ ৰোগীৰ ৰেকৰ্ড নিশ্চিত কৰা হৈছে","Current screening can now be linked with the patient's longitudinal record.":"বৰ্তমান স্ক্ৰিনিং এতিয়া ৰোগীৰ দীৰ্ঘম্যাদী ৰেকৰ্ডৰ সৈতে সংযোগ কৰিব পাৰি।","3. Latest Reports & Medical Documents":"3. শেহতীয়া প্ৰতিবেদন আৰু চিকিৎসা নথি","4. OA Risk Factors & Symptoms":"4. OA ঝুঁকি কাৰক আৰু লক্ষণ","Attached for this assessment:":"এই মূল্যায়নৰ বাবে সংলগ্ন:","🦵 KNEE-ONLY SCREENING":"🦵 কেৱল আঁঠুৰ স্ক্ৰিনিং","The screening site is fixed and cannot be changed.":"স্ক্ৰিনিং স্থান নিৰ্দিষ্ট আৰু সলনি কৰিব নোৱাৰি।","Sensor Assessment":"ছেন্সৰ মূল্যায়ন","Guided acquisition of joint sound and movement signals":"জইণ্টৰ শব্দ আৰু চলাচল সংকেতৰ নিৰ্দেশিত অধিগ্ৰহণ","🦵 SCREENING SITE: KNEE ONLY":"🦵 স্ক্ৰিনিং স্থান: কেৱল আঁঠু","ArthroSonic is configured specifically for knee assessment. The screening joint is fixed and cannot be changed.":"ArthroSonic বিশেষভাৱে আঁঠুৰ মূল্যায়নৰ বাবে কনফিগাৰ কৰা হৈছে। স্ক্ৰিনিং জইণ্ট নিৰ্দিষ্ট আৰু সলনি কৰিব নোৱাৰি।","Sensor Network":"ছেন্সৰ নেটৱৰ্ক","Knee vibration + joint sound":"আঁঠুৰ কম্পন + জইণ্টৰ শব্দ","Movement + posture + gait":"চলাচল + ভংগী + গেইট","Gait assessment":"গেইট মূল্যায়ন","Excellent acquisition":"উৎকৃষ্ট অধিগ্ৰহণ","Guided Assessment Protocol":"নিৰ্দেশিত মূল্যায়ন প্ৰট’কল","01 · Joint Signal":"01 · জইণ্ট সংকেত","Place the PZT and microphone module over the knee joint and perform controlled flexion-extension movements.":"PZT আৰু মাইক্ৰ’ফোন মডিউল আঁঠুৰ জইণ্টৰ ওপৰত ৰাখি নিয়ন্ত্ৰিত ফ্লেক্সন-এক্সটেনশ্যন চলাচল কৰক।","02 · Movement":"02 · চলাচল","Capture knee movement, gait, range of motion and left-right movement symmetry.":"আঁঠুৰ চলাচল, গেইট, গতি পৰিসৰ আৰু বাওঁ-সোঁ চলাচলৰ সমমিতি ৰেকৰ্ড কৰক।","03 · Symptoms":"03 · লক্ষণ","Combine patient-reported pain, stiffness, mobility and relevant risk factors.":"ৰোগীয়ে জনোৱা বিষ, জড়তা, চলাচল ক্ষমতা আৰু প্ৰাসংগিক ঝুঁকি কাৰক একত্ৰ কৰক।","Joint Signal Acquisition":"জইণ্ট সংকেত অধিগ্ৰহণ","READY":"সাজু","Acquisition Complete":"অধিগ্ৰহণ সম্পূৰ্ণ","Signal quality is suitable for feature extraction and prototype AI analysis.":"চিগনেলৰ গুণমান ফিচাৰ নিষ্কাশন আৰু প্ৰ’টোটাইপ AI বিশ্লেষণৰ বাবে উপযুক্ত।","Live Joint Signal":"লাইভ জইণ্ট সংকেত","Time-Frequency Analysis":"সময়-কম্পনাংক বিশ্লেষণ","DURATION":"সময়কাল","Recording":"ৰেকৰ্ডিং","EVENTS":"ঘটনা","Detected sound events":"ধৰা পৰা শব্দৰ ঘটনা","SAMPLING":"চেম্পলিং","Acquisition rate":"অধিগ্ৰহণ হাৰ","QUALITY":"গুণমান","Signal quality index":"চিগনেল গুণমান সূচক","AI Risk Analysis":"AI ঝুঁকি বিশ্লেষণ","Screening grade, risk markers and supporting assessment findings":"স্ক্ৰিনিং গ্ৰেড, ঝুঁকি সূচক আৰু সহায়ক মূল্যায়ন ফলাফল","PROTOTYPE / SIMULATED AI OUTPUT":"প্ৰ’টোটাইপ / চিমুলেটেড AI আউটপুট","This page presents a preliminary screening interpretation for demonstration. It does not establish a medical diagnosis.":"এই পৃষ্ঠাই প্ৰদৰ্শনৰ বাবে প্ৰাথমিক স্ক্ৰিনিং ব্যাখ্যা দেখুৱায়। ই চিকিৎসাগত নিৰ্ণয় স্থাপন নকৰে।","Screening Grade":"স্ক্ৰিনিং গ্ৰেড","OA-ASSOCIATED RISK SCORE":"OA-সম্পৰ্কীয় ঝুঁকি স্ক’ৰ","Prototype screening index":"প্ৰ’টোটাইপ স্ক্ৰিনিং সূচক","DATA QUALITY":"তথ্যৰ গুণমান","Good input quality; not OA probability":"ইনপুটৰ গুণমান ভাল; ই OA-ৰ সম্ভাৱনা নহয়","What Do the Grades Mean?":"গ্ৰেডে কি বুজায়?","What Did the System Find?":"চিষ্টেমে কি পাইছে?","SCREENING DETAIL":"স্ক্ৰিনিং বিৱৰণ","RESULT":"ফলাফল","WHAT IT MEANS":"ইয়াৰ অৰ্থ","Movement & Patient-Reported Findings":"চলাচল আৰু ৰোগীয়ে জনোৱা ফলাফল","KNEE ROM":"আঁঠুৰ গতি পৰিসৰ","GAIT SYMMETRY":"গেইট সমমিতি","Left-right symmetry":"বাওঁ-সোঁ সমমিতি","PAIN":"বিষ","Patient reported":"ৰোগীয়ে জনোৱা","STIFFNESS":"জড়তা","Joint Signal Analysis":"জইণ্ট সংকেত বিশ্লেষণ","Explainable Screening Factors":"ব্যাখ্যাযোগ্য স্ক্ৰিনিং কাৰক","Sound + vibration events":"শব্দ + কম্পন ঘটনা","17 patterns detected during the prototype movement sequence.":"প্ৰ’টোটাইপ চলাচল ক্ৰমত 17টা পেটাৰ্ণ ধৰা পৰিছে।","Movement symmetry":"চলাচল সমমিতি","Mild left-right movement asymmetry is present in the demonstration profile.":"ডেম’ প্ৰ’ফাইলত সামান্য বাওঁ-সোঁ চলাচলৰ অসমমিতি আছে।","Range of motion":"গতি পৰিসৰ","The recorded knee range of motion is 108° in the demonstration profile.":"ডেম’ প্ৰ’ফাইলত ৰেকৰ্ড কৰা আঁঠুৰ গতি পৰিসৰ 108°।","Reported symptoms":"জনোৱা লক্ষণ","Pain and stiffness inputs contribute to the multimodal screening profile.":"বিষ আৰু জড়তাৰ ইনপুটে মাল্টিম’ডেল স্ক্ৰিনিং প্ৰ’ফাইলত অৰিহণা যোগায়।","Longitudinal Risk Monitoring":"দীৰ্ঘম্যাদী ঝুঁকি নিৰীক্ষণ","What Does This Mean for You?":"আপোনাৰ বাবে ইয়াৰ অৰ্থ কি?","Predictive screening only. This system does not diagnose OA or prescribe treatment.":"কেৱল পূৰ্বানুমানমূলক স্ক্ৰিনিং। এই চিষ্টেমে OA নিৰ্ণয় বা চিকিৎসা নিৰ্ধাৰণ নকৰে।","OA Human Digital Twin":"OA হিউমেন ডিজিটেল টুইন","Longitudinal digital representation of patient-specific OA-related characteristics":"ৰোগী-নিৰ্দিষ্ট OA-সম্পৰ্কীয় বৈশিষ্ট্যৰ দীৰ্ঘম্যাদী ডিজিটেল প্ৰতিনিধিত্ব","PATIENT DIGITAL REPRESENTATION":"ৰোগীৰ ডিজিটেল প্ৰতিনিধিত্ব","From one-time screening to longitudinal monitoring.":"এবাৰৰ স্ক্ৰিনিঙৰ পৰা দীৰ্ঘম্যাদী নিৰীক্ষণলৈ।","The ArthroSonic Digital Twin organizes sound, movement, symptom and contextual measurements into a patient-specific longitudinal profile.":"ArthroSonic ডিজিটেল টুইনে শব্দ, চলাচল, লক্ষণ আৰু প্ৰাসংগিক মাপসমূহক ৰোগী-নিৰ্দিষ্ট দীৰ্ঘম্যাদী প্ৰ’ফাইলত সংগঠিত কৰে।","Patient Twin State":"ৰোগী টুইনৰ অৱস্থা","DIGITAL PATIENT MODEL":"ডিজিটেল ৰোগী মডেল","Right Knee Profile":"সোঁ আঁঠুৰ প্ৰ’ফাইল","MODERATE MARKER STATE":"মধ্যম সূচক অৱস্থা","Patient-Specific State Variables":"ৰোগী-নিৰ্দিষ্ট অৱস্থা চলক","These variables form the current demonstration state of the digital twin.":"এই চলকসমূহে ডিজিটেল টুইনৰ বৰ্তমান ডেম’ অৱস্থা গঠন কৰে।","Knee Sound + Vibration Signature":"আঁঠুৰ শব্দ + কম্পন চিগনেচাৰ","Digital Twin Timeline":"ডিজিটেল টুইন সময়ৰেখা","Baseline Assessment":"বেচলাইন মূল্যায়ন","Initial patient movement and joint-signal profile recorded.":"প্ৰাৰম্ভিক ৰোগীৰ চলাচল আৰু জইণ্ট-চিগনেল প্ৰ’ফাইল ৰেকৰ্ড কৰা হৈছে।","Follow-up Assessment":"ফ’ল’-আপ মূল্যায়ন","Longitudinal measurements added to patient profile.":"দীৰ্ঘম্যাদী মাপ ৰোগীৰ প্ৰ’ফাইলত যোগ কৰা হৈছে।","Movement Assessment":"চলাচল মূল্যায়ন","Updated gait and knee movement characteristics.":"আপডেট কৰা গেইট আৰু আঁঠুৰ চলাচলৰ বৈশিষ্ট্য।","Current Assessment":"বৰ্তমান মূল্যায়ন","Latest multimodal screening profile generated.":"শেহতীয়া মাল্টিম’ডেল স্ক্ৰিনিং প্ৰ’ফাইল সৃষ্টি কৰা হৈছে।","Why a Digital Twin?":"ডিজিটেল টুইন কিয়?","Longitudinal":"দীৰ্ঘম্যাদী","Compare future measurements against the patient's own baseline.":"ভৱিষ্যতৰ মাপসমূহ ৰোগীৰ নিজৰ বেচলাইনৰ সৈতে তুলনা কৰক।","Multimodal":"মাল্টিম’ডেল","Combine sound, movement and symptom information.":"শব্দ, চলাচল আৰু লক্ষণৰ তথ্য একত্ৰ কৰক।","Personalized":"ব্যক্তিগতকৃত","Represent patient-specific characteristics rather than relying only on population averages.":"কেৱল জনসংখ্যাৰ গড়ৰ ওপৰত নিৰ্ভৰ নকৰি ৰোগী-নিৰ্দিষ্ট বৈশিষ্ট্য প্ৰতিনিধিত্ব কৰক।","Patient History":"ৰোগীৰ ইতিহাস","Longitudinal screening records and personalized baseline tracking":"দীৰ্ঘম্যাদী স্ক্ৰিনিং ৰেকৰ্ড আৰু ব্যক্তিগতকৃত বেচলাইন ট্ৰেকিং","PATIENT RECORD":"ৰোগীৰ ৰেকৰ্ড","Previous Assessments":"পূৰ্বৰ মূল্যায়ন","Longitudinal Trends":"দীৰ্ঘম্যাদী প্ৰৱণতা","Personalized Baseline":"ব্যক্তিগতকৃত বেচলাইন","Screening Interpretation":"স্ক্ৰিনিং ব্যাখ্যা","Longitudinal monitoring":"দীৰ্ঘম্যাদী নিৰীক্ষণ","PERSONALIZED MONITORING":"ব্যক্তিগতকৃত নিৰীক্ষণ","BASELINE ROM":"বেচলাইন গতি পৰিসৰ","CURRENT ROM":"বৰ্তমান গতি পৰিসৰ","BASELINE EVENTS":"বেচলাইন ঘটনা","CURRENT EVENTS":"বৰ্তমান ঘটনা","AI Engine — Ready":"AI ইঞ্জিন — সাজু","Joint Signal Sensor — Connected":"জইণ্ট চিগনেল চেন্সৰ — সংযুক্ত","IMU Module — Connected":"IMU মডিউল — সংযুক্ত","Local Database — Ready":"স্থানীয় ডাটাবেছ — সাজু","NER / Rural Healthcare":"NER / গ্ৰাম্য স্বাস্থ্যসেৱা","Offline-ready architecture":"অফলাইন-প্ৰস্তুত স্থাপত্য","Secure patient records":"সুৰক্ষিত ৰোগী ৰেকৰ্ড","ArthroSonic Prototype • SIH 2026":"ArthroSonic প্ৰ’টোটাইপ • SIH 2026"},
"bn": {
"AI-Assisted Osteoarthritis Screening":"AI-সহায়িত অস্টিওআর্থ্রাইটিস স্ক্রিনিং","Portable multimodal assessment platform for early OA risk identification":"প্রাথমিক OA ঝুঁকি শনাক্তকরণের জন্য পোর্টেবল মাল্টিমোডাল মূল্যায়ন প্ল্যাটফর্ম","ARTHROSONIC • FIELD SCREENING PLATFORM":"ARTHROSONIC • ফিল্ড স্ক্রিনিং প্ল্যাটফর্ম","Turning joint signals into":"জয়েন্টের সংকেতকে রূপান্তর করা","actionable risk markers.":"কার্যকর ঝুঁকি সূচকে।","ArthroSonic combines joint sound emissions, movement analysis, patient-reported symptoms and longitudinal data to support preliminary osteoarthritis risk screening in low-resource healthcare environments.":"ArthroSonic জয়েন্টের শব্দ নির্গমন, নড়াচড়া বিশ্লেষণ, রোগীর জানানো উপসর্গ এবং দীর্ঘমেয়াদি ডেটা একত্র করে সীমিত সম্পদের স্বাস্থ্যসেবা পরিবেশে প্রাথমিক অস্টিওআর্থ্রাইটিস ঝুঁকি স্ক্রিনিংয়ে সহায়তা করে।","Live System Overview":"লাইভ সিস্টেম ওভারভিউ","Multimodal Patient Profile":"মাল্টিমোডাল রোগী প্রোফাইল","Screening Workflow":"স্ক্রিনিং কর্মপ্রবাহ","ACTIVE PATIENT":"সক্রিয় রোগী","Assessment ready":"মূল্যায়ন প্রস্তুত","SENSOR STATUS":"সেন্সর অবস্থা","SIGNAL QUALITY":"সিগন্যালের গুণমান","Suitable for analysis":"বিশ্লেষণের জন্য উপযুক্ত","ASSESSMENT MODE":"মূল্যায়ন মোড","MULTIMODAL":"মাল্টিমোডাল","CURRENT SCREENING":"বর্তমান স্ক্রিনিং","OA-associated risk markers":"OA-সম্পর্কিত ঝুঁকি সূচক","DEMO OUTPUT":"ডেমো আউটপুট","MODERATE":"মাঝারি","Prototype multimodal analysis indicates a moderate level of OA-associated markers.":"প্রোটোটাইপ মাল্টিমোডাল বিশ্লেষণ OA-সম্পর্কিত সূচকের মাঝারি স্তর দেখায়।","OA HUMAN DIGITAL TWIN":"OA হিউম্যান ডিজিটাল টুইন","Patient Movement State":"রোগীর নড়াচড়ার অবস্থা","Longitudinal representation of movement, sound-pattern and symptom characteristics.":"নড়াচড়া, শব্দ-প্যাটার্ন এবং উপসর্গের বৈশিষ্ট্যের দীর্ঘমেয়াদি উপস্থাপন।","Knee ROM":"হাঁটুর গতি পরিসর","Symmetry":"সমতা","Gait m/s":"গেইট মি/সে","Patient Profile":"রোগী প্রোফাইল","Symptoms + history":"উপসর্গ + ইতিহাস","Sensor Capture":"সেন্সর ক্যাপচার","Joint sound + movement":"জয়েন্টের শব্দ + নড়াচড়া","AI Fusion":"AI ফিউশন","Feature extraction":"ফিচার নিষ্কাশন","Risk Report":"ঝুঁকি রিপোর্ট","Personalized output":"ব্যক্তিগতকৃত আউটপুট","Create or reconnect a patient record before assessment":"মূল্যায়নের আগে রোগীর রেকর্ড তৈরি বা পুনরায় সংযোগ করুন","1. Patient Information":"1. রোগীর তথ্য","2. Connect Patient Record":"2. রোগীর রেকর্ড সংযোগ করুন","✓ Patient record confirmed":"✓ রোগীর রেকর্ড নিশ্চিত হয়েছে","Current screening can now be linked with the patient's longitudinal record.":"বর্তমান স্ক্রিনিং এখন রোগীর দীর্ঘমেয়াদি রেকর্ডের সঙ্গে যুক্ত করা যাবে।","3. Latest Reports & Medical Documents":"3. সর্বশেষ রিপোর্ট ও চিকিৎসা নথি","4. OA Risk Factors & Symptoms":"4. OA ঝুঁকির কারণ ও উপসর্গ","Attached for this assessment:":"এই মূল্যায়নের জন্য সংযুক্ত:","🦵 KNEE-ONLY SCREENING":"🦵 শুধু হাঁটুর স্ক্রিনিং","The screening site is fixed and cannot be changed.":"স্ক্রিনিং স্থান নির্দিষ্ট এবং পরিবর্তন করা যাবে না।","Sensor Assessment":"সেন্সর মূল্যায়ন","Guided acquisition of joint sound and movement signals":"জয়েন্টের শব্দ ও নড়াচড়ার সংকেতের নির্দেশিত সংগ্রহ","🦵 SCREENING SITE: KNEE ONLY":"🦵 স্ক্রিনিং স্থান: শুধু হাঁটু","ArthroSonic is configured specifically for knee assessment. The screening joint is fixed and cannot be changed.":"ArthroSonic বিশেষভাবে হাঁটুর মূল্যায়নের জন্য কনফিগার করা হয়েছে। স্ক্রিনিং জয়েন্ট নির্দিষ্ট এবং পরিবর্তন করা যাবে না।","Sensor Network":"সেন্সর নেটওয়ার্ক","Knee vibration + joint sound":"হাঁটুর কম্পন + জয়েন্টের শব্দ","Movement + posture + gait":"নড়াচড়া + ভঙ্গি + গেইট","Gait assessment":"গেইট মূল্যায়ন","Excellent acquisition":"চমৎকার সংগ্রহ","Guided Assessment Protocol":"নির্দেশিত মূল্যায়ন প্রোটোকল","01 · Joint Signal":"01 · জয়েন্ট সংকেত","Place the PZT and microphone module over the knee joint and perform controlled flexion-extension movements.":"PZT ও মাইক্রোফোন মডিউল হাঁটুর জয়েন্টের উপর রাখুন এবং নিয়ন্ত্রিত ফ্লেক্সন-এক্সটেনশন নড়াচড়া করুন।","02 · Movement":"02 · নড়াচড়া","Capture knee movement, gait, range of motion and left-right movement symmetry.":"হাঁটুর নড়াচড়া, গেইট, গতি পরিসর এবং বাম-ডান নড়াচড়ার সমতা রেকর্ড করুন।","03 · Symptoms":"03 · উপসর্গ","Combine patient-reported pain, stiffness, mobility and relevant risk factors.":"রোগীর জানানো ব্যথা, জড়তা, চলাচল এবং প্রাসঙ্গিক ঝুঁকির কারণ একত্র করুন।","Joint Signal Acquisition":"জয়েন্ট সংকেত সংগ্রহ","READY":"প্রস্তুত","Acquisition Complete":"সংগ্রহ সম্পূর্ণ","Signal quality is suitable for feature extraction and prototype AI analysis.":"সিগন্যালের গুণমান ফিচার নিষ্কাশন ও প্রোটোটাইপ AI বিশ্লেষণের জন্য উপযুক্ত।","Live Joint Signal":"লাইভ জয়েন্ট সংকেত","Time-Frequency Analysis":"সময়-ফ্রিকোয়েন্সি বিশ্লেষণ","DURATION":"সময়কাল","Recording":"রেকর্ডিং","EVENTS":"ঘটনা","Detected sound events":"শনাক্ত শব্দের ঘটনা","SAMPLING":"স্যাম্পলিং","Acquisition rate":"সংগ্রহের হার","QUALITY":"গুণমান","Signal quality index":"সিগন্যাল গুণমান সূচক","AI Risk Analysis":"AI ঝুঁকি বিশ্লেষণ","Screening grade, risk markers and supporting assessment findings":"স্ক্রিনিং গ্রেড, ঝুঁকি সূচক এবং সহায়ক মূল্যায়ন ফলাফল","PROTOTYPE / SIMULATED AI OUTPUT":"প্রোটোটাইপ / সিমুলেটেড AI আউটপুট","This page presents a preliminary screening interpretation for demonstration. It does not establish a medical diagnosis.":"এই পৃষ্ঠা প্রদর্শনের জন্য প্রাথমিক স্ক্রিনিং ব্যাখ্যা দেখায়। এটি চিকিৎসাগত রোগনির্ণয় স্থাপন করে না।","Screening Grade":"স্ক্রিনিং গ্রেড","OA-ASSOCIATED RISK SCORE":"OA-সম্পর্কিত ঝুঁকি স্কোর","Prototype screening index":"প্রোটোটাইপ স্ক্রিনিং সূচক","DATA QUALITY":"ডেটার গুণমান","Good input quality; not OA probability":"ইনপুটের গুণমান ভালো; এটি OA-এর সম্ভাবনা নয়","What Do the Grades Mean?":"গ্রেডের অর্থ কী?","What Did the System Find?":"সিস্টেম কী পেয়েছে?","SCREENING DETAIL":"স্ক্রিনিং বিবরণ","RESULT":"ফলাফল","WHAT IT MEANS":"এর অর্থ","Movement & Patient-Reported Findings":"নড়াচড়া ও রোগীর জানানো ফলাফল","KNEE ROM":"হাঁটুর গতি পরিসর","GAIT SYMMETRY":"গেইট সমতা","Left-right symmetry":"বাম-ডান সমতা","PAIN":"ব্যথা","Patient reported":"রোগীর জানানো","STIFFNESS":"জড়তা","Joint Signal Analysis":"জয়েন্ট সংকেত বিশ্লেষণ","Explainable Screening Factors":"ব্যাখ্যাযোগ্য স্ক্রিনিং কারণ","Sound + vibration events":"শব্দ + কম্পন ঘটনা","17 patterns detected during the prototype movement sequence.":"প্রোটোটাইপ নড়াচড়ার ক্রমে 17টি প্যাটার্ন শনাক্ত হয়েছে।","Movement symmetry":"নড়াচড়ার সমতা","Mild left-right movement asymmetry is present in the demonstration profile.":"ডেমো প্রোফাইলে হালকা বাম-ডান নড়াচড়ার অসমতা রয়েছে।","Range of motion":"গতি পরিসর","The recorded knee range of motion is 108° in the demonstration profile.":"ডেমো প্রোফাইলে রেকর্ড করা হাঁটুর গতি পরিসর 108°।","Reported symptoms":"জানানো উপসর্গ","Pain and stiffness inputs contribute to the multimodal screening profile.":"ব্যথা ও জড়তার ইনপুট মাল্টিমোডাল স্ক্রিনিং প্রোফাইলে অবদান রাখে।","Longitudinal Risk Monitoring":"দীর্ঘমেয়াদি ঝুঁকি পর্যবেক্ষণ","What Does This Mean for You?":"আপনার জন্য এর অর্থ কী?","Predictive screening only. This system does not diagnose OA or prescribe treatment.":"শুধু পূর্বাভাসমূলক স্ক্রিনিং। এই সিস্টেম OA নির্ণয় বা চিকিৎসা নির্ধারণ করে না।","OA Human Digital Twin":"OA হিউম্যান ডিজিটাল টুইন","Longitudinal digital representation of patient-specific OA-related characteristics":"রোগী-নির্দিষ্ট OA-সম্পর্কিত বৈশিষ্ট্যের দীর্ঘমেয়াদি ডিজিটাল উপস্থাপন","PATIENT DIGITAL REPRESENTATION":"রোগীর ডিজিটাল উপস্থাপন","From one-time screening to longitudinal monitoring.":"একবারের স্ক্রিনিং থেকে দীর্ঘমেয়াদি পর্যবেক্ষণ পর্যন্ত।","The ArthroSonic Digital Twin organizes sound, movement, symptom and contextual measurements into a patient-specific longitudinal profile.":"ArthroSonic ডিজিটাল টুইন শব্দ, নড়াচড়া, উপসর্গ ও প্রাসঙ্গিক মাপকে রোগী-নির্দিষ্ট দীর্ঘমেয়াদি প্রোফাইলে সংগঠিত করে।","Patient Twin State":"রোগী টুইন অবস্থা","DIGITAL PATIENT MODEL":"ডিজিটাল রোগী মডেল","Right Knee Profile":"ডান হাঁটুর প্রোফাইল","MODERATE MARKER STATE":"মাঝারি সূচক অবস্থা","Patient-Specific State Variables":"রোগী-নির্দিষ্ট অবস্থা চলক","These variables form the current demonstration state of the digital twin.":"এই চলকগুলি ডিজিটাল টুইনের বর্তমান ডেমো অবস্থা গঠন করে।","Knee Sound + Vibration Signature":"হাঁটুর শব্দ + কম্পন সিগনেচার","Digital Twin Timeline":"ডিজিটাল টুইন টাইমলাইন","Baseline Assessment":"বেসলাইন মূল্যায়ন","Initial patient movement and joint-signal profile recorded.":"প্রাথমিক রোগীর নড়াচড়া ও জয়েন্ট-সিগন্যাল প্রোফাইল রেকর্ড করা হয়েছে।","Follow-up Assessment":"ফলো-আপ মূল্যায়ন","Longitudinal measurements added to patient profile.":"দীর্ঘমেয়াদি মাপ রোগী প্রোফাইলে যোগ করা হয়েছে।","Movement Assessment":"নড়াচড়া মূল্যায়ন","Updated gait and knee movement characteristics.":"আপডেট করা গেইট ও হাঁটুর নড়াচড়ার বৈশিষ্ট্য।","Current Assessment":"বর্তমান মূল্যায়ন","Latest multimodal screening profile generated.":"সর্বশেষ মাল্টিমোডাল স্ক্রিনিং প্রোফাইল তৈরি হয়েছে।","Why a Digital Twin?":"ডিজিটাল টুইন কেন?","Longitudinal":"দীর্ঘমেয়াদি","Compare future measurements against the patient's own baseline.":"ভবিষ্যতের মাপ রোগীর নিজের বেসলাইনের সঙ্গে তুলনা করুন।","Multimodal":"মাল্টিমোডাল","Combine sound, movement and symptom information.":"শব্দ, নড়াচড়া ও উপসর্গের তথ্য একত্র করুন।","Personalized":"ব্যক্তিগতকৃত","Represent patient-specific characteristics rather than relying only on population averages.":"শুধু জনসংখ্যার গড়ের উপর নির্ভর না করে রোগী-নির্দিষ্ট বৈশিষ্ট্য উপস্থাপন করুন।","Patient History":"রোগীর ইতিহাস","Longitudinal screening records and personalized baseline tracking":"দীর্ঘমেয়াদি স্ক্রিনিং রেকর্ড ও ব্যক্তিগতকৃত বেসলাইন ট্র্যাকিং","PATIENT RECORD":"রোগীর রেকর্ড","Previous Assessments":"পূর্ববর্তী মূল্যায়ন","Longitudinal Trends":"দীর্ঘমেয়াদি প্রবণতা","Personalized Baseline":"ব্যক্তিগতকৃত বেসলাইন","Screening Interpretation":"স্ক্রিনিং ব্যাখ্যা","Longitudinal monitoring":"দীর্ঘমেয়াদি পর্যবেক্ষণ","PERSONALIZED MONITORING":"ব্যক্তিগতকৃত পর্যবেক্ষণ","BASELINE ROM":"বেসলাইন গতি পরিসর","CURRENT ROM":"বর্তমান গতি পরিসর","BASELINE EVENTS":"বেসলাইন ঘটনা","CURRENT EVENTS":"বর্তমান ঘটনা","AI Engine — Ready":"AI ইঞ্জিন — প্রস্তুত","Joint Signal Sensor — Connected":"জয়েন্ট সিগন্যাল সেন্সর — সংযুক্ত","IMU Module — Connected":"IMU মডিউল — সংযুক্ত","Local Database — Ready":"স্থানীয় ডেটাবেস — প্রস্তুত","NER / Rural Healthcare":"NER / গ্রামীণ স্বাস্থ্যসেবা","Offline-ready architecture":"অফলাইন-প্রস্তুত আর্কিটেকচার","Secure patient records":"সুরক্ষিত রোগীর রেকর্ড","ArthroSonic Prototype • SIH 2026":"ArthroSonic প্রোটোটাইপ • SIH 2026"},
"ne": {
"AI-Assisted Osteoarthritis Screening":"AI-सहायित ओस्टियोआर्थराइटिस स्क्रिनिङ","Portable multimodal assessment platform for early OA risk identification":"प्रारम्भिक OA जोखिम पहिचानका लागि पोर्टेबल मल्टिमोडल मूल्याङ्कन प्लेटफर्म","ARTHROSONIC • FIELD SCREENING PLATFORM":"ARTHROSONIC • फिल्ड स्क्रिनिङ प्लेटफर्म","Turning joint signals into":"जोइन्टका सङ्केतलाई रूपान्तरण गर्दै","actionable risk markers.":"कार्यान्वयनयोग्य जोखिम सूचकमा।","ArthroSonic combines joint sound emissions, movement analysis, patient-reported symptoms and longitudinal data to support preliminary osteoarthritis risk screening in low-resource healthcare environments.":"ArthroSonic ले जोइन्टको ध्वनि उत्सर्जन, चाल विश्लेषण, बिरामीले बताएका लक्षण र दीर्घकालीन डेटा संयोजन गरी सीमित स्रोत भएका स्वास्थ्य सेवामा प्रारम्भिक ओस्टियोआर्थराइटिस जोखिम स्क्रिनिङमा सहयोग गर्छ।","Live System Overview":"लाइभ प्रणाली अवलोकन","Multimodal Patient Profile":"मल्टिमोडल बिरामी प्रोफाइल","Screening Workflow":"स्क्रिनिङ कार्यप्रवाह","ACTIVE PATIENT":"सक्रिय बिरामी","Assessment ready":"मूल्याङ्कन तयार","SENSOR STATUS":"सेन्सर स्थिति","SIGNAL QUALITY":"सिग्नल गुणस्तर","Suitable for analysis":"विश्लेषणका लागि उपयुक्त","ASSESSMENT MODE":"मूल्याङ्कन मोड","MULTIMODAL":"मल्टिमोडल","CURRENT SCREENING":"हालको स्क्रिनिङ","OA-associated risk markers":"OA-सम्बन्धित जोखिम सूचक","DEMO OUTPUT":"डेमो आउटपुट","MODERATE":"मध्यम","Prototype multimodal analysis indicates a moderate level of OA-associated markers.":"प्रोटोटाइप मल्टिमोडल विश्लेषणले OA-सम्बन्धित सूचकहरूको मध्यम स्तर देखाउँछ।","OA HUMAN DIGITAL TWIN":"OA ह्युमन डिजिटल ट्विन","Patient Movement State":"बिरामीको चाल अवस्था","Longitudinal representation of movement, sound-pattern and symptom characteristics.":"चाल, ध्वनि-प्याटर्न र लक्षणका विशेषताहरूको दीर्घकालीन प्रतिनिधित्व।","Knee ROM":"घुँडाको गति दायरा","Symmetry":"सममिति","Gait m/s":"चाल मि/से","Patient Profile":"बिरामी प्रोफाइल","Symptoms + history":"लक्षण + इतिहास","Sensor Capture":"सेन्सर क्याप्चर","Joint sound + movement":"जोइन्टको ध्वनि + चाल","AI Fusion":"AI फ्युजन","Feature extraction":"फिचर निष्कर्षण","Risk Report":"जोखिम रिपोर्ट","Personalized output":"व्यक्तिगत आउटपुट","Create or reconnect a patient record before assessment":"मूल्याङ्कन अघि बिरामीको रेकर्ड बनाउनुहोस् वा पुनः जडान गर्नुहोस्","1. Patient Information":"1. बिरामी जानकारी","2. Connect Patient Record":"2. बिरामी रेकर्ड जडान गर्नुहोस्","✓ Patient record confirmed":"✓ बिरामी रेकर्ड पुष्टि भयो","Current screening can now be linked with the patient's longitudinal record.":"हालको स्क्रिनिङ अब बिरामीको दीर्घकालीन रेकर्डसँग जोड्न सकिन्छ।","3. Latest Reports & Medical Documents":"3. नवीनतम रिपोर्ट र चिकित्सकीय कागजात","4. OA Risk Factors & Symptoms":"4. OA जोखिम कारक र लक्षण","Attached for this assessment:":"यस मूल्याङ्कनका लागि संलग्न:","🦵 KNEE-ONLY SCREENING":"🦵 घुँडा मात्र स्क्रिनिङ","The screening site is fixed and cannot be changed.":"स्क्रिनिङ स्थान निश्चित छ र परिवर्तन गर्न सकिँदैन।","Sensor Assessment":"सेन्सर मूल्याङ्कन","Guided acquisition of joint sound and movement signals":"जोइन्ट ध्वनि र चाल सङ्केतको निर्देशित सङ्कलन","🦵 SCREENING SITE: KNEE ONLY":"🦵 स्क्रिनिङ स्थान: घुँडा मात्र","ArthroSonic is configured specifically for knee assessment. The screening joint is fixed and cannot be changed.":"ArthroSonic विशेष रूपमा घुँडा मूल्याङ्कनका लागि कन्फिगर गरिएको छ। स्क्रिनिङ जोइन्ट निश्चित छ र परिवर्तन गर्न सकिँदैन।","Sensor Network":"सेन्सर नेटवर्क","Knee vibration + joint sound":"घुँडाको कम्पन + जोइन्ट ध्वनि","Movement + posture + gait":"चाल + आसन + गेट","Gait assessment":"चाल मूल्याङ्कन","Excellent acquisition":"उत्कृष्ट सङ्कलन","Guided Assessment Protocol":"निर्देशित मूल्याङ्कन प्रोटोकल","01 · Joint Signal":"01 · जोइन्ट सङ्केत","Place the PZT and microphone module over the knee joint and perform controlled flexion-extension movements.":"PZT र माइक्रोफोन मोड्युल घुँडाको जोइन्टमाथि राखेर नियन्त्रित फ्लेक्सन-एक्सटेन्सन चाल गर्नुहोस्।","02 · Movement":"02 · चाल","Capture knee movement, gait, range of motion and left-right movement symmetry.":"घुँडाको चाल, गेट, गति दायरा र बायाँ-दायाँ चालको सममिति रेकर्ड गर्नुहोस्।","03 · Symptoms":"03 · लक्षण","Combine patient-reported pain, stiffness, mobility and relevant risk factors.":"बिरामीले बताएका दुखाइ, कडापन, गतिशीलता र सम्बन्धित जोखिम कारक संयोजन गर्नुहोस्।","Joint Signal Acquisition":"जोइन्ट सङ्केत सङ्कलन","READY":"तयार","Acquisition Complete":"सङ्कलन पूरा भयो","Signal quality is suitable for feature extraction and prototype AI analysis.":"सिग्नल गुणस्तर फिचर निष्कर्षण र प्रोटोटाइप AI विश्लेषणका लागि उपयुक्त छ।","Live Joint Signal":"लाइभ जोइन्ट सङ्केत","Time-Frequency Analysis":"समय-आवृत्ति विश्लेषण","DURATION":"अवधि","Recording":"रेकर्डिङ","EVENTS":"घटनाहरू","Detected sound events":"पत्ता लागेका ध्वनि घटनाहरू","SAMPLING":"स्याम्पलिङ","Acquisition rate":"सङ्कलन दर","QUALITY":"गुणस्तर","Signal quality index":"सिग्नल गुणस्तर सूचक","AI Risk Analysis":"AI जोखिम विश्लेषण","Screening grade, risk markers and supporting assessment findings":"स्क्रिनिङ ग्रेड, जोखिम सूचक र सहायक मूल्याङ्कन निष्कर्ष","PROTOTYPE / SIMULATED AI OUTPUT":"प्रोटोटाइप / सिमुलेटेड AI आउटपुट","This page presents a preliminary screening interpretation for demonstration. It does not establish a medical diagnosis.":"यो पृष्ठले प्रदर्शनका लागि प्रारम्भिक स्क्रिनिङ व्याख्या प्रस्तुत गर्छ। यसले चिकित्सकीय निदान स्थापित गर्दैन।","Screening Grade":"स्क्रिनिङ ग्रेड","OA-ASSOCIATED RISK SCORE":"OA-सम्बन्धित जोखिम स्कोर","Prototype screening index":"प्रोटोटाइप स्क्रिनिङ सूचक","DATA QUALITY":"डेटा गुणस्तर","Good input quality; not OA probability":"इनपुट गुणस्तर राम्रो छ; यो OA को सम्भावना होइन","What Do the Grades Mean?":"ग्रेडको अर्थ के हो?","What Did the System Find?":"प्रणालीले के पत्ता लगायो?","SCREENING DETAIL":"स्क्रिनिङ विवरण","RESULT":"नतिजा","WHAT IT MEANS":"यसको अर्थ","Movement & Patient-Reported Findings":"चाल र बिरामीले बताएका निष्कर्ष","KNEE ROM":"घुँडाको गति दायरा","GAIT SYMMETRY":"चाल सममिति","Left-right symmetry":"बायाँ-दायाँ सममिति","PAIN":"दुखाइ","Patient reported":"बिरामीले बताएका","STIFFNESS":"कडापन","Joint Signal Analysis":"जोइन्ट सङ्केत विश्लेषण","Explainable Screening Factors":"व्याख्यायोग्य स्क्रिनिङ कारक","Sound + vibration events":"ध्वनि + कम्पन घटनाहरू","17 patterns detected during the prototype movement sequence.":"प्रोटोटाइप चाल क्रमका क्रममा 17 वटा प्याटर्न पत्ता लागे।","Movement symmetry":"चाल सममिति","Mild left-right movement asymmetry is present in the demonstration profile.":"डेमो प्रोफाइलमा हल्का बायाँ-दायाँ चाल असममिति देखिन्छ।","Range of motion":"गति दायरा","The recorded knee range of motion is 108° in the demonstration profile.":"डेमो प्रोफाइलमा रेकर्ड गरिएको घुँडाको गति दायरा 108° छ।","Reported symptoms":"बताइएका लक्षण","Pain and stiffness inputs contribute to the multimodal screening profile.":"दुखाइ र कडापनका इनपुटले मल्टिमोडल स्क्रिनिङ प्रोफाइलमा योगदान गर्छन्।","Longitudinal Risk Monitoring":"दीर्घकालीन जोखिम निगरानी","What Does This Mean for You?":"तपाईंका लागि यसको अर्थ के हो?","Predictive screening only. This system does not diagnose OA or prescribe treatment.":"पूर्वानुमानात्मक स्क्रिनिङ मात्र। यो प्रणालीले OA निदान वा उपचार निर्धारण गर्दैन।","OA Human Digital Twin":"OA ह्युमन डिजिटल ट्विन","Longitudinal digital representation of patient-specific OA-related characteristics":"बिरामी-विशिष्ट OA-सम्बन्धित विशेषताहरूको दीर्घकालीन डिजिटल प्रतिनिधित्व","PATIENT DIGITAL REPRESENTATION":"बिरामीको डिजिटल प्रतिनिधित्व","From one-time screening to longitudinal monitoring.":"एकपटकको स्क्रिनिङबाट दीर्घकालीन निगरानीसम्म।","The ArthroSonic Digital Twin organizes sound, movement, symptom and contextual measurements into a patient-specific longitudinal profile.":"ArthroSonic डिजिटल ट्विनले ध्वनि, चाल, लक्षण र सन्दर्भगत मापनलाई बिरामी-विशिष्ट दीर्घकालीन प्रोफाइलमा व्यवस्थित गर्छ।","Patient Twin State":"बिरामी ट्विन अवस्था","DIGITAL PATIENT MODEL":"डिजिटल बिरामी मोडेल","Right Knee Profile":"दायाँ घुँडा प्रोफाइल","MODERATE MARKER STATE":"मध्यम सूचक अवस्था","Patient-Specific State Variables":"बिरामी-विशिष्ट अवस्था चरहरू","These variables form the current demonstration state of the digital twin.":"यी चरहरूले डिजिटल ट्विनको हालको डेमो अवस्था बनाउँछन्।","Knee Sound + Vibration Signature":"घुँडाको ध्वनि + कम्पन सिग्नेचर","Digital Twin Timeline":"डिजिटल ट्विन समयरेखा","Baseline Assessment":"बेसलाइन मूल्याङ्कन","Initial patient movement and joint-signal profile recorded.":"प्रारम्भिक बिरामी चाल र जोइन्ट-सिग्नल प्रोफाइल रेकर्ड गरियो।","Follow-up Assessment":"फलो-अप मूल्याङ्कन","Longitudinal measurements added to patient profile.":"दीर्घकालीन मापन बिरामी प्रोफाइलमा थपियो।","Movement Assessment":"चाल मूल्याङ्कन","Updated gait and knee movement characteristics.":"अपडेट गरिएको चाल र घुँडा चालका विशेषताहरू।","Current Assessment":"हालको मूल्याङ्कन","Latest multimodal screening profile generated.":"नवीनतम मल्टिमोडल स्क्रिनिङ प्रोफाइल तयार गरियो।","Why a Digital Twin?":"डिजिटल ट्विन किन?","Longitudinal":"दीर्घकालीन","Compare future measurements against the patient's own baseline.":"भविष्यका मापनलाई बिरामीको आफ्नै बेसलाइनसँग तुलना गर्नुहोस्।","Multimodal":"मल्टिमोडल","Combine sound, movement and symptom information.":"ध्वनि, चाल र लक्षणको जानकारी संयोजन गर्नुहोस्।","Personalized":"व्यक्तिगतकृत","Represent patient-specific characteristics rather than relying only on population averages.":"जनसङ्ख्याको औसतमा मात्र निर्भर नगरी बिरामी-विशिष्ट विशेषताहरू प्रतिनिधित्व गर्नुहोस्।","Patient History":"बिरामी इतिहास","Longitudinal screening records and personalized baseline tracking":"दीर्घकालीन स्क्रिनिङ रेकर्ड र व्यक्तिगत बेसलाइन ट्र्याकिङ","PATIENT RECORD":"बिरामी रेकर्ड","Previous Assessments":"अघिल्ला मूल्याङ्कनहरू","Longitudinal Trends":"दीर्घकालीन प्रवृत्तिहरू","Personalized Baseline":"व्यक्तिगत बेसलाइन","Screening Interpretation":"स्क्रिनिङ व्याख्या","Longitudinal monitoring":"दीर्घकालीन निगरानी","PERSONALIZED MONITORING":"व्यक्तिगत निगरानी","BASELINE ROM":"बेसलाइन गति दायरा","CURRENT ROM":"हालको गति दायरा","BASELINE EVENTS":"बेसलाइन घटनाहरू","CURRENT EVENTS":"हालका घटनाहरू","AI Engine — Ready":"AI इन्जिन — तयार","Joint Signal Sensor — Connected":"जोइन्ट सिग्नल सेन्सर — जडान भएको","IMU Module — Connected":"IMU मोड्युल — जडान भएको","Local Database — Ready":"स्थानीय डेटाबेस — तयार","NER / Rural Healthcare":"NER / ग्रामीण स्वास्थ्य सेवा","Offline-ready architecture":"अफलाइन-तयार आर्किटेक्चर","Secure patient records":"सुरक्षित बिरामी रेकर्ड","ArthroSonic Prototype • SIH 2026":"ArthroSonic प्रोटोटाइप • SIH 2026"}
}
for _lang, _pack in EXTRA_UI_TRANSLATIONS.items():
    TRANSLATIONS.setdefault(_lang, {}).update(_pack)

# Dataframe-specific labels. Keep Risk Markers and Risk Index distinct; otherwise
# localized tables can contain duplicate column names and PyArrow will reject them.
_HISTORY_COLUMN_TRANSLATIONS = {
    "hi": {"Date":"तिथि", "Risk Markers":"जोखिम संकेतक", "Risk Index":"जोखिम सूचकांक", "Pain":"दर्द", "Sound Events":"ध्वनि घटनाएँ", "Knee ROM":"घुटने की गति सीमा"},
    "as": {"Date":"তাৰিখ", "Risk Markers":"ঝুঁকি সূচক", "Risk Index":"ঝুঁকি সূচকাংক", "Pain":"বিষ", "Sound Events":"শব্দৰ ঘটনা", "Knee ROM":"আঁঠুৰ গতি পৰিসৰ"},
    "bn": {"Date":"তারিখ", "Risk Markers":"ঝুঁকি সূচক", "Risk Index":"ঝুঁকি সূচকাঙ্ক", "Pain":"ব্যথা", "Sound Events":"শব্দের ঘটনা", "Knee ROM":"হাঁটুর গতি পরিসর"},
    "ne": {"Date":"मिति", "Risk Markers":"जोखिम सूचक", "Risk Index":"जोखिम सूचकाङ्क", "Pain":"दुखाइ", "Sound Events":"ध्वनि घटनाहरू", "Knee ROM":"घुँडाको गति दायरा"},
}
for _lang, _pack in _HISTORY_COLUMN_TRANSLATIONS.items():
    TRANSLATIONS.setdefault(_lang, {}).update(_pack)

_EXTRA_REMAINING_UI = {
    "hi": {
        "ARTHROSONIC • AI-Assisted OA Risk Screening • SIH 2026":"ARTHROSONIC • AI-सहायित OA जोखिम स्क्रीनिंग • SIH 2026",
        "Prototype for screening research and demonstration.":"स्क्रीनिंग अनुसंधान और प्रदर्शन के लिए प्रोटोटाइप।",
        "Not a medical diagnostic system.":"यह चिकित्सीय निदान प्रणाली नहीं है।",
        "Time (seconds)":"समय (सेकंड)", "Amplitude":"आयाम", "Frequency (Hz)":"आवृत्ति (Hz)",
        "Jan 2026":"जनवरी 2026", "Apr 2026":"अप्रैल 2026", "Jul 2026":"जुलाई 2026", "Sep 2026":"सितंबर 2026",
        "12 Jan 2026":"12 जनवरी 2026", "18 Apr 2026":"18 अप्रैल 2026", "20 Jul 2026":"20 जुलाई 2026", "18 Sep 2026":"18 सितंबर 2026",
        "e.g. +91 98765 43210":"उदा. +91 98765 43210", "House / village / town / district / state":"घर / गाँव / शहर / जिला / राज्य",
        "Prototype only: files are available during the current app session.":"केवल प्रोटोटाइप: फ़ाइलें वर्तमान ऐप सत्र में उपलब्ध हैं।",
        "Risk":"जोखिम", "Risk Index":"जोखिम सूचकांक", "Sound Event Trend":"ध्वनि घटना रुझान", "Prototype Risk Index":"प्रोटोटाइप जोखिम सूचकांक"
    },
    "as": {
        "ARTHROSONIC • AI-Assisted OA Risk Screening • SIH 2026":"ARTHROSONIC • AI-সহায়িত OA ঝুঁকি স্ক্ৰিনিং • SIH 2026",
        "Prototype for screening research and demonstration.":"স্ক্ৰিনিং গৱেষণা আৰু প্ৰদৰ্শনৰ বাবে প্ৰ’টোটাইপ।", "Not a medical diagnostic system.":"ই চিকিৎসাগত নিৰ্ণয় ব্যৱস্থা নহয়।",
        "Time (seconds)":"সময় (ছেকেণ্ড)", "Amplitude":"প্ৰশস্ততা", "Frequency (Hz)":"কম্পনাংক (Hz)",
        "Jan 2026":"জানুৱাৰী 2026", "Apr 2026":"এপ্ৰিল 2026", "Jul 2026":"জুলাই 2026", "Sep 2026":"ছেপ্টেম্বৰ 2026",
        "12 Jan 2026":"12 জানুৱাৰী 2026", "18 Apr 2026":"18 এপ্ৰিল 2026", "20 Jul 2026":"20 জুলাই 2026", "18 Sep 2026":"18 ছেপ্টেম্বৰ 2026",
        "e.g. +91 98765 43210":"উদাহৰণ: +91 98765 43210", "House / village / town / district / state":"ঘৰ / গাঁও / নগৰ / জিলা / ৰাজ্য",
        "Prototype only: files are available during the current app session.":"কেৱল প্ৰ’টোটাইপ: ফাইলসমূহ বৰ্তমান এপ ছেছনত উপলব্ধ।",
        "Risk":"ঝুঁকি", "Risk Index":"ঝুঁকি সূচকাংক", "Sound Event Trend":"শব্দ ঘটনা প্ৰৱণতা", "Prototype Risk Index":"প্ৰ’টোটাইপ ঝুঁকি সূচকাংক"
    },
    "bn": {
        "ARTHROSONIC • AI-Assisted OA Risk Screening • SIH 2026":"ARTHROSONIC • AI-সহায়িত OA ঝুঁকি স্ক্রিনিং • SIH 2026",
        "Prototype for screening research and demonstration.":"স্ক্রিনিং গবেষণা ও প্রদর্শনের জন্য প্রোটোটাইপ।", "Not a medical diagnostic system.":"এটি চিকিৎসাগত রোগনির্ণয় ব্যবস্থা নয়।",
        "Time (seconds)":"সময় (সেকেন্ড)", "Amplitude":"অ্যামপ্লিটিউড", "Frequency (Hz)":"ফ্রিকোয়েন্সি (Hz)",
        "Jan 2026":"জানুয়ারি 2026", "Apr 2026":"এপ্রিল 2026", "Jul 2026":"জুলাই 2026", "Sep 2026":"সেপ্টেম্বর 2026",
        "12 Jan 2026":"12 জানুয়ারি 2026", "18 Apr 2026":"18 এপ্রিল 2026", "20 Jul 2026":"20 জুলাই 2026", "18 Sep 2026":"18 সেপ্টেম্বর 2026",
        "e.g. +91 98765 43210":"উদাহরণ: +91 98765 43210", "House / village / town / district / state":"বাড়ি / গ্রাম / শহর / জেলা / রাজ্য",
        "Prototype only: files are available during the current app session.":"শুধু প্রোটোটাইপ: বর্তমান অ্যাপ সেশনে ফাইলগুলি উপলব্ধ।",
        "Risk":"ঝুঁকি", "Risk Index":"ঝুঁকি সূচকাঙ্ক", "Sound Event Trend":"শব্দ ঘটনার প্রবণতা", "Prototype Risk Index":"প্রোটোটাইপ ঝুঁকি সূচকাঙ্ক"
    },
    "ne": {
        "ARTHROSONIC • AI-Assisted OA Risk Screening • SIH 2026":"ARTHROSONIC • AI-सहायित OA जोखिम स्क्रिनिङ • SIH 2026",
        "Prototype for screening research and demonstration.":"स्क्रिनिङ अनुसन्धान र प्रदर्शनका लागि प्रोटोटाइप।", "Not a medical diagnostic system.":"यो चिकित्सकीय निदान प्रणाली होइन।",
        "Time (seconds)":"समय (सेकेन्ड)", "Amplitude":"आयाम", "Frequency (Hz)":"आवृत्ति (Hz)",
        "Jan 2026":"जनवरी 2026", "Apr 2026":"अप्रिल 2026", "Jul 2026":"जुलाई 2026", "Sep 2026":"सेप्टेम्बर 2026",
        "12 Jan 2026":"12 जनवरी 2026", "18 Apr 2026":"18 अप्रिल 2026", "20 Jul 2026":"20 जुलाई 2026", "18 Sep 2026":"18 सेप्टेम्बर 2026",
        "e.g. +91 98765 43210":"उदाहरण: +91 98765 43210", "House / village / town / district / state":"घर / गाउँ / सहर / जिल्ला / राज्य",
        "Prototype only: files are available during the current app session.":"प्रोटोटाइप मात्र: हालको एप सत्रमा फाइलहरू उपलब्ध छन्।",
        "Risk":"जोखिम", "Risk Index":"जोखिम सूचकाङ्क", "Sound Event Trend":"ध्वनि घटना प्रवृत्ति", "Prototype Risk Index":"प्रोटोटाइप जोखिम सूचकाङ्क"
    }
}
for _lang, _pack in _EXTRA_REMAINING_UI.items():
    TRANSLATIONS.setdefault(_lang, {}).update(_pack)


# ============================================================
# COMPLETE EXACT UI PHRASE PACK
# ============================================================
# These are whole-phrase translations, not word-by-word substitutions.
# Existing translation entries remain intact; these fill the remaining
# visible phrases used by the prototype.
_EXTRA_EXACT_UI = {
"hi": {
"READY":"तैयार","Gait m/s":"चाल m/s","Knee ROM":"घुटने की गति सीमा","MODERATE":"मध्यम","Symmetry":"समरूपता","ARTHROSONIC":"ARTHROSONIC","DEMO OUTPUT":"डेमो आउटपुट","02 · Movement":"02 · गति","03 · Symptoms":"03 · लक्षण","Sensor Network":"सेंसर नेटवर्क","Screening Grade":"स्क्रीनिंग ग्रेड","knee joint only":"केवल घुटने का जोड़","01 · Joint Signal":"01 · जोड़ सिग्नल","AI Engine — Ready":"AI इंजन — तैयार","CURRENT SCREENING":"वर्तमान स्क्रीनिंग","Live Joint Signal":"लाइव जोड़ सिग्नल","Patient Twin State":"रोगी ट्विन स्थिति","Right Knee Profile":"दाएँ घुटने की प्रोफ़ाइल","Screening Workflow":"स्क्रीनिंग कार्यप्रवाह","Longitudinal Trends":"दीर्घकालिक रुझान","Why a Digital Twin?":"डिजिटल ट्विन क्यों?","Live System Overview":"लाइव सिस्टम अवलोकन","Previous Assessments":"पिछले मूल्यांकन","DIGITAL PATIENT MODEL":"डिजिटल रोगी मॉडल","Digital Twin Timeline":"डिजिटल ट्विन समयरेखा","Joint Signal Analysis":"जोड़ सिग्नल विश्लेषण","MODERATE MARKER STATE":"मध्यम संकेतक स्थिति","OA HUMAN DIGITAL TWIN":"OA ह्यूमन डिजिटल ट्विन","Personalized Baseline":"व्यक्तिगत बेसलाइन","🦵 KNEE-ONLY SCREENING":"🦵 केवल घुटने की स्क्रीनिंग","1. Patient Information":"1. रोगी की जानकारी","IMU Module — Connected":"IMU मॉड्यूल — कनेक्टेड","Local Database — Ready":"स्थानीय डेटाबेस — तैयार","Patient Movement State":"रोगी की गति स्थिति","✓ Acquisition Complete":"✓ अधिग्रहण पूरा हुआ","Longitudinal monitoring":"दीर्घकालिक निगरानी","PERSONALIZED MONITORING":"व्यक्तिगत निगरानी","Time-Frequency Analysis":"समय-आवृत्ति विश्लेषण","Joint Signal Acquisition":"जोड़ सिग्नल अधिग्रहण","Screening Interpretation":"स्क्रीनिंग व्याख्या","What Do the Grades Mean?":"ग्रेड का क्या अर्थ है?","actionable risk markers.":"कार्रवाई योग्य जोखिम संकेतक।","2. Connect Patient Record":"2. रोगी रिकॉर्ड कनेक्ट करें","What Did the System Find?":"सिस्टम ने क्या पाया?","Guided Assessment Protocol":"निर्देशित मूल्यांकन प्रोटोकॉल","Multimodal Patient Profile":"मल्टीमॉडल रोगी प्रोफ़ाइल","OA-associated risk markers":"OA-संबंधित जोखिम संकेतक","Turning joint signals into":"जोड़ सिग्नलों को बदलना","✓ Patient record confirmed":"✓ रोगी रिकॉर्ड की पुष्टि हो गई","🦵 SCREENING SITE: KNEE ONLY":"🦵 स्क्रीनिंग साइट: केवल घुटना","Longitudinal Risk Monitoring":"दीर्घकालिक जोखिम निगरानी","What Does This Mean for You?":"आपके लिए इसका क्या अर्थ है?","4. OA Risk Factors & Symptoms":"4. OA जोखिम कारक और लक्षण","Explainable Screening Factors":"व्याख्यायोग्य स्क्रीनिंग कारक","PATIENT DIGITAL REPRESENTATION":"रोगी का डिजिटल प्रतिनिधित्व","Joint Signal Sensor — Connected":"जोड़ सिग्नल सेंसर — कनेक्टेड","PROTOTYPE / SIMULATED AI OUTPUT":"प्रोटोटाइप / सिम्युलेटेड AI आउटपुट","Patient-Specific State Variables":"रोगी-विशिष्ट स्थिति चर","Movement & Patient-Reported Findings":"गति और रोगी द्वारा बताए गए निष्कर्ष","3. Latest Reports & Medical Documents":"3. नवीनतम रिपोर्ट और चिकित्सीय दस्तावेज़","ARTHROSONIC • FIELD SCREENING PLATFORM":"ARTHROSONIC • फील्ड स्क्रीनिंग प्लेटफ़ॉर्म","The ArthroSonic prototype measures the":"ArthroSonic प्रोटोटाइप मापता है","• AI-Assisted OA Risk Screening • SIH 2026":"• AI-सहायित OA जोखिम स्क्रीनिंग • SIH 2026","From one-time screening to longitudinal monitoring.":"एक बार की स्क्रीनिंग से दीर्घकालिक निगरानी तक।",". The screening site is fixed and cannot be changed.":"। स्क्रीनिंग साइट निश्चित है और बदली नहीं जा सकती।","These variables form the current demonstration state of the digital twin.":"ये चर डिजिटल ट्विन की वर्तमान डेमो स्थिति बनाते हैं।","Current screening can now be linked with the patient's longitudinal record.":"वर्तमान स्क्रीनिंग को अब रोगी के दीर्घकालिक रिकॉर्ड से जोड़ा जा सकता है।","Signal quality is suitable for feature extraction and prototype AI analysis.":"सिग्नल गुणवत्ता फीचर निष्कर्षण और प्रोटोटाइप AI विश्लेषण के लिए उपयुक्त है।","Combine patient-reported pain, stiffness, mobility and relevant risk factors.":"रोगी द्वारा बताए गए दर्द, जकड़न, गतिशीलता और संबंधित जोखिम कारकों को मिलाएँ।","Capture knee movement, gait, range of motion and left-right movement symmetry.":"घुटने की गति, चाल, गति सीमा और बाएँ-दाएँ गति समरूपता रिकॉर्ड करें।","Prototype multimodal analysis indicates a moderate level of OA-associated markers.":"प्रोटोटाइप मल्टीमॉडल विश्लेषण मध्यम स्तर के OA-संबंधित संकेतक दर्शाता है।","Longitudinal representation of movement, sound-pattern and symptom characteristics.":"गति, ध्वनि-पैटर्न और लक्षण विशेषताओं का दीर्घकालिक प्रतिनिधित्व।","Prototype for screening research and demonstration. Not a medical diagnostic system.":"स्क्रीनिंग अनुसंधान और प्रदर्शन के लिए प्रोटोटाइप। यह चिकित्सीय निदान प्रणाली नहीं है।","Place the PZT and microphone module over the knee joint and perform controlled flexion-extension movements.":"PZT और माइक्रोफ़ोन मॉड्यूल को घुटने के जोड़ पर रखें और नियंत्रित फ्लेक्शन-एक्सटेंशन गति करें।","ArthroSonic is configured specifically for knee assessment. The screening joint is fixed and cannot be changed.":"ArthroSonic विशेष रूप से घुटने के मूल्यांकन के लिए कॉन्फ़िगर किया गया है। स्क्रीनिंग जोड़ निश्चित है और बदला नहीं जा सकता।","This page presents a preliminary screening interpretation for demonstration. It does not establish a medical diagnosis.":"यह पृष्ठ प्रदर्शन के लिए प्रारंभिक स्क्रीनिंग व्याख्या प्रस्तुत करता है। यह चिकित्सीय निदान स्थापित नहीं करता।","ArthroSonic stores repeated screening measurements so that future assessments can be compared with the patient's own historical baseline.":"ArthroSonic दोहराई गई स्क्रीनिंग माप संग्रहीत करता है ताकि भविष्य के मूल्यांकन की तुलना रोगी की अपनी ऐतिहासिक बेसलाइन से की जा सके।","Changes in sound-pattern features, movement characteristics, symptoms and other recorded variables can therefore be visualized over time.":"इससे ध्वनि-पैटर्न विशेषताओं, गति विशेषताओं, लक्षणों और अन्य रिकॉर्ड किए गए चरों में बदलाव समय के साथ देखे जा सकते हैं।","The ArthroSonic Digital Twin organizes sound, movement, symptom and contextual measurements into a patient-specific longitudinal profile.":"ArthroSonic डिजिटल ट्विन ध्वनि, गति, लक्षण और संदर्भात्मक मापों को रोगी-विशिष्ट दीर्घकालिक प्रोफ़ाइल में व्यवस्थित करता है।","ArthroSonic combines joint sound emissions, movement analysis, patient-reported symptoms and longitudinal data to support preliminary osteoarthritis risk screening in low-resource healthcare environments.":"ArthroSonic जोड़ की ध्वनि उत्सर्जन, गति विश्लेषण, रोगी द्वारा बताए गए लक्षण और दीर्घकालिक डेटा को मिलाकर सीमित संसाधनों वाले स्वास्थ्य वातावरण में प्रारंभिक ऑस्टियोआर्थराइटिस जोखिम स्क्रीनिंग में सहायता करता है।",
"No":"नहीं","Low":"कम","Yes":"हाँ","High":"उच्च","Male":"पुरुष","Other":"अन्य","Female":"महिला","Moderate":"मध्यम","Amplitude":"आयाम","Sound Events":"ध्वनि घटनाएँ","Time (seconds)":"समय (सेकंड)","Assessment Date":"मूल्यांकन तिथि","Knee Joint Signal":"घुटने का जोड़ सिग्नल","Sound Event Trend":"ध्वनि घटना रुझान","🌐 Language / भाषा":"🌐 भाषा","Prototype Risk Index":"प्रोटोटाइप जोखिम सूचकांक","e.g. +91 98765 43210":"उदाहरण: +91 98765 43210","RUN MULTIMODAL AI ANALYSIS":"मल्टीमॉडल AI विश्लेषण चलाएँ","Attached for this assessment:":"इस मूल्यांकन के लिए संलग्न:","ArthroSonic Prototype • SIH 2026":"ArthroSonic प्रोटोटाइप • SIH 2026","Prototype multimodal analysis completed.":"प्रोटोटाइप मल्टीमॉडल विश्लेषण पूरा हुआ।","House / village / town / district / state":"घर / गाँव / कस्बा / जिला / राज्य","Joint-signal and movement sequence captured successfully.":"जोड़-सिग्नल और गति अनुक्रम सफलतापूर्वक रिकॉर्ड किया गया।","Prototype only: files are available during the current app session.":"केवल प्रोटोटाइप: फ़ाइलें वर्तमान ऐप सत्र के दौरान उपलब्ध हैं।","Confirm the patient record to unlock document upload and the next step.":"दस्तावेज़ अपलोड और अगले चरण को सक्रिय करने के लिए रोगी रिकॉर्ड की पुष्टि करें।","Predictive screening only. This system does not diagnose OA or prescribe treatment.":"केवल पूर्वानुमानात्मक स्क्रीनिंग। यह सिस्टम OA का निदान या उपचार निर्धारित नहीं करता।","Grades describe screening risk only. They do not confirm OA or show the amount of joint damage. Grade boundaries must be defined and validated for the AI model.":"ग्रेड केवल स्क्रीनिंग जोखिम बताते हैं। वे OA की पुष्टि या जोड़ की क्षति की मात्रा नहीं बताते। ग्रेड सीमाएँ AI मॉडल के लिए परिभाषित और मान्य की जानी चाहिए।",
},
"as": {
"READY":"সাজু","Gait m/s":"গেইট m/s","Knee ROM":"আঁঠুৰ গতি পৰিসৰ","MODERATE":"মধ্যম","Symmetry":"সমমিতি","ARTHROSONIC":"ARTHROSONIC","DEMO OUTPUT":"ডেমো আউটপুট","02 · Movement":"02 · চলাচল","03 · Symptoms":"03 · লক্ষণ","Sensor Network":"চেন্সৰ নেটৱৰ্ক","Screening Grade":"স্ক্ৰিনিং গ্ৰেড","knee joint only":"কেৱল আঁঠুৰ জইণ্ট","01 · Joint Signal":"01 · জইণ্ট চিগনেল","AI Engine — Ready":"AI ইঞ্জিন — সাজু","CURRENT SCREENING":"বৰ্তমান স্ক্ৰিনিং","Live Joint Signal":"লাইভ জইণ্ট চিগনেল","Patient Twin State":"ৰোগীৰ টুইন অৱস্থা","Right Knee Profile":"সোঁ আঁঠুৰ প্ৰ’ফাইল","Screening Workflow":"স্ক্ৰিনিং কাৰ্যপ্ৰবাহ","Longitudinal Trends":"দীৰ্ঘম্যাদী প্ৰৱণতা","Why a Digital Twin?":"ডিজিটেল টুইন কিয়?","Live System Overview":"লাইভ চিষ্টেমৰ অভাৰভিউ","Previous Assessments":"পূৰ্বৰ মূল্যায়ন","DIGITAL PATIENT MODEL":"ডিজিটেল ৰোগী মডেল","Digital Twin Timeline":"ডিজিটেল টুইন সময়ৰেখা","Joint Signal Analysis":"জইণ্ট চিগনেল বিশ্লেষণ","MODERATE MARKER STATE":"মধ্যম সূচক অৱস্থা","OA HUMAN DIGITAL TWIN":"OA হিউমেন ডিজিটেল টুইন","Personalized Baseline":"ব্যক্তিগতকৃত বেচলাইন","🦵 KNEE-ONLY SCREENING":"🦵 কেৱল আঁঠুৰ স্ক্ৰিনিং","1. Patient Information":"1. ৰোগীৰ তথ্য","IMU Module — Connected":"IMU মডিউল — সংযুক্ত","Local Database — Ready":"স্থানীয় ডাটাবেছ — সাজু","Patient Movement State":"ৰোগীৰ চলাচলৰ অৱস্থা","✓ Acquisition Complete":"✓ অধিগ্ৰহণ সম্পূৰ্ণ","Longitudinal monitoring":"দীৰ্ঘম্যাদী নিৰীক্ষণ","PERSONALIZED MONITORING":"ব্যক্তিগতকৃত নিৰীক্ষণ","Time-Frequency Analysis":"সময়-কম্পাঙ্ক বিশ্লেষণ","Joint Signal Acquisition":"জইণ্ট চিগনেল অধিগ্ৰহণ","Screening Interpretation":"স্ক্ৰিনিং ব্যাখ্যা","What Do the Grades Mean?":"গ্ৰেডৰ অৰ্থ কি?","actionable risk markers.":"কাৰ্যকৰী ঝুঁকি সূচক।","2. Connect Patient Record":"2. ৰোগীৰ ৰেকৰ্ড সংযোগ কৰক","What Did the System Find?":"চিষ্টেমে কি পাইছে?","Guided Assessment Protocol":"নিৰ্দেশিত মূল্যায়ন প্ৰট’কল","Multimodal Patient Profile":"মাল্টিম’ডেল ৰোগীৰ প্ৰ’ফাইল","OA-associated risk markers":"OA-সম্পৰ্কীয় ঝুঁকি সূচক","Turning joint signals into":"জইণ্ট চিগনেলক ৰূপান্তৰ কৰা","✓ Patient record confirmed":"✓ ৰোগীৰ ৰেকৰ্ড নিশ্চিত কৰা হৈছে","🦵 SCREENING SITE: KNEE ONLY":"🦵 স্ক্ৰিনিং স্থান: কেৱল আঁঠু","Longitudinal Risk Monitoring":"দীৰ্ঘম্যাদী ঝুঁকি নিৰীক্ষণ","What Does This Mean for You?":"ইয়াৰ আপোনাৰ বাবে অৰ্থ কি?","4. OA Risk Factors & Symptoms":"4. OA ঝুঁকি কাৰক আৰু লক্ষণ","Explainable Screening Factors":"ব্যাখ্যাযোগ্য স্ক্ৰিনিং কাৰক","PATIENT DIGITAL REPRESENTATION":"ৰোগীৰ ডিজিটেল প্ৰতিনিধিত্ব","Joint Signal Sensor — Connected":"জইণ্ট চিগনেল ছেন্সৰ — সংযুক্ত","PROTOTYPE / SIMULATED AI OUTPUT":"প্ৰ’টোটাইপ / চিমুলেটেড AI আউটপুট","Patient-Specific State Variables":"ৰোগী-নিৰ্দিষ্ট অৱস্থা চলক","Movement & Patient-Reported Findings":"চলাচল আৰু ৰোগীয়ে জনোৱা ফলাফল","3. Latest Reports & Medical Documents":"3. শেহতীয়া প্ৰতিবেদন আৰু চিকিৎসাগত নথি","ARTHROSONIC • FIELD SCREENING PLATFORM":"ARTHROSONIC • ফিল্ড স্ক্ৰিনিং প্লেটফৰ্ম","The ArthroSonic prototype measures the":"ArthroSonic প্ৰ’টোটাইপে মাপে","• AI-Assisted OA Risk Screening • SIH 2026":"• AI-সহায়িত OA ঝুঁকি স্ক্ৰিনিং • SIH 2026","From one-time screening to longitudinal monitoring.":"এবাৰৰ স্ক্ৰিনিঙৰ পৰা দীৰ্ঘম্যাদী নিৰীক্ষণলৈ।",". The screening site is fixed and cannot be changed.":"। স্ক্ৰিনিং স্থান নিৰ্দিষ্ট আৰু সলনি কৰিব নোৱাৰি।","These variables form the current demonstration state of the digital twin.":"এই চলকসমূহে ডিজিটেল টুইনৰ বৰ্তমান ডেমো অৱস্থা গঠন কৰে।","Current screening can now be linked with the patient's longitudinal record.":"বৰ্তমান স্ক্ৰিনিং এতিয়া ৰোগীৰ দীৰ্ঘম্যাদী ৰেকৰ্ডৰ সৈতে সংযোগ কৰিব পাৰি।","Signal quality is suitable for feature extraction and prototype AI analysis.":"চিগনেলৰ গুণমান ফিচাৰ নিষ্কাশন আৰু প্ৰ’টোটাইপ AI বিশ্লেষণৰ বাবে উপযুক্ত।","Combine patient-reported pain, stiffness, mobility and relevant risk factors.":"ৰোগীয়ে জনোৱা বিষ, জড়তা, চলাচল ক্ষমতা আৰু সংশ্লিষ্ট ঝুঁকি কাৰকসমূহ একত্ৰ কৰক।","Capture knee movement, gait, range of motion and left-right movement symmetry.":"আঁঠুৰ চলাচল, গেইট, গতি পৰিসৰ আৰু বাওঁ-সোঁ চলাচলৰ সমমিতি ৰেকৰ্ড কৰক।","Prototype multimodal analysis indicates a moderate level of OA-associated markers.":"প্ৰ’টোটাইপ মাল্টিম’ডেল বিশ্লেষণে মধ্যম স্তৰৰ OA-সম্পৰ্কীয় সূচক দেখুৱায়।","Longitudinal representation of movement, sound-pattern and symptom characteristics.":"চলাচল, শব্দ-পেটাৰ্ণ আৰু লক্ষণৰ বৈশিষ্ট্যৰ দীৰ্ঘম্যাদী প্ৰতিনিধিত্ব।","Prototype for screening research and demonstration. Not a medical diagnostic system.":"স্ক্ৰিনিং গৱেষণা আৰু ডেমোৰ বাবে প্ৰ’টোটাইপ। ই চিকিৎসাগত নিৰ্ণয় ব্যৱস্থা নহয়।","Place the PZT and microphone module over the knee joint and perform controlled flexion-extension movements.":"PZT আৰু মাইক্ৰ’ফোন মডিউল আঁঠুৰ জইণ্টৰ ওপৰত ৰাখি নিয়ন্ত্ৰিত ফ্লেক্সন-এক্সটেনচন চলাচল কৰক।","ArthroSonic is configured specifically for knee assessment. The screening joint is fixed and cannot be changed.":"ArthroSonic বিশেষভাৱে আঁঠুৰ মূল্যায়নৰ বাবে কনফিগাৰ কৰা হৈছে। স্ক্ৰিনিং জইণ্ট নিৰ্দিষ্ট আৰু সলনি কৰিব নোৱাৰি।","This page presents a preliminary screening interpretation for demonstration. It does not establish a medical diagnosis.":"এই পৃষ্ঠাই ডেমোৰ বাবে প্ৰাথমিক স্ক্ৰিনিং ব্যাখ্যা দেখুৱায়। ই চিকিৎসাগত নিৰ্ণয় স্থাপন নকৰে।","ArthroSonic stores repeated screening measurements so that future assessments can be compared with the patient's own historical baseline.":"ArthroSonic-এ পুনৰাবৃত্ত স্ক্ৰিনিং মাপ সংৰক্ষণ কৰে যাতে ভৱিষ্যৎ মূল্যায়ন ৰোগীৰ নিজৰ ঐতিহাসিক বেচলাইনৰ সৈতে তুলনা কৰিব পাৰি।","Changes in sound-pattern features, movement characteristics, symptoms and other recorded variables can therefore be visualized over time.":"সেয়ে শব্দ-পেটাৰ্ণ বৈশিষ্ট্য, চলাচলৰ বৈশিষ্ট্য, লক্ষণ আৰু অন্যান্য ৰেকৰ্ড কৰা চলকৰ পৰিৱৰ্তন সময়ৰ সৈতে দেখা যাব পাৰে।","The ArthroSonic Digital Twin organizes sound, movement, symptom and contextual measurements into a patient-specific longitudinal profile.":"ArthroSonic ডিজিটেল টুইনে শব্দ, চলাচল, লক্ষণ আৰু প্ৰাসংগিক মাপসমূহক ৰোগী-নিৰ্দিষ্ট দীৰ্ঘম্যাদী প্ৰ’ফাইলত সজায়।","ArthroSonic combines joint sound emissions, movement analysis, patient-reported symptoms and longitudinal data to support preliminary osteoarthritis risk screening in low-resource healthcare environments.":"ArthroSonic-এ জইণ্টৰ শব্দ নিৰ্গমন, চলাচল বিশ্লেষণ, ৰোগীয়ে জনোৱা লক্ষণ আৰু দীৰ্ঘম্যাদী তথ্য একত্ৰ কৰি সীমিত সম্পদৰ স্বাস্থ্যসেৱা পৰিৱেশত প্ৰাথমিক অষ্টিঅ’আৰ্থ্ৰাইটিছ ঝুঁকি স্ক্ৰিনিঙত সহায় কৰে।",
"No":"নহয়","Low":"কম","Yes":"হয়","High":"উচ্চ","Male":"পুৰুষ","Other":"অন্যান্য","Female":"মহিলা","Moderate":"মধ্যম","Amplitude":"এমপ্লিটিউড","Sound Events":"শব্দৰ ঘটনা","Time (seconds)":"সময় (ছেকেণ্ড)","Assessment Date":"মূল্যায়নৰ তাৰিখ","Knee Joint Signal":"আঁঠুৰ জইণ্ট চিগনেল","Sound Event Trend":"শব্দ ঘটনাৰ প্ৰৱণতা","🌐 Language / भाषा":"🌐 ভাষা","Prototype Risk Index":"প্ৰ’টোটাইপ ঝুঁকি সূচক","e.g. +91 98765 43210":"উদাহৰণ: +91 98765 43210","RUN MULTIMODAL AI ANALYSIS":"মাল্টিম’ডেল AI বিশ্লেষণ চলাওক","Attached for this assessment:":"এই মূল্যায়নৰ বাবে সংলগ্ন:","ArthroSonic Prototype • SIH 2026":"ArthroSonic প্ৰ’টোটাইপ • SIH 2026","Prototype multimodal analysis completed.":"প্ৰ’টোটাইপ মাল্টিম’ডেল বিশ্লেষণ সম্পূৰ্ণ হৈছে।","House / village / town / district / state":"ঘৰ / গাঁও / নগৰ / জিলা / ৰাজ্য","Joint-signal and movement sequence captured successfully.":"জইণ্ট চিগনেল আৰু চলাচলৰ ক্ৰম সফলভাৱে ৰেকৰ্ড কৰা হৈছে।","Prototype only: files are available during the current app session.":"কেৱল প্ৰ’টোটাইপ: ফাইলসমূহ বৰ্তমান এপ সেশ্যনৰ সময়ত উপলব্ধ।","Confirm the patient record to unlock document upload and the next step.":"নথি আপলোড আৰু পৰৱৰ্তী পদক্ষেপ সক্ৰিয় কৰিবলৈ ৰোগীৰ ৰেকৰ্ড নিশ্চিত কৰক।","Predictive screening only. This system does not diagnose OA or prescribe treatment.":"কেৱল পূৰ্বানুমানমূলক স্ক্ৰিনিং। এই চিষ্টেমে OA নিৰ্ণয় নকৰে বা চিকিৎসা নিৰ্ধাৰণ নকৰে।","Grades describe screening risk only. They do not confirm OA or show the amount of joint damage. Grade boundaries must be defined and validated for the AI model.":"গ্ৰেডে কেৱল স্ক্ৰিনিং ঝুঁকি বুজায়। ই OA নিশ্চিত নকৰে বা জইণ্টৰ ক্ষতিৰ পৰিমাণ নেদেখুৱায়। AI মডেলৰ বাবে গ্ৰেড সীমা সংজ্ঞায়িত আৰু বৈধ কৰিব লাগিব।",
},
"bn": {
"READY":"প্রস্তুত","Gait m/s":"গেইট m/s","Knee ROM":"হাঁটুর গতি পরিসর","MODERATE":"মাঝারি","Symmetry":"সমতা","ARTHROSONIC":"ARTHROSONIC","DEMO OUTPUT":"ডেমো আউটপুট","02 · Movement":"02 · নড়াচড়া","03 · Symptoms":"03 · উপসর্গ","Sensor Network":"সেন্সর নেটওয়ার্ক","Screening Grade":"স্ক্রিনিং গ্রেড","knee joint only":"শুধু হাঁটুর জয়েন্ট","01 · Joint Signal":"01 · জয়েন্ট সিগন্যাল","AI Engine — Ready":"AI ইঞ্জিন — প্রস্তুত","CURRENT SCREENING":"বর্তমান স্ক্রিনিং","Live Joint Signal":"লাইভ জয়েন্ট সিগন্যাল","Patient Twin State":"রোগীর টুইন অবস্থা","Right Knee Profile":"ডান হাঁটুর প্রোফাইল","Screening Workflow":"স্ক্রিনিং কার্যপ্রবাহ","Longitudinal Trends":"দীর্ঘমেয়াদি প্রবণতা","Why a Digital Twin?":"ডিজিটাল টুইন কেন?","Live System Overview":"লাইভ সিস্টেম ওভারভিউ","Previous Assessments":"পূর্ববর্তী মূল্যায়ন","DIGITAL PATIENT MODEL":"ডিজিটাল রোগী মডেল","Digital Twin Timeline":"ডিজিটাল টুইন টাইমলাইন","Joint Signal Analysis":"জয়েন্ট সিগন্যাল বিশ্লেষণ","MODERATE MARKER STATE":"মাঝারি সূচক অবস্থা","OA HUMAN DIGITAL TWIN":"OA হিউম্যান ডিজিটাল টুইন","Personalized Baseline":"ব্যক্তিগত বেসলাইন","🦵 KNEE-ONLY SCREENING":"🦵 শুধু হাঁটুর স্ক্রিনিং","1. Patient Information":"1. রোগীর তথ্য","IMU Module — Connected":"IMU মডিউল — সংযুক্ত","Local Database — Ready":"স্থানীয় ডেটাবেস — প্রস্তুত","Patient Movement State":"রোগীর নড়াচড়ার অবস্থা","✓ Acquisition Complete":"✓ অধিগ্রহণ সম্পূর্ণ","Longitudinal monitoring":"দীর্ঘমেয়াদি পর্যবেক্ষণ","PERSONALIZED MONITORING":"ব্যক্তিগত পর্যবেক্ষণ","Time-Frequency Analysis":"সময়-কম্পাঙ্ক বিশ্লেষণ","Joint Signal Acquisition":"জয়েন্ট সিগন্যাল অধিগ্রহণ","Screening Interpretation":"স্ক্রিনিং ব্যাখ্যা","What Do the Grades Mean?":"গ্রেডগুলোর অর্থ কী?","actionable risk markers.":"কার্যকর ঝুঁকি সূচক।","2. Connect Patient Record":"2. রোগীর রেকর্ড সংযুক্ত করুন","What Did the System Find?":"সিস্টেম কী পেয়েছে?","Guided Assessment Protocol":"নির্দেশিত মূল্যায়ন প্রোটোকল","Multimodal Patient Profile":"মাল্টিমোডাল রোগী প্রোফাইল","OA-associated risk markers":"OA-সম্পর্কিত ঝুঁকি সূচক","Turning joint signals into":"জয়েন্ট সিগন্যালকে রূপান্তর করা","✓ Patient record confirmed":"✓ রোগীর রেকর্ড নিশ্চিত হয়েছে","🦵 SCREENING SITE: KNEE ONLY":"🦵 স্ক্রিনিং স্থান: শুধু হাঁটু","Longitudinal Risk Monitoring":"দীর্ঘমেয়াদি ঝুঁকি পর্যবেক্ষণ","What Does This Mean for You?":"আপনার জন্য এর অর্থ কী?","4. OA Risk Factors & Symptoms":"4. OA ঝুঁকির কারণ ও উপসর্গ","Explainable Screening Factors":"ব্যাখ্যাযোগ্য স্ক্রিনিং কারণ","PATIENT DIGITAL REPRESENTATION":"রোগীর ডিজিটাল উপস্থাপন","Joint Signal Sensor — Connected":"জয়েন্ট সিগন্যাল সেন্সর — সংযুক্ত","PROTOTYPE / SIMULATED AI OUTPUT":"প্রোটোটাইপ / সিমুলেটেড AI আউটপুট","Patient-Specific State Variables":"রোগী-নির্দিষ্ট অবস্থা চলক","Movement & Patient-Reported Findings":"নড়াচড়া ও রোগীর জানানো ফলাফল","3. Latest Reports & Medical Documents":"3. সাম্প্রতিক রিপোর্ট ও চিকিৎসা নথি","ARTHROSONIC • FIELD SCREENING PLATFORM":"ARTHROSONIC • ফিল্ড স্ক্রিনিং প্ল্যাটফর্ম","The ArthroSonic prototype measures the":"ArthroSonic প্রোটোটাইপ মাপে","• AI-Assisted OA Risk Screening • SIH 2026":"• AI-সহায়িত OA ঝুঁকি স্ক্রিনিং • SIH 2026","From one-time screening to longitudinal monitoring.":"একবারের স্ক্রিনিং থেকে দীর্ঘমেয়াদি পর্যবেক্ষণ পর্যন্ত।",". The screening site is fixed and cannot be changed.":"। স্ক্রিনিং স্থান নির্দিষ্ট এবং পরিবর্তন করা যায় না।","These variables form the current demonstration state of the digital twin.":"এই চলকগুলো ডিজিটাল টুইনের বর্তমান ডেমো অবস্থা তৈরি করে।","Current screening can now be linked with the patient's longitudinal record.":"বর্তমান স্ক্রিনিং এখন রোগীর দীর্ঘমেয়াদি রেকর্ডের সঙ্গে যুক্ত করা যেতে পারে।","Signal quality is suitable for feature extraction and prototype AI analysis.":"সিগন্যালের গুণমান ফিচার নিষ্কাশন ও প্রোটোটাইপ AI বিশ্লেষণের জন্য উপযুক্ত।","Combine patient-reported pain, stiffness, mobility and relevant risk factors.":"রোগীর জানানো ব্যথা, জড়তা, চলাচল এবং সংশ্লিষ্ট ঝুঁকির কারণগুলো একত্র করুন।","Capture knee movement, gait, range of motion and left-right movement symmetry.":"হাঁটুর নড়াচড়া, গেইট, গতি পরিসর এবং বাম-ডান নড়াচড়ার সমতা রেকর্ড করুন।","Prototype multimodal analysis indicates a moderate level of OA-associated markers.":"প্রোটোটাইপ মাল্টিমোডাল বিশ্লেষণ মাঝারি মাত্রার OA-সম্পর্কিত সূচক দেখায়।","Longitudinal representation of movement, sound-pattern and symptom characteristics.":"নড়াচড়া, শব্দ-প্যাটার্ন ও উপসর্গের বৈশিষ্ট্যের দীর্ঘমেয়াদি উপস্থাপন।","Prototype for screening research and demonstration. Not a medical diagnostic system.":"স্ক্রিনিং গবেষণা ও প্রদর্শনের জন্য প্রোটোটাইপ। এটি চিকিৎসাগত রোগনির্ণয় ব্যবস্থা নয়।","Place the PZT and microphone module over the knee joint and perform controlled flexion-extension movements.":"PZT ও মাইক্রোফোন মডিউল হাঁটুর জয়েন্টের উপর রাখুন এবং নিয়ন্ত্রিত ফ্লেক্সন-এক্সটেনশন নড়াচড়া করুন।","ArthroSonic is configured specifically for knee assessment. The screening joint is fixed and cannot be changed.":"ArthroSonic বিশেষভাবে হাঁটু মূল্যায়নের জন্য কনফিগার করা। স্ক্রিনিং জয়েন্ট নির্দিষ্ট এবং পরিবর্তন করা যায় না।","This page presents a preliminary screening interpretation for demonstration. It does not establish a medical diagnosis.":"এই পৃষ্ঠা প্রদর্শনের জন্য প্রাথমিক স্ক্রিনিং ব্যাখ্যা দেখায়। এটি চিকিৎসাগত রোগনির্ণয় প্রতিষ্ঠা করে না।","ArthroSonic stores repeated screening measurements so that future assessments can be compared with the patient's own historical baseline.":"ArthroSonic পুনরাবৃত্ত স্ক্রিনিং মাপ সংরক্ষণ করে যাতে ভবিষ্যৎ মূল্যায়ন রোগীর নিজস্ব ঐতিহাসিক বেসলাইনের সঙ্গে তুলনা করা যায়।","Changes in sound-pattern features, movement characteristics, symptoms and other recorded variables can therefore be visualized over time.":"এর ফলে শব্দ-প্যাটার্নের বৈশিষ্ট্য, নড়াচড়ার বৈশিষ্ট্য, উপসর্গ এবং অন্যান্য রেকর্ড করা চলকের পরিবর্তন সময়ের সঙ্গে দেখা যায়।","The ArthroSonic Digital Twin organizes sound, movement, symptom and contextual measurements into a patient-specific longitudinal profile.":"ArthroSonic ডিজিটাল টুইন শব্দ, নড়াচড়া, উপসর্গ ও প্রাসঙ্গিক মাপগুলোকে রোগী-নির্দিষ্ট দীর্ঘমেয়াদি প্রোফাইলে সাজায়।","ArthroSonic combines joint sound emissions, movement analysis, patient-reported symptoms and longitudinal data to support preliminary osteoarthritis risk screening in low-resource healthcare environments.":"ArthroSonic জয়েন্টের শব্দ নির্গমন, নড়াচড়া বিশ্লেষণ, রোগীর জানানো উপসর্গ এবং দীর্ঘমেয়াদি ডেটা একত্র করে সীমিত সম্পদের স্বাস্থ্যসেবা পরিবেশে প্রাথমিক অস্টিওআর্থ্রাইটিস ঝুঁকি স্ক্রিনিংয়ে সহায়তা করে।",
"No":"না","Low":"কম","Yes":"হ্যাঁ","High":"উচ্চ","Male":"পুরুষ","Other":"অন্যান্য","Female":"মহিলা","Moderate":"মাঝারি","Amplitude":"অ্যামপ্লিটিউড","Sound Events":"শব্দের ঘটনা","Time (seconds)":"সময় (সেকেন্ড)","Assessment Date":"মূল্যায়নের তারিখ","Knee Joint Signal":"হাঁটুর জয়েন্ট সিগন্যাল","Sound Event Trend":"শব্দ ঘটনার প্রবণতা","🌐 Language / भाषा":"🌐 ভাষা","Prototype Risk Index":"প্রোটোটাইপ ঝুঁকি সূচক","e.g. +91 98765 43210":"উদাহরণ: +91 98765 43210","RUN MULTIMODAL AI ANALYSIS":"মাল্টিমোডাল AI বিশ্লেষণ চালান","Attached for this assessment:":"এই মূল্যায়নের জন্য সংযুক্ত:","ArthroSonic Prototype • SIH 2026":"ArthroSonic প্রোটোটাইপ • SIH 2026","Prototype multimodal analysis completed.":"প্রোটোটাইপ মাল্টিমোডাল বিশ্লেষণ সম্পন্ন হয়েছে।","House / village / town / district / state":"বাড়ি / গ্রাম / শহর / জেলা / রাজ্য","Joint-signal and movement sequence captured successfully.":"জয়েন্ট সিগন্যাল ও নড়াচড়ার ক্রম সফলভাবে রেকর্ড হয়েছে।","Prototype only: files are available during the current app session.":"শুধু প্রোটোটাইপ: ফাইলগুলো বর্তমান অ্যাপ সেশনে উপলব্ধ।","Confirm the patient record to unlock document upload and the next step.":"নথি আপলোড ও পরবর্তী ধাপ চালু করতে রোগীর রেকর্ড নিশ্চিত করুন।","Predictive screening only. This system does not diagnose OA or prescribe treatment.":"শুধু পূর্বাভাসমূলক স্ক্রিনিং। এই সিস্টেম OA নির্ণয় বা চিকিৎসা নির্দেশ করে না।","Grades describe screening risk only. They do not confirm OA or show the amount of joint damage. Grade boundaries must be defined and validated for the AI model.":"গ্রেড শুধু স্ক্রিনিং ঝুঁকি বোঝায়। এগুলো OA নিশ্চিত করে না বা জয়েন্টের ক্ষতির পরিমাণ দেখায় না। AI মডেলের জন্য গ্রেডের সীমা নির্ধারণ ও যাচাই করতে হবে।",
},
"ne": {
"READY":"तयार","Gait m/s":"गेट m/s","Knee ROM":"घुँडाको गति दायरा","MODERATE":"मध्यम","Symmetry":"सममिति","ARTHROSONIC":"ARTHROSONIC","DEMO OUTPUT":"डेमो आउटपुट","02 · Movement":"02 · चाल","03 · Symptoms":"03 · लक्षण","Sensor Network":"सेन्सर नेटवर्क","Screening Grade":"स्क्रिनिङ ग्रेड","knee joint only":"घुँडाको जोइन्ट मात्र","01 · Joint Signal":"01 · जोइन्ट सङ्केत","AI Engine — Ready":"AI इन्जिन — तयार","CURRENT SCREENING":"हालको स्क्रिनिङ","Live Joint Signal":"लाइभ जोइन्ट सङ्केत","Patient Twin State":"बिरामी ट्विन अवस्था","Right Knee Profile":"दायाँ घुँडाको प्रोफाइल","Screening Workflow":"स्क्रिनिङ कार्यप्रवाह","Longitudinal Trends":"दीर्घकालीन प्रवृत्तिहरू","Why a Digital Twin?":"डिजिटल ट्विन किन?","Live System Overview":"लाइभ प्रणाली अवलोकन","Previous Assessments":"अघिल्ला मूल्याङ्कनहरू","DIGITAL PATIENT MODEL":"डिजिटल बिरामी मोडेल","Digital Twin Timeline":"डिजिटल ट्विन समयरेखा","Joint Signal Analysis":"जोइन्ट सङ्केत विश्लेषण","MODERATE MARKER STATE":"मध्यम सूचक अवस्था","OA HUMAN DIGITAL TWIN":"OA ह्युमन डिजिटल ट्विन","Personalized Baseline":"व्यक्तिगत बेसलाइन","🦵 KNEE-ONLY SCREENING":"🦵 घुँडा मात्र स्क्रिनिङ","1. Patient Information":"1. बिरामीको जानकारी","IMU Module — Connected":"IMU मोड्युल — जडान भएको","Local Database — Ready":"स्थानीय डाटाबेस — तयार","Patient Movement State":"बिरामीको चाल अवस्था","✓ Acquisition Complete":"✓ अधिग्रहण पूरा भयो","Longitudinal monitoring":"दीर्घकालीन निगरानी","PERSONALIZED MONITORING":"व्यक्तिगत निगरानी","Time-Frequency Analysis":"समय-फ्रिक्वेन्सी विश्लेषण","Joint Signal Acquisition":"जोइन्ट सङ्केत अधिग्रहण","Screening Interpretation":"स्क्रिनिङ व्याख्या","What Do the Grades Mean?":"ग्रेडको अर्थ के हो?","actionable risk markers.":"कार्यान्वयनयोग्य जोखिम सूचकहरू।","2. Connect Patient Record":"2. बिरामी रेकर्ड जडान गर्नुहोस्","What Did the System Find?":"प्रणालीले के पत्ता लगायो?","Guided Assessment Protocol":"निर्देशित मूल्याङ्कन प्रोटोकल","Multimodal Patient Profile":"मल्टिमोडल बिरामी प्रोफाइल","OA-associated risk markers":"OA-सम्बन्धित जोखिम सूचक","Turning joint signals into":"जोइन्ट सङ्केतलाई रूपान्तरण गर्दै","✓ Patient record confirmed":"✓ बिरामी रेकर्ड पुष्टि भयो","🦵 SCREENING SITE: KNEE ONLY":"🦵 स्क्रिनिङ स्थान: घुँडा मात्र","Longitudinal Risk Monitoring":"दीर्घकालीन जोखिम निगरानी","What Does This Mean for You?":"यसको तपाईंका लागि के अर्थ छ?","4. OA Risk Factors & Symptoms":"4. OA जोखिम कारक र लक्षण","Explainable Screening Factors":"व्याख्यायोग्य स्क्रिनिङ कारक","PATIENT DIGITAL REPRESENTATION":"बिरामीको डिजिटल प्रतिनिधित्व","Joint Signal Sensor — Connected":"जोइन्ट सङ्केत सेन्सर — जडान भएको","PROTOTYPE / SIMULATED AI OUTPUT":"प्रोटोटाइप / सिमुलेटेड AI आउटपुट","Patient-Specific State Variables":"बिरामी-विशिष्ट अवस्था चरहरू","Movement & Patient-Reported Findings":"चाल र बिरामीले बताएका निष्कर्षहरू","3. Latest Reports & Medical Documents":"3. नयाँ रिपोर्ट र चिकित्सा कागजातहरू","ARTHROSONIC • FIELD SCREENING PLATFORM":"ARTHROSONIC • फिल्ड स्क्रिनिङ प्लेटफर्म","The ArthroSonic prototype measures the":"ArthroSonic प्रोटोटाइपले मापन गर्छ","• AI-Assisted OA Risk Screening • SIH 2026":"• AI-सहायित OA जोखिम स्क्रिनिङ • SIH 2026","From one-time screening to longitudinal monitoring.":"एकपटकको स्क्रिनिङदेखि दीर्घकालीन निगरानीसम्म।",". The screening site is fixed and cannot be changed.":"। स्क्रिनिङ स्थान निश्चित छ र परिवर्तन गर्न सकिँदैन।","These variables form the current demonstration state of the digital twin.":"यी चरहरूले डिजिटल ट्विनको हालको डेमो अवस्था बनाउँछन्।","Current screening can now be linked with the patient's longitudinal record.":"हालको स्क्रिनिङ अब बिरामीको दीर्घकालीन रेकर्डसँग जोड्न सकिन्छ।","Signal quality is suitable for feature extraction and prototype AI analysis.":"सङ्केतको गुणस्तर फिचर एक्स्ट्र्याक्सन र प्रोटोटाइप AI विश्लेषणका लागि उपयुक्त छ।","Combine patient-reported pain, stiffness, mobility and relevant risk factors.":"बिरामीले बताएका दुखाइ, कडापन, गतिशीलता र सम्बन्धित जोखिम कारकहरू जोड्नुहोस्।","Capture knee movement, gait, range of motion and left-right movement symmetry.":"घुँडाको चाल, गेट, गति दायरा र बायाँ-दायाँ चालको सममिति रेकर्ड गर्नुहोस्।","Prototype multimodal analysis indicates a moderate level of OA-associated markers.":"प्रोटोटाइप मल्टिमोडल विश्लेषणले मध्यम स्तरका OA-सम्बन्धित सूचक देखाउँछ।","Longitudinal representation of movement, sound-pattern and symptom characteristics.":"चाल, ध्वनि-प्याटर्न र लक्षणका विशेषताहरूको दीर्घकालीन प्रतिनिधित्व।","Prototype for screening research and demonstration. Not a medical diagnostic system.":"स्क्रिनिङ अनुसन्धान र डेमोका लागि प्रोटोटाइप। यो चिकित्सकीय निदान प्रणाली होइन।","Place the PZT and microphone module over the knee joint and perform controlled flexion-extension movements.":"PZT र माइक्रोफोन मोड्युल घुँडाको जोइन्टमाथि राखेर नियन्त्रित फ्लेक्सन-एक्सटेन्सन चाल गर्नुहोस्।","ArthroSonic is configured specifically for knee assessment. The screening joint is fixed and cannot be changed.":"ArthroSonic विशेष रूपमा घुँडा मूल्याङ्कनका लागि कन्फिगर गरिएको छ। स्क्रिनिङ जोइन्ट निश्चित छ र परिवर्तन गर्न सकिँदैन।","This page presents a preliminary screening interpretation for demonstration. It does not establish a medical diagnosis.":"यो पृष्ठले डेमोका लागि प्रारम्भिक स्क्रिनिङ व्याख्या प्रस्तुत गर्छ। यसले चिकित्सकीय निदान स्थापित गर्दैन।","ArthroSonic stores repeated screening measurements so that future assessments can be compared with the patient's own historical baseline.":"ArthroSonic ले दोहोरिएका स्क्रिनिङ मापनहरू भण्डारण गर्छ ताकि भविष्यका मूल्याङ्कन बिरामीको आफ्नै ऐतिहासिक बेसलाइनसँग तुलना गर्न सकियोस्।","Changes in sound-pattern features, movement characteristics, symptoms and other recorded variables can therefore be visualized over time.":"यसरी ध्वनि-प्याटर्न विशेषता, चालका विशेषता, लक्षण र अन्य रेकर्ड गरिएका चरका परिवर्तन समयसँगै देख्न सकिन्छ।","The ArthroSonic Digital Twin organizes sound, movement, symptom and contextual measurements into a patient-specific longitudinal profile.":"ArthroSonic डिजिटल ट्विनले ध्वनि, चाल, लक्षण र सन्दर्भगत मापनहरूलाई बिरामी-विशिष्ट दीर्घकालीन प्रोफाइलमा व्यवस्थित गर्छ।","ArthroSonic combines joint sound emissions, movement analysis, patient-reported symptoms and longitudinal data to support preliminary osteoarthritis risk screening in low-resource healthcare environments.":"ArthroSonic ले जोइन्टको ध्वनि उत्सर्जन, चाल विश्लेषण, बिरामीले बताएका लक्षण र दीर्घकालीन डेटा जोडेर सीमित स्रोत भएका स्वास्थ्य वातावरणमा प्रारम्भिक ओस्टियोआर्थराइटिस जोखिम स्क्रिनिङमा सहयोग गर्छ।",
"No":"होइन","Low":"कम","Yes":"हो","High":"उच्च","Male":"पुरुष","Other":"अन्य","Female":"महिला","Moderate":"मध्यम","Amplitude":"आयाम","Sound Events":"ध्वनि घटनाहरू","Time (seconds)":"समय (सेकेन्ड)","Assessment Date":"मूल्याङ्कन मिति","Knee Joint Signal":"घुँडा जोइन्ट सङ्केत","Sound Event Trend":"ध्वनि घटनाको प्रवृत्ति","🌐 Language / भाषा":"🌐 भाषा","Prototype Risk Index":"प्रोटोटाइप जोखिम सूचकाङ्क","e.g. +91 98765 43210":"उदाहरण: +91 98765 43210","RUN MULTIMODAL AI ANALYSIS":"मल्टिमोडल AI विश्लेषण चलाउनुहोस्","Attached for this assessment:":"यस मूल्याङ्कनका लागि संलग्न:","ArthroSonic Prototype • SIH 2026":"ArthroSonic प्रोटोटाइप • SIH 2026","Prototype multimodal analysis completed.":"प्रोटोटाइप मल्टिमोडल विश्लेषण पूरा भयो।","House / village / town / district / state":"घर / गाउँ / सहर / जिल्ला / राज्य","Joint-signal and movement sequence captured successfully.":"जोइन्ट-सङ्केत र चाल क्रम सफलतापूर्वक रेकर्ड भयो।","Prototype only: files are available during the current app session.":"प्रोटोटाइप मात्र: फाइलहरू हालको एप सत्रमा उपलब्ध छन्।","Confirm the patient record to unlock document upload and the next step.":"कागजात अपलोड र अर्को चरण खोल्न बिरामी रेकर्ड पुष्टि गर्नुहोस्।","Predictive screening only. This system does not diagnose OA or prescribe treatment.":"पूर्वानुमानात्मक स्क्रिनिङ मात्र। यस प्रणालीले OA निदान वा उपचार तोक्दैन।","Grades describe screening risk only. They do not confirm OA or show the amount of joint damage. Grade boundaries must be defined and validated for the AI model.":"ग्रेडले स्क्रिनिङ जोखिम मात्र जनाउँछन्। तिनले OA पुष्टि गर्दैनन् वा जोइन्ट क्षतिको मात्रा देखाउँदैनन्। AI मोडेलका लागि ग्रेड सीमा परिभाषित र मान्य गर्नुपर्छ।",
},
}
for _lang, _pack in _EXTRA_EXACT_UI.items():
    TRANSLATIONS.setdefault(_lang, {}).update(_pack)

_EXTRA_EXACT_UI["ne"].update({
    "Terrain Exposure":"भू-भागको सम्पर्क",
    "Risk Index":"जोखिम सूचकाङ्क",
    "AI-Assisted Osteoarthritis Risk Screening":"AI-सहायित ओस्टियोआर्थराइटिस जोखिम स्क्रिनिङ",
    "Frequency (Hz)":"फ्रिक्वेन्सी (Hz)",
})
for _lang in ("hi", "as", "bn"):
    _EXTRA_EXACT_UI[_lang].setdefault("Frequency (Hz)", {
        "hi":"आवृत्ति (Hz)", "as":"কম্পাঙ্ক (Hz)", "bn":"কম্পাঙ্ক (Hz)"
    }[_lang])
for _lang, _pack in _EXTRA_EXACT_UI.items():
    TRANSLATIONS.setdefault(_lang, {}).update(_pack)

# Reverse map lets the app normalize phrases that were hard-coded in an
# earlier localized version of a page, then translate them into the newly
# selected language instead of leaving mixed-language fragments behind.
_REVERSE_UI = {}
for _lang, _pack in TRANSLATIONS.items():
    for _src, _dst in _pack.items():
        if isinstance(_dst, str) and _dst:
            _REVERSE_UI[_dst.strip()] = _src


def _normalize_ui_text(value):
    return re.sub(r"\s+", " ", str(value)).strip()

def current_language():
    return st.session_state.get("language", "en")


def t(text):
    """Exact phrase translation. No word-by-word fallback is used."""
    if not isinstance(text, str):
        return text
    lang = current_language()
    if lang == "en":
        return text
    key = text if text in TRANSLATIONS.get(lang, {}) else _REVERSE_UI.get(_normalize_ui_text(text), text)
    return TRANSLATIONS.get(lang, {}).get(key, text)


def localize_df(df):
    """Translate dataframe labels/values and guarantee unique column names."""
    out = df.copy()
    translated_columns = [t(str(c)) for c in out.columns]
    seen = {}
    unique_columns = []
    for col in translated_columns:
        base = str(col)
        count = seen.get(base, 0)
        unique = base if count == 0 else f"{base} ({count + 1})"
        while unique in seen:
            count += 1
            unique = f"{base} ({count + 1})"
        seen[base] = count + 1
        seen[unique] = seen.get(unique, 0)
        unique_columns.append(unique)
    out.columns = unique_columns
    for c in out.columns:
        out[c] = out[c].map(lambda v: t(v) if isinstance(v, str) else v)
    return out


def translate_html(content):
    """Translate only visible HTML text nodes; never touch CSS or attributes."""
    if not isinstance(content, str) or current_language() == "en":
        return content

    # Protect style/script blocks from text translation.
    protected = []
    def _protect(match):
        protected.append(match.group(0))
        return f"__ARTHRO_PROTECTED_{len(protected)-1}__"

    content = re.sub(r"<style\b[^>]*>.*?</style>|<script\b[^>]*>.*?</script>", _protect, content, flags=re.I|re.S)

    def _node(match):
        raw = match.group(1)
        if not raw.strip():
            return match.group(0)
        core = _normalize_ui_text(raw)
        translated = t(core)
        if translated == core:
            return match.group(0)
        leading = raw[:len(raw) - len(raw.lstrip())]
        trailing = raw[len(raw.rstrip()):]
        return ">" + leading + translated + trailing + "<"

    # This only operates between HTML tags. It cannot modify tag attributes.
    content = re.sub(r">([^<>]+)<", _node, content)

    for i, block in enumerate(protected):
        content = content.replace(f"__ARTHRO_PROTECTED_{i}__", block)
    return content


# Legacy fallback vocabulary retained only for source compatibility.
# It is intentionally NOT used by t()/translate_html().
UI_FALLBACK = {}
def _fallback_translate(text, lang):
    return text

# ============================================================
# HTML / MARKDOWN RENDERING HELPER
# ============================================================

def render_markdown(content, *args, **kwargs):
    # Streamlit 1.64 can render raw HTML directly with st.html().
    # Apply the selected language to visible UI text before rendering.
    if isinstance(content, str):
        content = textwrap.dedent(content).strip()
        content = translate_html(content)

        if "<" in content and ">" in content:
            return st.html(content)

    return st.markdown(content, *args, **kwargs)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="ArthroSonic | AI OA Screening",
    page_icon="🦴",
    layout="wide",
    initial_sidebar_state="expanded"
)
LOGO_PATH = Path("Assets/logo.png")
if not LOGO_PATH.exists():
    LOGO_PATH = Path("assets/logo.png")
if LOGO_PATH.exists():
    st.logo(str(LOGO_PATH))

if "language" not in st.session_state:
    st.session_state.language = "en"

# ============================================================
# RESPONSIVE LIGHT / DARK THEME
# ============================================================

# ============================================================
# STREAMLIT CHROME / SIDEBAR TOGGLE
# ============================================================

render_markdown("""
<style>
/* Keep Streamlit's header so the sidebar can always be reopened. */
header[data-testid="stHeader"] {
    background: transparent !important;
}

/* Keep the sidebar collapse/expand control visible. */
button[data-testid="stSidebarCollapseButton"],
button[data-testid="stSidebarCollapseButton"] svg {
    visibility: visible !important;
    opacity: 1 !important;
}

/* Make the owner toolbar unobtrusive rather than removing the header. */
div[data-testid="stToolbar"] {
    opacity: 0.55;
}

/* Navigation typography */
section[data-testid="stSidebar"] div[role="radiogroup"] label {
    min-height: 42px !important;
    padding: 8px 10px !important;
    border-radius: 10px !important;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label p {
    font-size: 15px !important;
    font-weight: 650 !important;
    line-height: 1.25 !important;
}

section[data-testid="stSidebar"] .stRadio > label {
    font-size: 13px !important;
    font-weight: 800 !important;
    letter-spacing: 0.7px !important;
}

/* The language picker sits on the dark sidebar, but its selected value must stay black. */
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] div[data-baseweb="select"],
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] div[data-baseweb="select"] *,
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] input {
    color: #111827 !important;
    -webkit-text-fill-color: #111827 !important;
}
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background: #ffffff !important;
}
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] [data-baseweb="select"],
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] [data-baseweb="select"] *,
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] input,
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] span {
    color: #111827 !important;
    -webkit-text-fill-color: #111827 !important;
}
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] [role="option"],
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] [role="option"] * {
    color: #111827 !important;
    background: #ffffff !important;
}

.status-row {
    display: flex;
    align-items: center;
    gap: 9px;
    font-size: 15px;
    font-weight: 650;
    padding: 7px 10px;
    border-radius: 10px;
}

.next-row {
    margin-top: 30px;
}
</style>
""")

render_markdown("""
<style>

/* =========================================================
   BASE
   ========================================================= */

:root {
    --bg: #f5f7fb;
    --surface: #ffffff;
    --surface-2: #f8fafc;
    --text: #101828;
    --text2: #475467;
    --muted: #667085;
    --border: #e4e7ec;
    --accent: #2563eb;
    --accent2: #06b6d4;
    --success: #12b76a;
    --warning: #f79009;
    --danger: #f04438;
}

/* Light mode */

.stApp {
    background: var(--bg) !important;
}

.main {
    background: var(--bg) !important;
}

.block-container {
    padding-top: 1.3rem;
    padding-bottom: 3rem;
    max-width: 1500px;
}

.stApp,
.stApp p,
.stApp span,
.stApp label,
.stApp li {
    color: var(--text2);
}

h1, h2, h3, h4, h5, h6 {
    color: var(--text) !important;
}


/* =========================================================
   DARK MODE
   Follows browser/system preference
   ========================================================= */

@media (prefers-color-scheme: dark) {

    :root {
        --bg: #090d16;
        --surface: #111827;
        --surface-2: #172033;
        --text: #f9fafb;
        --text2: #d0d5dd;
        --muted: #98a2b3;
        --border: #263246;
        --accent: #60a5fa;
        --accent2: #22d3ee;
    }

    .stApp,
    .main {
        background: #090d16 !important;
    }

    .stApp p,
    .stApp span,
    .stApp label,
    .stApp li {
        color: #d0d5dd !important;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #f9fafb !important;
    }

    .hero-title {
        color: #f9fafb !important;
    }

    .hero-subtitle {
        color: #98a2b3 !important;
    }

    .card,
    .metric-card,
    .glass-card {
        background: #111827 !important;
        border-color: #263246 !important;
    }

    .card p,
    .card li {
        color: #d0d5dd !important;
    }

    .metric-label,
    .metric-small {
        color: #98a2b3 !important;
    }

    .metric-value {
        color: #f9fafb !important;
    }

    div[data-baseweb="input"] input,
    div[data-baseweb="textarea"] textarea,
    div[data-baseweb="select"] > div {
        background: #111827 !important;
        color: #f9fafb !important;
        border-color: #344054 !important;
    }
}


/* =========================================================
   SIDEBAR
   ========================================================= */

section[data-testid="stSidebar"] {
    background: #0b1220 !important;
}

section[data-testid="stSidebar"] * {
    color: #f8fafc !important;
}


/* =========================================================
   HERO
   ========================================================= */

.hero-title {
    font-size: clamp(30px, 4vw, 48px);
    font-weight: 850;
    letter-spacing: -1.8px;
    color: var(--text) !important;
    line-height: 1.05;
    margin-bottom: 8px;
}

.hero-subtitle {
    font-size: 16px;
    color: var(--muted) !important;
    line-height: 1.6;
}


/* =========================================================
   SECTION TITLES
   ========================================================= */

.section-title {
    font-size: 24px;
    font-weight: 800;
    color: var(--text) !important;
    margin-top: 28px;
    margin-bottom: 15px;
}


/* =========================================================
   CARDS
   ========================================================= */

.card {
    background: var(--surface) !important;
    border-radius: 20px;
    padding: 25px;
    border: 1px solid var(--border);
    box-shadow: 0 8px 30px rgba(16,24,40,0.06);
    color: var(--text2);
}

.card h1,
.card h2,
.card h3,
.card h4 {
    color: var(--text) !important;
}

.card p,
.card li {
    color: var(--text2) !important;
}


/* =========================================================
   GLASS CARDS
   ========================================================= */

.glass-card {
    background: rgba(255,255,255,0.82);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 22px;
    box-shadow: 0 10px 35px rgba(16,24,40,0.07);
    backdrop-filter: blur(10px);
}


/* =========================================================
   METRIC CARDS
   ========================================================= */

.metric-card {
    background: var(--surface) !important;
    border-radius: 18px;
    padding: 20px;
    border: 1px solid var(--border);
    min-height: 125px;
    box-shadow: 0 6px 20px rgba(16,24,40,0.05);
}

.metric-label {
    color: var(--muted) !important;
    font-size: 12px;
    font-weight: 750;
    letter-spacing: 0.7px;
    text-transform: uppercase;
}

.metric-value {
    font-size: 29px;
    font-weight: 850;
    color: var(--text) !important;
    margin-top: 8px;
}

.metric-small {
    color: var(--muted) !important;
    font-size: 13px;
    margin-top: 4px;
}


/* =========================================================
   STATUS CHIPS
   ========================================================= */

.status-chip {
    display: inline-block;
    padding: 7px 12px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 750;
}

.status-green {
    background: #ecfdf3;
    color: #027a48 !important;
}

.status-blue {
    background: #eff8ff;
    color: #175cd3 !important;
}

.status-yellow {
    background: #fffaeb;
    color: #b54708 !important;
}


/* =========================================================
   HERO GRADIENT
   ========================================================= */

.hero-box {
    border-radius: 24px;
    padding: 30px;
    background:
        radial-gradient(circle at 85% 15%, rgba(34,211,238,0.18), transparent 30%),
        radial-gradient(circle at 15% 85%, rgba(37,99,235,0.15), transparent 35%),
        var(--surface);
    border: 1px solid var(--border);
    box-shadow: 0 12px 40px rgba(16,24,40,0.08);
}


/* =========================================================
   RISK DISPLAY
   ========================================================= */

.risk-moderate {
    background: linear-gradient(
        135deg,
        rgba(245,158,11,0.13),
        rgba(255,255,255,0.8)
    );
    border: 1px solid #fedf89;
    border-radius: 20px;
    padding: 25px;
}

.risk-score {
    font-size: 52px;
    font-weight: 900;
    color: #b54708 !important;
    line-height: 1;
}


/* =========================================================
   DIGITAL TWIN
   ========================================================= */

.twin-box {
    border-radius: 24px;
    padding: 25px;
    background:
        radial-gradient(circle at center,
        rgba(37,99,235,0.14),
        transparent 55%),
        var(--surface);
    border: 1px solid var(--border);
    min-height: 400px;
}


/* =========================================================
   TIMELINE
   ========================================================= */

.timeline-item {
    border-left: 3px solid var(--accent);
    padding-left: 18px;
    margin-bottom: 20px;
}

.timeline-date {
    font-size: 12px;
    color: var(--muted);
    font-weight: 700;
}

.timeline-title {
    font-size: 17px;
    font-weight: 800;
    color: var(--text);
}


/* =========================================================
   FOOTER
   ========================================================= */

.footer {
    text-align: center;
    color: var(--muted) !important;
    font-size: 12px;
    margin-top: 55px;
    padding-top: 20px;
    border-top: 1px solid var(--border);
}


/* =========================================================
   BUTTONS
   ========================================================= */

.stButton > button {
    border-radius: 12px;
    font-weight: 700;
}


/* =========================================================
   DIVIDERS
   ========================================================= */

hr {
    border-color: var(--border) !important;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================

if "patient_id" not in st.session_state:
    st.session_state.patient_id = "AS-2026-0147"

if "recording_complete" not in st.session_state:
    st.session_state.recording_complete = False

if "analysis_generated" not in st.session_state:
    st.session_state.analysis_generated = False

if "current_page" not in st.session_state:
    st.session_state.current_page = "🏠 Overview"

if "profile_confirmed" not in st.session_state:
    st.session_state.profile_confirmed = False

if "previous_data_connected" not in st.session_state:
    st.session_state.previous_data_connected = False

if "uploaded_reports" not in st.session_state:
    st.session_state.uploaded_reports = []

if "risk_score" not in st.session_state:
    st.session_state.risk_score = 67

if "joint_screened" not in st.session_state:
    st.session_state.joint_screened = "Knee"

# Patient identity/contact fields
for _key, _default in {
    "patient_name": "Ananya Sharma",
    "patient_age": 56,
    "patient_sex": "Female",
    "patient_location": "Assam, NER",
    "patient_occupation": "Agricultural worker",
    "patient_activity": "Moderate",
    "patient_phone": "",
    "patient_address": "",
}.items():
    if _key not in st.session_state:
        st.session_state[_key] = _default


# ============================================================
# SIMULATED DATA
# ============================================================

np.random.seed(42)

time = np.linspace(0, 10, 3000)

signal = (
    0.12 * np.sin(2 * np.pi * 4 * time)
    + 0.07 * np.sin(2 * np.pi * 12 * time)
    + 0.025 * np.random.randn(len(time))
)

for center in [2.1, 4.4, 6.2, 8.1]:
    signal += 0.45 * np.exp(-((time - center) / 0.025) ** 2)


# ============================================================
# RISK / REPORT HELPERS
# ============================================================

def risk_grade(score):
    if score < 40:
        return 1, "LOW", "Few OA-related risk markers detected."
    if score < 70:
        return 2, "MEDIUM", "Some OA-related risk markers detected."
    return 3, "HIGH", "More OA-related risk markers detected."


def scroll_to_top():
    # The AI page contains Plotly charts that can finish rendering after the
    # first DOM pass. Keep forcing the main scroll containers to the top while
    # Streamlit and Plotly settle, then stop.
    components.html("""
        <script>
        (function () {
            const w = window.parent;
            const d = w.document;
            try { w.history.scrollRestoration = 'manual'; } catch (e) {}

            function topNow() {
                try {
                    const targets = [
                        w, d.documentElement, d.body,
                        d.querySelector('[data-testid="stAppViewContainer"]'),
                        d.querySelector('[data-testid="stMain"]'),
                        d.querySelector('[data-testid="stMainBlockContainer"]'),
                        d.querySelector('section.main'),
                        d.querySelector('main')
                    ].filter(Boolean);
                    targets.forEach(function(el) {
                        if (el === w) {
                            el.scrollTo(0, 0);
                        } else {
                            el.scrollTop = 0;
                            if (typeof el.scrollTo === 'function') el.scrollTo({top: 0, left: 0, behavior: 'auto'});
                        }
                    });
                    const first = d.querySelector('[data-testid="stMainBlockContainer"]');
                    if (first && typeof first.scrollIntoView === 'function') {
                        first.scrollIntoView({block: 'start', inline: 'nearest', behavior: 'auto'});
                    }
                } catch (e) {}
            }

            topNow();
            let n = 0;
            const timer = setInterval(function () {
                topNow();
                n += 1;
                if (n >= 45) clearInterval(timer);
            }, 100);
            [0, 50, 150, 300, 600, 1000, 1600, 2400, 3500].forEach(function(ms) {
                setTimeout(topNow, ms);
            });
        })();
        </script>
    """, height=0)

def go_next(target):
    st.session_state.current_page = target
    st.session_state._scroll_to_top = True
    st.rerun()


def next_button(target, label="NEXT →"):
    st.markdown("<div class='next-row'></div>", unsafe_allow_html=True)
    if st.button(t(label), type="primary", use_container_width=True):
        go_next(target)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def page_header(title, subtitle):

    title = t(title)
    subtitle = t(subtitle)

    col1, col2 = st.columns([5, 1])

    with col1:

        render_markdown(
            f"""
            <div class="hero-title">{title}</div>
            <div class="hero-subtitle">{subtitle}</div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        logo_path = LOGO_PATH

        if logo_path.exists():
            st.image(str(logo_path), width=120)

    render_markdown("---")


def metric_card(label, value, small=""):

    label = t(label)
    value = t(value) if isinstance(value, str) else value
    small = t(small)

    render_markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-small">{small}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def acoustic_waveform(height=320):

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=time,
            y=signal,
            mode="lines",
            name=t("Knee Joint Signal"),
            line=dict(width=1.4)
        )
    )

    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=30, b=20),
        template="plotly_white",
        xaxis_title=t("Time (seconds)"),
        yaxis_title=t("Amplitude"),
        hovermode="x unified"
    )

    return fig


def create_spectrogram():

    frequencies = np.linspace(100, 8000, 90)
    times = np.linspace(0, 10, 130)

    Z = np.random.rand(
        len(frequencies),
        len(times)
    ) * 0.12

    for event in [2.1, 4.4, 6.2, 8.1]:

        idx = np.argmin(abs(times - event))

        Z[
            :,
            max(0, idx - 2):min(len(times), idx + 3)
        ] += np.random.rand(
            len(frequencies),
            min(5, len(times))
        ) * 0.55

    fig = go.Figure(
        data=go.Heatmap(
            x=times,
            y=frequencies,
            z=Z,
            colorscale="Viridis"
        )
    )

    fig.update_layout(
        height=350,
        template="plotly_white",
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis_title=t("Time (seconds)"),
        yaxis_title=t("Frequency (Hz)")
    )

    return fig


def _report_font_paths(lang):
    """Find bundled Indic fonts first, then common OS font locations."""
    font_dir = BASE_DIR / "Assets" / "fonts"
    candidates = {
        "hi": ("NotoSansDevanagari-Regular.ttf", "NotoSansDevanagari-Bold.ttf"),
        "ne": ("NotoSansDevanagari-Regular.ttf", "NotoSansDevanagari-Bold.ttf"),
        "as": ("NotoSansBengali-Regular.ttf", "NotoSansBengali-Bold.ttf"),
        "bn": ("NotoSansBengali-Regular.ttf", "NotoSansBengali-Bold.ttf"),
    }
    if lang not in candidates:
        return None, None

    regular_name, bold_name = candidates[lang]
    search_roots = [
        font_dir,
        Path("/usr/share/fonts/truetype/noto"),
        Path("/usr/share/fonts/truetype/lohit-bengali"),
        Path("/usr/share/fonts/truetype/lohit-devanagari"),
        Path("C:/Windows/Fonts"),
    ]

    regular = next((root / regular_name for root in search_roots if (root / regular_name).exists()), None)
    bold = next((root / bold_name for root in search_roots if (root / bold_name).exists()), None)

    # Windows fallback fonts commonly available for Indic scripts.
    if regular is None:
        fallback_names = {
            "hi": ["Nirmala.ttf", "Mangal.ttf"],
            "ne": ["Nirmala.ttf", "Mangal.ttf"],
            "as": ["Nirmala.ttf", "Vrinda.ttf"],
            "bn": ["Nirmala.ttf", "Vrinda.ttf"],
        }[lang]
        for name in fallback_names:
            candidate = Path("C:/Windows/Fonts") / name
            if candidate.exists():
                regular = candidate
                break
    if bold is None:
        fallback_names = {
            "hi": ["NirmalaB.ttf", "Mangalb.ttf"],
            "ne": ["NirmalaB.ttf", "Mangalb.ttf"],
            "as": ["NirmalaB.ttf", "Vrindab.ttf"],
            "bn": ["NirmalaB.ttf", "Vrindab.ttf"],
        }[lang]
        for name in fallback_names:
            candidate = Path("C:/Windows/Fonts") / name
            if candidate.exists():
                bold = candidate
                break
    return regular, bold


def generate_pdf():
    """Generate a compact one-page predictive screening report in the selected UI language."""
    from reportlab.platypus import Image
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from xml.sax.saxutils import escape as xml_escape

    lang = current_language()
    score = int(st.session_state.risk_score)
    grade, level, simple_words = risk_grade(score)
    patient_id = st.session_state.patient_id
    report_date = datetime.now().strftime("%d %B %Y")
    data_quality = 94
    sound_events = 17
    uploaded_count = len(st.session_state.get("uploaded_reports", []))
    patient_name = st.session_state.get("patient_name", "Ananya Sharma")
    phone = st.session_state.get("patient_phone", "Not provided") or "Not provided"
    address = st.session_state.get("patient_address", "Not provided") or "Not provided"

    # Exact report-language phrases. Technical acronyms (OA, AI, PZT, IMU) and
    # the ArthroSonic brand remain unchanged intentionally.
    REPORT_TRANSLATIONS = {
        "hi": {
            "ARTHROSONIC":"ARTHROSONIC",
            "AI-Assisted Osteoarthritis (OA) Risk Screening":"AI-सहायित ऑस्टियोआर्थराइटिस (OA) जोखिम स्क्रीनिंग",
            "NORTH EASTERN REGION (NER), INDIA":"भारत का उत्तर-पूर्वी क्षेत्र (NER)",
            "OSTEOARTHRITIS RISK REPORT • PREDICTIVE SCREENING":"ऑस्टियोआर्थराइटिस जोखिम रिपोर्ट • पूर्वानुमानात्मक स्क्रीनिंग",
            "PREDICTIVE SCREENING REPORT":"पूर्वानुमानात्मक स्क्रीनिंग रिपोर्ट",
            "NOT A MEDICAL DIAGNOSIS":"चिकित्सीय निदान नहीं",
            "Patient & Report Details":"रोगी और रिपोर्ट विवरण",
            "Patient":"रोगी","Patient ID":"रोगी ID","Report Date":"रिपोर्ट तिथि","Phone":"फ़ोन","Address":"पता","Knee Screen":"घुटना स्क्रीन","Fixed — Knee":"निश्चित — घुटना","Screening Type":"स्क्रीनिंग प्रकार","Multimodal predictive risk screening":"मल्टीमॉडल पूर्वानुमानात्मक जोखिम स्क्रीनिंग","Status":"स्थिति","Preliminary":"प्रारंभिक","System":"सिस्टम","OA-NER v1.0":"OA-NER v1.0",
            "Predictive Screening Result":"पूर्वानुमानात्मक स्क्रीनिंग परिणाम","Few OA-associated risk markers were detected by the prototype model.":"प्रोटोटाइप मॉडल ने कुछ OA-संबंधित जोखिम संकेतक पाए।","Some OA-associated risk markers were detected by the prototype model.":"प्रोटोटाइप मॉडल ने कुछ OA-संबंधित जोखिम संकेतक पाए।","More OA-associated risk markers were detected by the prototype model.":"प्रोटोटाइप मॉडल ने अधिक OA-संबंधित जोखिम संकेतक पाए।","OA-associated predictive risk score":"OA-संबंधित पूर्वानुमानात्मक जोखिम स्कोर","Grade 1":"ग्रेड 1","Grade 2":"ग्रेड 2","Grade 3":"ग्रेड 3","LOW":"कम","MEDIUM":"मध्यम","HIGH":"उच्च","Risk Level":"जोखिम स्तर","Screening Interpretation":"स्क्रीनिंग व्याख्या","Few OA-associated risk markers detected.":"कुछ OA-संबंधित जोखिम संकेतक पाए गए।","Some OA-associated risk markers detected.":"कुछ OA-संबंधित जोखिम संकेतक पाए गए।","More OA-associated risk markers detected.":"अधिक OA-संबंधित जोखिम संकेतक पाए गए।",
            "Grades represent screening risk markers only. They do not confirm OA, quantify joint damage, or prescribe treatment. Grade boundaries are prototype values and require validation against reference data.":"ग्रेड केवल स्क्रीनिंग जोखिम संकेतकों को दर्शाते हैं। वे OA की पुष्टि, जोड़ की क्षति की मात्रा या उपचार निर्धारित नहीं करते। ग्रेड सीमाएँ प्रोटोटाइप मान हैं और संदर्भ डेटा के विरुद्ध सत्यापन आवश्यक है।",
            "What the System Found":"सिस्टम ने क्या पाया","SCREENING DETAIL":"स्क्रीनिंग विवरण","RESULT":"परिणाम","INTERPRETATION":"व्याख्या","OA-related risk markers":"OA-संबंधित जोखिम संकेतक","Data quality":"डेटा गुणवत्ता","Good":"अच्छी","Input capture quality for this prototype; not the probability of OA.":"इस प्रोटोटाइप के लिए इनपुट कैप्चर गुणवत्ता; यह OA की संभावना नहीं है।","Knee sound-pattern events":"घुटने की ध्वनि-पैटर्न घटनाएँ","Patterns detected during the controlled knee movement sequence.":"नियंत्रित घुटना गति अनुक्रम के दौरान पाए गए पैटर्न।","Movement profile":"गति प्रोफ़ाइल","Movement features contribute to the multimodal risk profile.":"गति विशेषताएँ मल्टीमॉडल जोखिम प्रोफ़ाइल में योगदान करती हैं।","Patient-reported inputs":"रोगी द्वारा बताए गए इनपुट","Symptoms are included as contextual model inputs.":"लक्षणों को संदर्भात्मक मॉडल इनपुट के रूप में शामिल किया गया है।",
            "Predictive Interpretation":"पूर्वानुमानात्मक व्याख्या","Grade 1 (Low Risk) indicates that the current multimodal input profile contains relatively few OA-associated risk markers.":"ग्रेड 1 (कम जोखिम) दर्शाता है कि वर्तमान मल्टीमॉडल इनपुट प्रोफ़ाइल में अपेक्षाकृत कम OA-संबंधित जोखिम संकेतक हैं।","Grade 2 (Medium Risk) indicates that the current multimodal input profile contains some OA-associated risk markers.":"ग्रेड 2 (मध्यम जोखिम) दर्शाता है कि वर्तमान मल्टीमॉडल इनपुट प्रोफ़ाइल में कुछ OA-संबंधित जोखिम संकेतक हैं।","Grade 3 (High Risk) indicates that the current multimodal input profile contains more OA-associated risk markers.":"ग्रेड 3 (उच्च जोखिम) दर्शाता है कि वर्तमान मल्टीमॉडल इनपुट प्रोफ़ाइल में अधिक OA-संबंधित जोखिम संकेतक हैं।","This is a predictive screening output, not a diagnosis or treatment recommendation.":"यह पूर्वानुमानात्मक स्क्रीनिंग आउटपुट है, निदान या उपचार की सिफारिश नहीं।",
            "Important Information":"महत्वपूर्ण जानकारी","Screening and demonstration only.":"केवल स्क्रीनिंग और प्रदर्शन के लिए।","ArthroSonic combines knee sound/vibration, movement/gait and patient-reported inputs to estimate OA-associated risk markers.":"ArthroSonic घुटने की ध्वनि/कंपन, गति/चाल और रोगी द्वारा बताए गए इनपुट को मिलाकर OA-संबंधित जोखिम संकेतकों का अनुमान लगाता है।","It is designed for preliminary predictive screening in the prototype and does not diagnose OA, prescribe treatment, or replace clinical assessment.":"इसे प्रोटोटाइप में प्रारंभिक पूर्वानुमानात्मक स्क्रीनिंग के लिए बनाया गया है और यह OA का निदान, उपचार निर्धारित या चिकित्सीय मूल्यांकन का स्थान नहीं लेता।","Generated by:":"द्वारा जनरेट किया गया:","Data status:":"डेटा स्थिति:","Simulated prototype data":"सिम्युलेटेड प्रोटोटाइप डेटा","supporting file(s) attached":"सहायक फ़ाइल संलग्न","— END OF REPORT —":"— रिपोर्ट समाप्त —"
        },
        "as": {}, "bn": {}, "ne": {}
    }

    # The remaining packs are explicit so the PDF never falls back to English.
    REPORT_TRANSLATIONS["as"] = {
        "ARTHROSONIC":"ARTHROSONIC","AI-Assisted Osteoarthritis (OA) Risk Screening":"AI-সহায়িত অষ্টিঅ’আৰ্থ্ৰাইটিছ (OA) ঝুঁকি স্ক্ৰিনিং","NORTH EASTERN REGION (NER), INDIA":"ভাৰতৰ উত্তৰ-পূৰ্বাঞ্চল (NER)","OSTEOARTHRITIS RISK REPORT • PREDICTIVE SCREENING":"অষ্টিঅ’আৰ্থ্ৰাইটিছ ঝুঁকি প্ৰতিবেদন • পূৰ্বানুমানমূলক স্ক্ৰিনিং","PREDICTIVE SCREENING REPORT":"পূৰ্বানুমানমূলক স্ক্ৰিনিং প্ৰতিবেদন","NOT A MEDICAL DIAGNOSIS":"চিকিৎসাগত নিৰ্ণয় নহয়","Patient & Report Details":"ৰোগী আৰু প্ৰতিবেদনৰ বিৱৰণ","Patient":"ৰোগী","Patient ID":"ৰোগী ID","Report Date":"প্ৰতিবেদনৰ তাৰিখ","Phone":"ফোন","Address":"ঠিকনা","Knee Screen":"আঁঠু স্ক্ৰিন","Fixed — Knee":"নিৰ্দিষ্ট — আঁঠু","Screening Type":"স্ক্ৰিনিংৰ ধৰণ","Multimodal predictive risk screening":"মাল্টিম’ডেল পূৰ্বানুমানমূলক ঝুঁকি স্ক্ৰিনিং","Status":"স্থিতি","Preliminary":"প্ৰাথমিক","System":"চিষ্টেম","Predictive Screening Result":"পূৰ্বানুমানমূলক স্ক্ৰিনিং ফলাফল","Few OA-associated risk markers were detected by the prototype model.":"প্ৰ’টোটাইপ মডেলে কম OA-সম্পৰ্কীয় ঝুঁকি সূচক ধৰা পেলালে।","Some OA-associated risk markers were detected by the prototype model.":"প্ৰ’টোটাইপ মডেলে কিছুমান OA-সম্পৰ্কীয় ঝুঁকি সূচক ধৰা পেলালে।","More OA-associated risk markers were detected by the prototype model.":"প্ৰ’টোটাইপ মডেলে অধিক OA-সম্পৰ্কীয় ঝুঁকি সূচক ধৰা পেলালে।","OA-associated predictive risk score":"OA-সম্পৰ্কীয় পূৰ্বানুমানমূলক ঝুঁকি স্ক’ৰ","Grade 1":"গ্ৰেড 1","Grade 2":"গ্ৰেড 2","Grade 3":"গ্ৰেড 3","LOW":"কম","MEDIUM":"মধ্যম","HIGH":"উচ্চ","Risk Level":"ঝুঁকিৰ স্তৰ","Screening Interpretation":"স্ক্ৰিনিং ব্যাখ্যা","Few OA-associated risk markers detected.":"কম OA-সম্পৰ্কীয় ঝুঁকি সূচক ধৰা পৰিছে।","Some OA-associated risk markers detected.":"কিছুমান OA-সম্পৰ্কীয় ঝুঁকি সূচক ধৰা পৰিছে।","More OA-associated risk markers detected.":"অধিক OA-সম্পৰ্কীয় ঝুঁকি সূচক ধৰা পৰিছে।","Grades represent screening risk markers only. They do not confirm OA, quantify joint damage, or prescribe treatment. Grade boundaries are prototype values and require validation against reference data.":"গ্ৰেডে কেৱল স্ক্ৰিনিং ঝুঁকি সূচক বুজায়। ই OA নিশ্চিত নকৰে, জইণ্টৰ ক্ষতিৰ পৰিমাণ নেদেখুৱায় বা চিকিৎসা নিৰ্ধাৰণ নকৰে। গ্ৰেডৰ সীমা প্ৰ’টোটাইপ মান আৰু তথ্যৰ সৈতে বৈধতা পৰীক্ষা কৰিব লাগিব।","What the System Found":"চিষ্টেমে কি পাইছে","SCREENING DETAIL":"স্ক্ৰিনিং বিৱৰণ","RESULT":"ফলাফল","INTERPRETATION":"ব্যাখ্যা","OA-related risk markers":"OA-সম্পৰ্কীয় ঝুঁকি সূচক","Data quality":"তথ্যৰ গুণমান","Good":"ভাল","Input capture quality for this prototype; not the probability of OA.":"এই প্ৰ’টোটাইপৰ ইনপুট কেপচাৰৰ গুণমান; ই OA-ৰ সম্ভাৱনা নহয়।","Knee sound-pattern events":"আঁঠুৰ শব্দ-পেটাৰ্ণ ঘটনা","Patterns detected during the controlled knee movement sequence.":"নিয়ন্ত্ৰিত আঁঠুৰ চলাচল ক্ৰমত ধৰা পৰা পেটাৰ্ণ।","Movement profile":"চলাচল প্ৰ’ফাইল","Movement features contribute to the multimodal risk profile.":"চলাচলৰ বৈশিষ্ট্যই মাল্টিম’ডেল ঝুঁকি প্ৰ’ফাইলত অৰিহণা যোগায়।","Patient-reported inputs":"ৰোগীয়ে জনোৱা ইনপুট","Symptoms are included as contextual model inputs.":"লক্ষণসমূহক প্ৰাসংগিক মডেল ইনপুট হিচাপে অন্তৰ্ভুক্ত কৰা হৈছে।","Predictive Interpretation":"পূৰ্বানুমানমূলক ব্যাখ্যা","Grade 1 (Low Risk) indicates that the current multimodal input profile contains relatively few OA-associated risk markers.":"গ্ৰেড 1 (কম ঝুঁকি)য়ে বৰ্তমানৰ মাল্টিম’ডেল ইনপুট প্ৰ’ফাইলত তুলনামূলকভাৱে কম OA-সম্পৰ্কীয় ঝুঁকি সূচক থকা বুজায়।","Grade 2 (Medium Risk) indicates that the current multimodal input profile contains some OA-associated risk markers.":"গ্ৰেড 2 (মধ্যম ঝুঁকি)য়ে বৰ্তমানৰ মাল্টিম’ডেল ইনপুট প্ৰ’ফাইলত কিছুমান OA-সম্পৰ্কীয় ঝুঁকি সূচক থকা বুজায়।","Grade 3 (High Risk) indicates that the current multimodal input profile contains more OA-associated risk markers.":"গ্ৰেড 3 (উচ্চ ঝুঁকি)য়ে বৰ্তমানৰ মাল্টিম’ডেল ইনপুট প্ৰ’ফাইলত অধিক OA-সম্পৰ্কীয় ঝুঁকি সূচক থকা বুজায়।","This is a predictive screening output, not a diagnosis or treatment recommendation.":"এইটো পূৰ্বানুমানমূলক স্ক্ৰিনিং ফলাফল, নিৰ্ণয় বা চিকিৎসাৰ পৰামৰ্শ নহয়।","Important Information":"গুৰুত্বপূৰ্ণ তথ্য","Screening and demonstration only.":"কেৱল স্ক্ৰিনিং আৰু প্ৰদৰ্শনৰ বাবে।","ArthroSonic combines knee sound/vibration, movement/gait and patient-reported inputs to estimate OA-associated risk markers.":"ArthroSonic-এ আঁঠুৰ শব্দ/কম্পন, চলাচল/গেইট আৰু ৰোগীয়ে জনোৱা ইনপুট একত্ৰ কৰি OA-সম্পৰ্কীয় ঝুঁকি সূচকৰ অনুমান কৰে।","It is designed for preliminary predictive screening in the prototype and does not diagnose OA, prescribe treatment, or replace clinical assessment.":"ই প্ৰ’টোটাইপত প্ৰাথমিক পূৰ্বানুমানমূলক স্ক্ৰিনিঙৰ বাবে ডিজাইন কৰা হৈছে আৰু OA নিৰ্ণয় নকৰে, চিকিৎসা নিৰ্ধাৰণ নকৰে বা চিকিৎসাগত মূল্যায়নৰ বিকল্প নহয়।","Generated by:":"উৎপন্ন কৰিছে:","Data status:":"তথ্যৰ স্থিতি:","Simulated prototype data":"চিমুলেটেড প্ৰ’টোটাইপ তথ্য","supporting file(s) attached":"সহায়ক ফাইল সংলগ্ন","— END OF REPORT —":"— প্ৰতিবেদন সমাপ্ত —"
    }
    REPORT_TRANSLATIONS["bn"] = {
        "ARTHROSONIC":"ARTHROSONIC","AI-Assisted Osteoarthritis (OA) Risk Screening":"AI-সহায়িত অস্টিওআর্থ্রাইটিস (OA) ঝুঁকি স্ক্রিনিং","NORTH EASTERN REGION (NER), INDIA":"ভারতের উত্তর-পূর্বাঞ্চল (NER)","OSTEOARTHRITIS RISK REPORT • PREDICTIVE SCREENING":"অস্টিওআর্থ্রাইটিস ঝুঁকি রিপোর্ট • পূর্বাভাসমূলক স্ক্রিনিং","PREDICTIVE SCREENING REPORT":"পূর্বাভাসমূলক স্ক্রিনিং রিপোর্ট","NOT A MEDICAL DIAGNOSIS":"চিকিৎসাগত রোগনির্ণয় নয়","Patient & Report Details":"রোগী ও রিপোর্টের বিবরণ","Patient":"রোগী","Patient ID":"রোগী ID","Report Date":"রিপোর্টের তারিখ","Phone":"ফোন","Address":"ঠিকানা","Knee Screen":"হাঁটু স্ক্রিন","Fixed — Knee":"নির্দিষ্ট — হাঁটু","Screening Type":"স্ক্রিনিংয়ের ধরন","Multimodal predictive risk screening":"মাল্টিমোডাল পূর্বাভাসমূলক ঝুঁকি স্ক্রিনিং","Status":"অবস্থা","Preliminary":"প্রাথমিক","System":"সিস্টেম","Predictive Screening Result":"পূর্বাভাসমূলক স্ক্রিনিং ফলাফল","Few OA-associated risk markers were detected by the prototype model.":"প্রোটোটাইপ মডেল কয়েকটি OA-সম্পর্কিত ঝুঁকি সূচক শনাক্ত করেছে।","Some OA-associated risk markers were detected by the prototype model.":"প্রোটোটাইপ মডেল কিছু OA-সম্পর্কিত ঝুঁকি সূচক শনাক্ত করেছে।","More OA-associated risk markers were detected by the prototype model.":"প্রোটোটাইপ মডেল আরও বেশি OA-সম্পর্কিত ঝুঁকি সূচক শনাক্ত করেছে।","OA-associated predictive risk score":"OA-সম্পর্কিত পূর্বাভাসমূলক ঝুঁকি স্কোর","Grade 1":"গ্রেড 1","Grade 2":"গ্রেড 2","Grade 3":"গ্রেড 3","LOW":"কম","MEDIUM":"মাঝারি","HIGH":"উচ্চ","Risk Level":"ঝুঁকির স্তর","Screening Interpretation":"স্ক্রিনিং ব্যাখ্যা","Few OA-associated risk markers detected.":"কয়েকটি OA-সম্পর্কিত ঝুঁকি সূচক শনাক্ত হয়েছে।","Some OA-associated risk markers detected.":"কিছু OA-সম্পর্কিত ঝুঁকি সূচক শনাক্ত হয়েছে।","More OA-associated risk markers detected.":"আরও বেশি OA-সম্পর্কিত ঝুঁকি সূচক শনাক্ত হয়েছে।","Grades represent screening risk markers only. They do not confirm OA, quantify joint damage, or prescribe treatment. Grade boundaries are prototype values and require validation against reference data.":"গ্রেড শুধুমাত্র স্ক্রিনিং ঝুঁকি সূচক বোঝায়। এগুলো OA নিশ্চিত করে না, জয়েন্টের ক্ষতির পরিমাণ নির্ধারণ করে না বা চিকিৎসা নির্দেশ করে না। গ্রেডের সীমা প্রোটোটাইপ মান এবং রেফারেন্স ডেটার মাধ্যমে যাচাই করা প্রয়োজন।","What the System Found":"সিস্টেম কী পেয়েছে","SCREENING DETAIL":"স্ক্রিনিং বিবরণ","RESULT":"ফলাফল","INTERPRETATION":"ব্যাখ্যা","OA-related risk markers":"OA-সম্পর্কিত ঝুঁকি সূচক","Data quality":"ডেটার গুণমান","Good":"ভালো","Input capture quality for this prototype; not the probability of OA.":"এই প্রোটোটাইপের ইনপুট ক্যাপচার গুণমান; এটি OA-এর সম্ভাবনা নয়।","Knee sound-pattern events":"হাঁটুর শব্দ-প্যাটার্ন ঘটনা","Patterns detected during the controlled knee movement sequence.":"নিয়ন্ত্রিত হাঁটুর নড়াচড়ার ক্রমে শনাক্ত প্যাটার্ন।","Movement profile":"নড়াচড়ার প্রোফাইল","Movement features contribute to the multimodal risk profile.":"নড়াচড়ার বৈশিষ্ট্য মাল্টিমোডাল ঝুঁকি প্রোফাইলে অবদান রাখে।","Patient-reported inputs":"রোগীর জানানো ইনপুট","Symptoms are included as contextual model inputs.":"উপসর্গকে প্রাসঙ্গিক মডেল ইনপুট হিসেবে অন্তর্ভুক্ত করা হয়েছে।","Predictive Interpretation":"পূর্বাভাসমূলক ব্যাখ্যা","Grade 1 (Low Risk) indicates that the current multimodal input profile contains relatively few OA-associated risk markers.":"গ্রেড 1 (কম ঝুঁকি) বোঝায় যে বর্তমান মাল্টিমোডাল ইনপুট প্রোফাইলে তুলনামূলকভাবে কম OA-সম্পর্কিত ঝুঁকি সূচক রয়েছে।","Grade 2 (Medium Risk) indicates that the current multimodal input profile contains some OA-associated risk markers.":"গ্রেড 2 (মাঝারি ঝুঁকি) বোঝায় যে বর্তমান মাল্টিমোডাল ইনপুট প্রোফাইলে কিছু OA-সম্পর্কিত ঝুঁকি সূচক রয়েছে।","Grade 3 (High Risk) indicates that the current multimodal input profile contains more OA-associated risk markers.":"গ্রেড 3 (উচ্চ ঝুঁকি) বোঝায় যে বর্তমান মাল্টিমোডাল ইনপুট প্রোফাইলে আরও বেশি OA-সম্পর্কিত ঝুঁকি সূচক রয়েছে।","This is a predictive screening output, not a diagnosis or treatment recommendation.":"এটি পূর্বাভাসমূলক স্ক্রিনিং ফলাফল, রোগনির্ণয় বা চিকিৎসার পরামর্শ নয়।","Important Information":"গুরুত্বপূর্ণ তথ্য","Screening and demonstration only.":"শুধু স্ক্রিনিং ও প্রদর্শনের জন্য।","ArthroSonic combines knee sound/vibration, movement/gait and patient-reported inputs to estimate OA-associated risk markers.":"ArthroSonic হাঁটুর শব্দ/কম্পন, নড়াচড়া/গেইট এবং রোগীর জানানো ইনপুট একত্র করে OA-সম্পর্কিত ঝুঁকি সূচক অনুমান করে।","It is designed for preliminary predictive screening in the prototype and does not diagnose OA, prescribe treatment, or replace clinical assessment.":"এটি প্রোটোটাইপে প্রাথমিক পূর্বাভাসমূলক স্ক্রিনিংয়ের জন্য তৈরি এবং OA নির্ণয়, চিকিৎসা নির্দেশ বা ক্লিনিক্যাল মূল্যায়নের বিকল্প নয়।","Generated by:":"তৈরি করেছে:","Data status:":"ডেটার অবস্থা:","Simulated prototype data":"সিমুলেটেড প্রোটোটাইপ ডেটা","supporting file(s) attached":"সহায়ক ফাইল সংযুক্ত","— END OF REPORT —":"— রিপোর্ট সমাপ্ত —"
    }
    REPORT_TRANSLATIONS["ne"] = {
        "ARTHROSONIC":"ARTHROSONIC","AI-Assisted Osteoarthritis (OA) Risk Screening":"AI-सहायित ओस्टियोआर्थराइटिस (OA) जोखिम स्क्रिनिङ","NORTH EASTERN REGION (NER), INDIA":"भारतको उत्तर-पूर्वी क्षेत्र (NER)","OSTEOARTHRITIS RISK REPORT • PREDICTIVE SCREENING":"ओस्टियोआर्थराइटिस जोखिम रिपोर्ट • पूर्वानुमानात्मक स्क्रिनिङ","PREDICTIVE SCREENING REPORT":"पूर्वानुमानात्मक स्क्रिनिङ रिपोर्ट","NOT A MEDICAL DIAGNOSIS":"चिकित्सकीय निदान होइन","Patient & Report Details":"बिरामी र रिपोर्ट विवरण","Patient":"बिरामी","Patient ID":"बिरामी ID","Report Date":"रिपोर्ट मिति","Phone":"फोन","Address":"ठेगाना","Knee Screen":"घुँडा स्क्रिन","Fixed — Knee":"निश्चित — घुँडा","Screening Type":"स्क्रिनिङ प्रकार","Multimodal predictive risk screening":"मल्टिमोडल पूर्वानुमानात्मक जोखिम स्क्रिनिङ","Status":"स्थिति","Preliminary":"प्रारम्भिक","System":"प्रणाली","Predictive Screening Result":"पूर्वानुमानात्मक स्क्रिनिङ परिणाम","Few OA-associated risk markers were detected by the prototype model.":"प्रोटोटाइप मोडेलले कम OA-सम्बन्धित जोखिम सूचकहरू पत्ता लगायो।","Some OA-associated risk markers were detected by the prototype model.":"प्रोटोटाइप मोडेलले केही OA-सम्बन्धित जोखिम सूचकहरू पत्ता लगायो।","More OA-associated risk markers were detected by the prototype model.":"प्रोटोटाइप मोडेलले बढी OA-सम्बन्धित जोखिम सूचकहरू पत्ता लगायो।","OA-associated predictive risk score":"OA-सम्बन्धित पूर्वानुमानात्मक जोखिम स्कोर","Grade 1":"ग्रेड 1","Grade 2":"ग्रेड 2","Grade 3":"ग्रेड 3","LOW":"कम","MEDIUM":"मध्यम","HIGH":"उच्च","Risk Level":"जोखिम स्तर","Screening Interpretation":"स्क्रिनिङ व्याख्या","Few OA-associated risk markers detected.":"केही OA-सम्बन्धित जोखिम सूचकहरू पत्ता लागे।","Some OA-associated risk markers detected.":"केही OA-सम्बन्धित जोखिम सूचकहरू पत्ता लागे।","More OA-associated risk markers detected.":"धेरै OA-सम्बन्धित जोखिम सूचकहरू पत्ता लागे।","Grades represent screening risk markers only. They do not confirm OA, quantify joint damage, or prescribe treatment. Grade boundaries are prototype values and require validation against reference data.":"ग्रेडले स्क्रिनिङ जोखिम सूचक मात्र जनाउँछन्। तिनले OA पुष्टि गर्दैनन्, जोइन्ट क्षतिको मात्रा निर्धारण गर्दैनन् वा उपचार तोक्दैनन्। ग्रेड सीमा प्रोटोटाइप मान हुन् र सन्दर्भ डेटासँग प्रमाणीकरण आवश्यक छ।","What the System Found":"प्रणालीले के पत्ता लगायो","SCREENING DETAIL":"स्क्रिनिङ विवरण","RESULT":"नतिजा","INTERPRETATION":"व्याख्या","OA-related risk markers":"OA-सम्बन्धित जोखिम सूचक","Data quality":"डेटा गुणस्तर","Good":"राम्रो","Input capture quality for this prototype; not the probability of OA.":"यस प्रोटोटाइपको इनपुट क्याप्चर गुणस्तर; यो OA को सम्भावना होइन।","Knee sound-pattern events":"घुँडाको ध्वनि-प्याटर्न घटनाहरू","Patterns detected during the controlled knee movement sequence.":"नियन्त्रित घुँडा चाल क्रमका क्रममा पत्ता लागेका प्याटर्नहरू।","Movement profile":"चाल प्रोफाइल","Movement features contribute to the multimodal risk profile.":"चालका विशेषताले मल्टिमोडल जोखिम प्रोफाइलमा योगदान गर्छन्।","Patient-reported inputs":"बिरामीले बताएका इनपुट","Symptoms are included as contextual model inputs.":"लक्षणलाई सन्दर्भगत मोडेल इनपुटका रूपमा समावेश गरिएको छ।","Predictive Interpretation":"पूर्वानुमानात्मक व्याख्या","Grade 1 (Low Risk) indicates that the current multimodal input profile contains relatively few OA-associated risk markers.":"ग्रेड 1 (कम जोखिम) ले हालको मल्टिमोडल इनपुट प्रोफाइलमा तुलनात्मक रूपमा कम OA-सम्बन्धित जोखिम सूचक रहेको जनाउँछ।","Grade 2 (Medium Risk) indicates that the current multimodal input profile contains some OA-associated risk markers.":"ग्रेड 2 (मध्यम जोखिम) ले हालको मल्टिमोडल इनपुट प्रोफाइलमा केही OA-सम्बन्धित जोखिम सूचक रहेको जनाउँछ।","Grade 3 (High Risk) indicates that the current multimodal input profile contains more OA-associated risk markers.":"ग्रेड 3 (उच्च जोखिम) ले हालको मल्टिमोडल इनपुट प्रोफाइलमा बढी OA-सम्बन्धित जोखिम सूचक रहेको जनाउँछ।","This is a predictive screening output, not a diagnosis or treatment recommendation.":"यो पूर्वानुमानात्मक स्क्रिनिङ परिणाम हो, निदान वा उपचारको सिफारिस होइन।","Important Information":"महत्त्वपूर्ण जानकारी","Screening and demonstration only.":"स्क्रिनिङ र प्रदर्शनका लागि मात्र।","ArthroSonic combines knee sound/vibration, movement/gait and patient-reported inputs to estimate OA-associated risk markers.":"ArthroSonic ले घुँडाको ध्वनि/कम्पन, चाल/गेट र बिरामीले बताएका इनपुट संयोजन गरी OA-सम्बन्धित जोखिम सूचक अनुमान गर्छ।","It is designed for preliminary predictive screening in the prototype and does not diagnose OA, prescribe treatment, or replace clinical assessment.":"यो प्रोटोटाइपमा प्रारम्भिक पूर्वानुमानात्मक स्क्रिनिङका लागि बनाइएको हो र यसले OA निदान, उपचार निर्धारण वा चिकित्सकीय मूल्याङ्कनको स्थान लिँदैन।","Generated by:":"उत्पन्नकर्ता:","Data status:":"डेटा स्थिति:","Simulated prototype data":"सिमुलेटेड प्रोटोटाइप डेटा","supporting file(s) attached":"सहायक फाइल संलग्न","— END OF REPORT —":"— रिपोर्ट समाप्त —"
    }

    REPORT_COMMON_EXTRA = {
        "hi": {"Grade Reference":"ग्रेड संदर्भ", "Grade":"ग्रेड", "Risk":"जोखिम", "Not provided":"उपलब्ध नहीं", "Medium":"मध्यम", "Pain":"दर्द", "Stiffness":"जकड़न", "symmetry":"समरूपता", "108° ROM • 81% symmetry":"108° गति सीमा • 81% समरूपता", "Pain 6/10 • Stiffness 4/10":"दर्द 6/10 • जकड़न 4/10"},
        "as": {"Grade Reference":"গ্ৰেডৰ সন্দৰ্ভ", "Grade":"গ্ৰেড", "Risk":"ঝুঁকি", "Not provided":"উপলব্ধ নহয়", "Medium":"মধ্যম", "Pain":"বিষ", "Stiffness":"জড়তা", "symmetry":"সমমিতি", "108° ROM • 81% symmetry":"108° গতি পৰিসৰ • 81% সমমিতি", "Pain 6/10 • Stiffness 4/10":"বিষ 6/10 • জড়তা 4/10"},
        "bn": {"Grade Reference":"গ্রেডের রেফারেন্স", "Grade":"গ্রেড", "Risk":"ঝুঁকি", "Not provided":"দেওয়া হয়নি", "Medium":"মাঝারি", "Pain":"ব্যথা", "Stiffness":"জড়তা", "symmetry":"সমতা", "108° ROM • 81% symmetry":"108° গতি পরিসর • 81% সমতা", "Pain 6/10 • Stiffness 4/10":"ব্যথা 6/10 • জড়তা 4/10"},
        "ne": {"Grade Reference":"ग्रेड सन्दर्भ", "Grade":"ग्रेड", "Risk":"जोखिम", "Not provided":"उपलब्ध छैन", "Medium":"मध्यम", "Pain":"दुखाइ", "Stiffness":"कडापन", "symmetry":"सममिति", "108° ROM • 81% symmetry":"108° गति दायरा • 81% सममिति", "Pain 6/10 • Stiffness 4/10":"दुखाइ 6/10 • कडापन 4/10"}
    }
    for _lang, _pack in REPORT_COMMON_EXTRA.items():
        REPORT_TRANSLATIONS.setdefault(_lang, {}).update(_pack)

    def rt(text):
        return REPORT_TRANSLATIONS.get(lang, {}).get(text, t(text))

    # Date is translated through the language pack where possible.
    month_map = {
        "hi": {"January":"जनवरी","February":"फ़रवरी","March":"मार्च","April":"अप्रैल","May":"मई","June":"जून","July":"जुलाई","August":"अगस्त","September":"सितंबर","October":"अक्टूबर","November":"नवंबर","December":"दिसंबर"},
        "as": {"January":"জানুৱাৰী","February":"ফেব্ৰুৱাৰী","March":"মাৰ্চ","April":"এপ্ৰিল","May":"মে","June":"জুন","July":"জুলাই","August":"আগষ্ট","September":"ছেপ্টেম্বৰ","October":"অক্টোবৰ","November":"নৱেম্বৰ","December":"ডিচেম্বৰ"},
        "bn": {"January":"জানুয়ারি","February":"ফেব্রুয়ারি","March":"মার্চ","April":"এপ্রিল","May":"মে","June":"জুন","July":"জুলাই","August":"আগস্ট","September":"সেপ্টেম্বর","October":"অক্টোবর","November":"নভেম্বর","December":"ডিসেম্বর"},
        "ne": {"January":"जनवरी","February":"फेब्रुअरी","March":"मार्च","April":"अप्रिल","May":"मे","June":"जुन","July":"जुलाई","August":"अगस्ट","September":"सेप्टेम्बर","October":"अक्टोबर","November":"नोभेम्बर","December":"डिसेम्बर"}
    }
    report_date = datetime.now().strftime("%d %B %Y")
    if lang in month_map:
        for en_month, local_month in month_map[lang].items():
            report_date = report_date.replace(en_month, local_month)

    # For Indic scripts, render the report page with Pillow + Noto Sans using
    # RAQM shaping, then package that page with ReportLab. This avoids the
    # broken glyph/combining-mark rendering produced by ReportLab Paragraphs.
    if lang != "en":
        from PIL import Image as PILImage, ImageDraw, ImageFont, features as PILFeatures
        from reportlab.platypus import Image as RLImage
        HAS_RAQM = bool(PILFeatures.check("raqm"))

        W, H = 1240, 1754
        canvas_img = PILImage.new("RGB", (W, H), "white")
        draw = ImageDraw.Draw(canvas_img)
        script_lang = "bn" if lang in ("as", "bn") else "hi"

        def _mixed_width(text, indic_font):
            total = 0
            for chunk in re.findall(r"[A-Za-z0-9][A-Za-z0-9 .,:;!?/()\-+%°•|]*|[^A-Za-z0-9]+", str(text)):
                use_font = (f_title_l if id(indic_font) in bold_indic_fonts and indic_font == f_title else
                            f_section_l if id(indic_font) in bold_indic_fonts and indic_font == f_section else
                            f_body_bold_l if id(indic_font) in bold_indic_fonts and indic_font == f_body_bold else
                            f_table_head_l if id(indic_font) in bold_indic_fonts and indic_font == f_table_head else
                            f_score_l if id(indic_font) in bold_indic_fonts and indic_font == f_score else f_small_l if indic_font == f_small else f_body_l)
                if re.fullmatch(r"[A-Za-z0-9 .,:;!?/()\-+%°•|]+", chunk):
                    total += draw.textlength(chunk, font=use_font)
                else:
                    total += draw.textlength(chunk, font=indic_font, **({"language": script_lang} if HAS_RAQM else {}))
            return total

        def put_text(xy, text, font=None, fill=None, **kwargs):
            x, y0 = xy
            is_bold = id(font) in bold_indic_fonts
            if font == f_title: latin_font = f_title_l
            elif font == f_section: latin_font = f_section_l
            elif font == f_body_bold: latin_font = f_body_bold_l
            elif font == f_table_head: latin_font = f_table_head_l
            elif font == f_score: latin_font = f_score_l
            elif font == f_sub: latin_font = f_sub_l
            elif font == f_small: latin_font = f_small_l
            else: latin_font = f_body_l
            for chunk in re.findall(r"[A-Za-z0-9][A-Za-z0-9 .,:;!?/()\-+%°•|]*|[^A-Za-z0-9]+", str(text)):
                use_font = latin_font if re.fullmatch(r"[A-Za-z0-9 .,:;!?/()\-+%°•|]+", chunk) else font
                use_kwargs = dict(kwargs)
                if use_font == font:
                    if HAS_RAQM:
                        use_kwargs["language"] = script_lang
                draw.text((x, y0), chunk, font=use_font, fill=fill, **use_kwargs)
                x += (draw.textlength(chunk, font=use_font, **({"language": script_lang} if HAS_RAQM else {})) if use_font == font else draw.textlength(chunk, font=use_font))

        font_dir = BASE_DIR / "Assets" / "fonts"
        if lang in ("hi", "ne"):
            reg_file = font_dir / "NotoSansDevanagari-Regular.ttf"
            bold_file = font_dir / "NotoSansDevanagari-Bold.ttf"
        else:
            reg_file = font_dir / "NotoSansBengali-Regular.ttf"
            bold_file = font_dir / "NotoSansBengali-Bold.ttf"
        if not reg_file.exists():
            reg_file = _report_font_paths(lang)[0]
        if not bold_file.exists():
            bold_file = _report_font_paths(lang)[1] or reg_file

        latin_reg_file = font_dir / "NotoSans-Regular.ttf"
        latin_bold_file = font_dir / "NotoSans-Bold.ttf"
       

        f_title = ImageFont.truetype(str(bold_file), 31)
        f_sub = ImageFont.truetype(str(reg_file), 16)
        f_section = ImageFont.truetype(str(bold_file), 20)
        f_body = ImageFont.truetype(str(reg_file), 14)
        f_body_bold = ImageFont.truetype(str(bold_file), 14)
        f_small = ImageFont.truetype(str(reg_file), 11)
        f_table_head = ImageFont.truetype(str(bold_file), 13)
        f_score = ImageFont.truetype(str(bold_file), 30)
        f_title_l = ImageFont.truetype(str(latin_bold_file), 31)
        f_sub_l = ImageFont.truetype(str(latin_reg_file), 16)
        f_section_l = ImageFont.truetype(str(latin_bold_file), 20)
        f_body_l = ImageFont.truetype(str(latin_reg_file), 14)
        f_body_bold_l = ImageFont.truetype(str(latin_bold_file), 14)
        f_small_l = ImageFont.truetype(str(latin_reg_file), 11)
        f_table_head_l = ImageFont.truetype(str(latin_bold_file), 13)
        f_score_l = ImageFont.truetype(str(latin_bold_file), 30)
        bold_indic_fonts = {id(f_title), id(f_section), id(f_body_bold), id(f_table_head), id(f_score)}

        navy_rgb = (23, 61, 85)
        muted_rgb = (102, 122, 137)
        grid_rgb = (215, 222, 227)
        pale_blue_rgb = (234, 246, 246)
        pale_yellow_rgb = (255, 242, 210)
        pale_green_rgb = (234, 246, 236)
        pale_red_rgb = (251, 232, 232)
        margin = 58
        content_w = W - 2 * margin
        y = 42

        def wrap(text, font, max_width):
            words = str(text).split()
            lines, current = [], ""
            for word in words:
                test = word if not current else current + " " + word
                if _mixed_width(test, font) <= max_width:
                    current = test
                else:
                    if current:
                        lines.append(current)
                    current = word
            if current:
                lines.append(current)
            return lines or [""]

        def text_block(text, font, x, y0, max_width, fill=navy_rgb, line_gap=5):
            lines = wrap(text, font, max_width)
            line_h = int(font.size * 1.28)
            for line in lines:
                put_text((x, y0), line, font=font, fill=fill)
                y0 += line_h + line_gap
            return y0

        # Header
        title_x = margin
        if LOGO_PATH.exists():
            try:
                logo_img = PILImage.open(LOGO_PATH).convert("RGBA")
                logo_img.thumbnail((92, 92))
                canvas_img.paste(logo_img, (margin, y), logo_img)
                title_x = margin + 108
            except Exception:
                pass
        put_text((title_x, y), rt("ARTHROSONIC"), font=f_title, fill=navy_rgb)
        put_text((title_x, y + 42), rt("AI-Assisted Osteoarthritis (OA) Risk Screening"), font=f_sub, fill=muted_rgb)
        put_text((title_x, y + 66), rt("NORTH EASTERN REGION (NER), INDIA"), font=f_sub, fill=muted_rgb)
        put_text((title_x, y + 89), rt("OSTEOARTHRITIS RISK REPORT • PREDICTIVE SCREENING"), font=f_sub, fill=muted_rgb)
        y += 124
        draw.line((margin, y, W - margin, y), fill=grid_rgb, width=1); y += 18

        def section_title(num, key):
            nonlocal y
            put_text((margin, y), f"{num}. {rt(key)}", font=f_section, fill=navy_rgb); y += 34

        def table(rows, col_widths, row_heights, header=False):
            nonlocal y
            x0 = margin
            for r_idx, row in enumerate(rows):
                rh = row_heights[r_idx] if r_idx < len(row_heights) else 36
                x = x0
                for c_idx, cell in enumerate(row):
                    cw = col_widths[c_idx]
                    is_header = header and r_idx == 0
                    fill = navy_rgb if is_header else (242,245,246) if r_idx == 0 and not header else (255,255,255)
                    draw.rectangle((x, y, x+cw, y+rh), fill=fill, outline=grid_rgb, width=1)
                    font = f_table_head if is_header else f_body
                    color = "white" if is_header else navy_rgb
                    lines = wrap(cell, font, cw-14)
                    line_h = int(font.size * 1.25)
                    ty = y + max(4, (rh - len(lines)*line_h)//2)
                    for line in lines[:max(1, rh//line_h)]:
                        put_text((x+7, ty), line, font=font, fill=color)
                        ty += line_h
                    x += cw
                y += rh

        section_title(1, "Patient & Report Details")
        table([[rt("Patient"), patient_name, rt("Patient ID"), patient_id, rt("Report Date"), report_date],
               [rt("Phone"), rt("Not provided") if phone == "Not provided" else phone, rt("Address"), rt("Not provided") if address == "Not provided" else address, rt("Knee Screen"), rt("Fixed — Knee")],
               [rt("Screening Type"), rt("Multimodal predictive risk screening"), rt("Status"), rt("Preliminary"), rt("System"), "OA-NER v1.0"]],
              [78,184,88,174,92,156], [42,42,52])
        y += 12

        section_title(2, "Predictive Screening Result")
        box_h = 76; box_color = pale_yellow_rgb if grade == 2 else (pale_green_rgb if grade == 1 else pale_red_rgb)
        draw.rounded_rectangle((margin, y, W-margin, y+box_h), radius=10, fill=box_color, outline=(229,167,45), width=2)
        put_text((margin+16, y+14), f"{rt('Grade ' + str(grade))} — {rt(level)} {rt('Risk')}", font=f_body_bold, fill=navy_rgb)
        put_text((W-margin-215, y+8), f"{score} / 100", font=f_score, fill=navy_rgb)
        put_text((margin+16, y+48), rt("OA-associated predictive risk score"), font=f_small, fill=muted_rgb)
        result_key = {1:"Few OA-associated risk markers were detected by the prototype model.",2:"Some OA-associated risk markers were detected by the prototype model.",3:"More OA-associated risk markers were detected by the prototype model."}[grade]
        result_lines = wrap(rt(result_key), f_small, 320)
        for i,line in enumerate(result_lines[:2]): put_text((margin+360, y+44+i*15), line, font=f_small, fill=navy_rgb)
        y += box_h + 12

        section_title(3, "Grade Reference")
        table([[rt("Grade"), rt("Risk Level"), rt("Screening Interpretation")],
               [rt("Grade 1"), rt("LOW"), rt("Few OA-associated risk markers detected.")],
               [rt("Grade 2"), rt("MEDIUM"), rt("Some OA-associated risk markers detected.")],
               [rt("Grade 3"), rt("HIGH"), rt("More OA-associated risk markers detected.")]],
              [110,120,430], [34,34,34,34], header=True)
        y += 8
        y = text_block(rt("Grades represent screening risk markers only. They do not confirm OA, quantify joint damage, or prescribe treatment. Grade boundaries are prototype values and require validation against reference data."), f_small, margin, y, content_w, muted_rgb, 2) + 6

        section_title(4, "What the System Found")
        table([[rt("SCREENING DETAIL"), rt("RESULT"), rt("INTERPRETATION")],
               [rt("OA-related risk markers"), rt(level), rt({1:"Few OA-associated risk markers detected.",2:"Some OA-associated risk markers detected.",3:"More OA-associated risk markers detected."}[grade])],
               [rt("Data quality"), f"{data_quality}% — {rt('Good')}", rt("Input capture quality for this prototype; not the probability of OA.")],
               [rt("Knee sound-pattern events"), str(sound_events), rt("Patterns detected during the controlled knee movement sequence.")],
               [rt("Movement profile"), rt("108° ROM • 81% symmetry"), rt("Movement features contribute to the multimodal risk profile.")],
               [rt("Patient-reported inputs"), rt("Pain 6/10 • Stiffness 4/10"), rt("Symptoms are included as contextual model inputs.")]],
              [190,150,320], [34,38,38,38,38,38], header=True)
        y += 10

        section_title(5, "Predictive Interpretation")
        meaning_key = {1:"Grade 1 (Low Risk) indicates that the current multimodal input profile contains relatively few OA-associated risk markers.",2:"Grade 2 (Medium Risk) indicates that the current multimodal input profile contains some OA-associated risk markers.",3:"Grade 3 (High Risk) indicates that the current multimodal input profile contains more OA-associated risk markers."}[grade]
        interp = rt(meaning_key) + " " + rt("This is a predictive screening output, not a diagnosis or treatment recommendation.")
        draw.rounded_rectangle((margin, y, W-margin, y+82), radius=8, fill=pale_blue_rgb, outline=(42,174,176), width=2)
        text_block(interp, f_body, margin+14, y+11, content_w-28, navy_rgb, 2); y += 94

        section_title(6, "Important Information")
        info = rt("Screening and demonstration only.") + " " + rt("ArthroSonic combines knee sound/vibration, movement/gait and patient-reported inputs to estimate OA-associated risk markers.") + " " + rt("It is designed for preliminary predictive screening in the prototype and does not diagnose OA, prescribe treatment, or replace clinical assessment.")
        info_h = 118
        draw.rounded_rectangle((margin, y, W-margin, y+info_h), radius=8, fill=(241,244,245), outline=grid_rgb, width=1)
        text_block(info, f_body, margin+14, y+12, content_w-28, navy_rgb, 3); y += info_h + 6
        status = rt("Simulated prototype data") + (f" • {uploaded_count} " + rt("supporting file(s) attached") if uploaded_count else "")
        put_text((margin, y), rt("Generated by:") + " ArthroSonic | " + rt("Data status:") + " " + status, font=f_small, fill=muted_rgb)
        put_text((W//2-80, y+24), rt("— END OF REPORT —"), font=f_small, fill=muted_rgb)

        draw.line((margin, H-55, W-margin, H-55), fill=grid_rgb, width=1)
        put_text((margin, H-40), rt("PREDICTIVE SCREENING REPORT") + " • " + rt("NOT A MEDICAL DIAGNOSIS"), font=f_small, fill=muted_rgb)
        page_label = {"hi":"पृष्ठ 1 में से 1", "as":"পৃষ্ঠা ১ৰ ১", "bn":"পৃষ্ঠা 1 / 1", "ne":"पृष्ठ 1 मध्ये 1"}.get(lang, "Page 1 of 1")
        put_text((W-margin-100, H-40), page_label, font=f_small, fill=muted_rgb)

        png = io.BytesIO(); canvas_img.save(png, format="PNG", optimize=True); png.seek(0)
        pdf_buffer = io.BytesIO()
        pdf_doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, rightMargin=0, leftMargin=0, topMargin=0, bottomMargin=0, title=rt("AI-Assisted Osteoarthritis (OA) Risk Screening"))
        pdf_doc.build([RLImage(png, width=A4[0]-12, height=A4[1]-12)])
        pdf_buffer.seek(0)
        return pdf_buffer

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4, rightMargin=42, leftMargin=42,
        topMargin=32, bottomMargin=38,
        title=rt("AI-Assisted Osteoarthritis (OA) Risk Screening")
    )

    navy = colors.HexColor("#173D55")
    muted = colors.HexColor("#667A89")
    teal = colors.HexColor("#2AAEB0")
    pale_blue = colors.HexColor("#EAF6F6")
    pale_yellow = colors.HexColor("#FFF2D2")
    pale_green = colors.HexColor("#EAF6EC")
    pale_red = colors.HexColor("#FBE8E8")
    grid = colors.HexColor("#D7DEE3")

    # Register the proper Indic font for the selected language. English keeps the
    # original compact serif styling; localized reports use Noto Sans for glyph coverage.
    font_regular = "Times-Roman"
    font_bold = "Times-Bold"
    regular_path, bold_path = _report_font_paths(lang)
    if lang != "en" and regular_path:
        try:
            pdfmetrics.registerFont(TTFont("ArthroLocal", str(regular_path)))
            font_regular = "ArthroLocal"
            if bold_path:
                pdfmetrics.registerFont(TTFont("ArthroLocalBold", str(bold_path)))
                font_bold = "ArthroLocalBold"
            else:
                font_bold = "ArthroLocal"
        except Exception:
            pass

    styles = getSampleStyleSheet()
    title = styles["Title"]; title.fontName = font_bold; title.fontSize = 18; title.leading = 20; title.textColor = navy; title.alignment = TA_CENTER
    subtitle = styles["Normal"]; subtitle.fontName = font_regular; subtitle.fontSize = 8.5; subtitle.leading = 10.5; subtitle.textColor = muted; subtitle.alignment = TA_CENTER
    section = styles["Heading2"]; section.fontName = font_bold; section.fontSize = 10.5; section.leading = 12; section.textColor = navy; section.spaceBefore = 5; section.spaceAfter = 5
    body = styles["BodyText"]; body.fontName = font_regular; body.fontSize = 8.2; body.leading = 10.2; body.textColor = navy
    small = styles["BodyText"]; small.fontName = font_regular; small.fontSize = 7.1; small.leading = 8.7; small.textColor = muted
    bold = styles["BodyText"]; bold.fontName = font_bold; bold.fontSize = 8.2; bold.leading = 10.2; bold.textColor = navy

    def P(txt, style=body):
        return Paragraph(str(txt), style)

    def header_footer(canvas, doc_obj):
        canvas.saveState(); w, h = A4
        canvas.setStrokeColor(grid); canvas.setLineWidth(0.5); canvas.line(42, 28, w - 42, 28)
        canvas.setFont(font_regular, 6.7); canvas.setFillColor(muted)
        canvas.drawString(42, 17, f"{rt('ARTHROSONIC')} • {rt('PREDICTIVE SCREENING REPORT')} • {rt('NOT A MEDICAL DIAGNOSIS')}")
        canvas.drawRightString(w - 42, 17, "Page 1 of 1" if lang == "en" else ("पृष्ठ 1 में से 1" if lang == "hi" else ("পৃষ্ঠা 1 / 1" if lang == "bn" else ("पृष्ठ १ मध्ये १" if lang == "as" else "पृष्ठ 1 मध्ये 1"))))
        canvas.restoreState()

    story = []
    logo_path = LOGO_PATH if LOGO_PATH.exists() else None
    if logo_path:
        logo = Image(str(logo_path), width=55, height=55)
        header_table = Table([[logo, [P(rt("ARTHROSONIC"), title), P(rt("AI-Assisted Osteoarthritis (OA) Risk Screening"), subtitle), P(rt("NORTH EASTERN REGION (NER), INDIA"), subtitle), P(rt("OSTEOARTHRITIS RISK REPORT • PREDICTIVE SCREENING"), subtitle)]]], colWidths=[65, 475])
        header_table.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "MIDDLE"), ("ALIGN", (1,0), (1,0), "CENTER"), ("LEFTPADDING", (0,0), (-1,-1), 0), ("RIGHTPADDING", (0,0), (-1,-1), 0), ("TOPPADDING", (0,0), (-1,-1), 0), ("BOTTOMPADDING", (0,0), (-1,-1), 0)]))
        story.append(header_table)
    else:
        story += [P(rt("ARTHROSONIC"), title), P(rt("AI-Assisted Osteoarthritis (OA) Risk Screening"), subtitle), P(rt("NORTH EASTERN REGION (NER), INDIA"), subtitle)]

    story.append(Spacer(1, 7)); story.append(P("1. " + rt("Patient & Report Details"), section))
    patient_rows = [
        [P("<b>" + rt("Patient") + "</b>"), P(patient_name), P("<b>" + rt("Patient ID") + "</b>"), P(patient_id), P("<b>" + rt("Report Date") + "</b>"), P(report_date)],
        [P("<b>" + rt("Phone") + "</b>"), P(phone), P("<b>" + rt("Address") + "</b>"), P(address), P("<b>" + rt("Knee Screen") + "</b>"), P(rt("Fixed — Knee"))],
        [P("<b>" + rt("Screening Type") + "</b>"), P(rt("Multimodal predictive risk screening")), P("<b>" + rt("Status") + "</b>"), P(rt("Preliminary")), P("<b>" + rt("System") + "</b>"), P(rt("OA-NER v1.0"))],
    ]
    t1 = Table(patient_rows, colWidths=[48,126,55,132,58,121], rowHeights=[23,28,24])
    t1.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.45,grid),("BACKGROUND",(0,0),(0,-1),colors.HexColor("#F2F5F6")),("BACKGROUND",(2,0),(2,-1),colors.HexColor("#F2F5F6")),("BACKGROUND",(4,0),(4,-1),colors.HexColor("#F2F5F6")),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5)])); story.append(t1)

    story.append(P("2. " + rt("Predictive Screening Result"), section))
    result_text_en = {1:"Few OA-associated risk markers were detected by the prototype model.",2:"Some OA-associated risk markers were detected by the prototype model.",3:"More OA-associated risk markers were detected by the prototype model."}[grade]
    result_box = Table([[P(f"<b>{rt('Grade ' + str(grade))} — {rt(level)} {rt('Risk')}</b>"), P(f"<b>{score} / 100</b>", title)],[P(rt("OA-associated predictive risk score"),small),P(rt(result_text_en))]],colWidths=[215,325],rowHeights=[29,29])
    result_box.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),pale_yellow if grade==2 else (pale_green if grade==1 else pale_red)),("BOX",(0,0),(-1,-1),0.8,colors.HexColor("#E5A72D")),("ALIGN",(1,0),(1,0),"CENTER"),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8)])); story.append(result_box)

    story.append(P("3. " + rt("Grade Reference"), section))
    grade_rows = [[P("<b>"+rt("Grade")+"</b>"),P("<b>"+rt("Risk Level")+"</b>"),P("<b>"+rt("Screening Interpretation")+"</b>")],[P("<b>"+rt("Grade 1")+"</b>"),P(rt("LOW")),P(rt("Few OA-associated risk markers detected."))],[P("<b>"+rt("Grade 2")+"</b>"),P(rt("MEDIUM")),P(rt("Some OA-associated risk markers detected."))],[P("<b>"+rt("Grade 3")+"</b>"),P(rt("HIGH")),P(rt("More OA-associated risk markers detected."))]]
    gt=Table(grade_rows,colWidths=[75,90,375],rowHeights=[19,21,21,21]); gt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),navy),("TEXTCOLOR",(0,0),(-1,0),colors.white),("BACKGROUND",(0,1),(-1,1),pale_green),("BACKGROUND",(0,2),(-1,2),pale_yellow),("BACKGROUND",(0,3),(-1,3),pale_red),("GRID",(0,0),(-1,-1),0.45,grid),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6)])); story.append(gt)
    story.append(Spacer(1,3)); story.append(P(rt("Grades represent screening risk markers only. They do not confirm OA, quantify joint damage, or prescribe treatment. Grade boundaries are prototype values and require validation against reference data."),small))

    story.append(P("4. " + rt("What the System Found"), section))
    detail_rows=[[P("<b>"+rt("SCREENING DETAIL")+"</b>"),P("<b>"+rt("RESULT")+"</b>"),P("<b>"+rt("INTERPRETATION")+"</b>")],[P(rt("OA-related risk markers")),P("<b>"+rt(level)+"</b>"),P(rt({1:"Few OA-associated risk markers detected.",2:"Some OA-associated risk markers detected.",3:"More OA-associated risk markers detected."}[grade]))],[P(rt("Data quality")),P(f"<b>{data_quality}% — {rt('Good')}</b>"),P(rt("Input capture quality for this prototype; not the probability of OA."))],[P(rt("Knee sound-pattern events")),P(f"<b>{sound_events}</b>"),P(rt("Patterns detected during the controlled knee movement sequence."))],[P(rt("Movement profile")),P(rt("108° ROM • 81% symmetry")),P(rt("Movement features contribute to the multimodal risk profile."))],[P(rt("Patient-reported inputs")),P(rt("Pain 6/10 • Stiffness 4/10")),P(rt("Symptoms are included as contextual model inputs."))]]
    dt=Table(detail_rows,colWidths=[150,130,260],rowHeights=[18,20,22,22,22,22]); dt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),navy),("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),0.45,grid),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6)])); story.append(dt)

    story.append(P("5. " + rt("Predictive Interpretation"), section))
    meaning_en={1:"Grade 1 (Low Risk) indicates that the current multimodal input profile contains relatively few OA-associated risk markers.",2:"Grade 2 (Medium Risk) indicates that the current multimodal input profile contains some OA-associated risk markers.",3:"Grade 3 (High Risk) indicates that the current multimodal input profile contains more OA-associated risk markers."}[grade]
    mt=Table([[P(rt(meaning_en)+" "+rt("This is a predictive screening output, not a diagnosis or treatment recommendation."))]],colWidths=[540]); mt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),pale_blue),("BOX",(0,0),(-1,-1),0.8,teal),("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7)])); story.append(mt)

    story.append(P("6. " + rt("Important Information"), section))
    info=rt("Screening and demonstration only.")+" "+rt("ArthroSonic combines knee sound/vibration, movement/gait and patient-reported inputs to estimate OA-associated risk markers.")+" "+rt("It is designed for preliminary predictive screening in the prototype and does not diagnose OA, prescribe treatment, or replace clinical assessment.")
    it=Table([[P(info)]],colWidths=[540]); it.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#F1F4F5")),("BOX",(0,0),(-1,-1),0.45,grid),("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)])); story.append(it)
    story.append(Spacer(1,4)); status=rt("Simulated prototype data") + (f" • {uploaded_count} " + rt("supporting file(s) attached") if uploaded_count else "")
    story.append(P(f"<b>{rt('Generated by:')}</b> ArthroSonic | <b>{rt('Data status:')}</b> {status}",small)); story.append(P(rt("— END OF REPORT —"),subtitle))

    doc.build(story,onFirstPage=header_footer); buffer.seek(0); return buffer


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    logo_path = LOGO_PATH

    if logo_path.exists():

        st.image(
            str(logo_path),
            use_container_width=True
        )

    else:

        render_markdown(
            "<div style='text-align:center;font-size:55px;'>🦴</div>",
            unsafe_allow_html=True
        )

    render_markdown(
        "<h2 style='text-align:center;'>ARTHROSONIC</h2>",
        unsafe_allow_html=True
    )

    st.caption(t("AI-Assisted Osteoarthritis Risk Screening"))

    language_names = list(LANGUAGES.keys())
    current_name = next((name for name, code in LANGUAGES.items() if code == current_language()), "English")
    chosen_name = st.selectbox(t("🌐 Language / भाषा"), language_names, index=language_names.index(current_name))
    chosen_code = LANGUAGES[chosen_name]
    if chosen_code != current_language():
        st.session_state.language = chosen_code
        st.session_state._scroll_to_top = True
        st.rerun()

    render_markdown("---")

    nav_options = [
        "🏠 Overview",
        "👤 Patient Profile",
        "📡 Assessment",
        "🧠 AI Analysis",
        "🧬 Digital Twin",
        "📋 Patient History"
    ]
    nav_labels = [t(x) for x in nav_options]

    default_index = nav_options.index(st.session_state.current_page)
    selected_label = st.radio(
        t("NAVIGATION"),
        nav_labels,
        index=default_index
    )
    selected_page = nav_options[nav_labels.index(selected_label)]
    if selected_page != st.session_state.current_page:
        st.session_state.current_page = selected_page
        st.session_state._scroll_to_top = True
        st.rerun()
    page = selected_page

    render_markdown("---")

    st.caption(t("SYSTEM STATUS"))

    render_markdown("<div class='status-row'>🟢 <span>AI Engine — Ready</span></div>", unsafe_allow_html=True)
    render_markdown("<div class='status-row'>🟢 <span>Joint Signal Sensor — Connected</span></div>", unsafe_allow_html=True)
    render_markdown("<div class='status-row'>🟢 <span>IMU Module — Connected</span></div>", unsafe_allow_html=True)
    render_markdown("<div class='status-row'>🟢 <span>Local Database — Ready</span></div>", unsafe_allow_html=True)

    render_markdown("---")

    st.caption(t("DEPLOYMENT"))

    render_markdown("📍 NER / Rural Healthcare")
    render_markdown("📡 Offline-ready architecture")
    render_markdown("🔐 Secure patient records")

    render_markdown("---")

    st.caption(t("ArthroSonic Prototype • SIH 2026"))


# ============================================================
# PAGE 1 — OVERVIEW
# ============================================================

if page == "🏠 Overview":

    page_header(
        "AI-Assisted Osteoarthritis Screening",
        "Portable multimodal assessment platform for early OA risk identification"
    )

    # Hero

    render_markdown(
        """
        <div class="hero-box">

            <div style="font-size:13px;font-weight:800;
                        letter-spacing:1px;color:#2563eb;">
                ARTHROSONIC • FIELD SCREENING PLATFORM
            </div>

            <h1 style="font-size:36px;margin-top:12px;">
                Turning joint signals into
                <span style="color:#2563eb;">
                actionable risk markers.
                </span>
            </h1>

            <p style="font-size:17px;max-width:850px;line-height:1.7;">
                ArthroSonic combines joint sound emissions,
                movement analysis, patient-reported symptoms and
                longitudinal data to support preliminary
                osteoarthritis risk screening in low-resource
                healthcare environments.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    render_markdown(
        "<div class='section-title'>Live System Overview</div>",
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card(
            "ACTIVE PATIENT",
            "AS-2026-0147",
            "Assessment ready"
        )

    with c2:
        metric_card(
            "SENSOR STATUS",
            "ONLINE",
            "PZT + Microphone + IMU"
        )

    with c3:
        metric_card(
            "SIGNAL QUALITY",
            "94%",
            "Suitable for analysis"
        )

    with c4:
        metric_card(
            "ASSESSMENT MODE",
            "MULTIMODAL",
            "PZT + microphone + gait + symptoms"
        )

    # Visual area

    render_markdown(
        "<div class='section-title'>Multimodal Patient Profile</div>",
        unsafe_allow_html=True
    )

    left, right = st.columns([1.1, 1])

    with left:

        render_markdown(
            """
            <div class="card">

                <div style="display:flex;
                            justify-content:space-between;
                            align-items:center;">

                    <div>
                        <div style="font-size:12px;
                                    font-weight:800;
                                    color:#667085;">
                            CURRENT SCREENING
                        </div>

                        <h2 style="margin:5px 0;">
                            OA-associated risk markers
                        </h2>
                    </div>

                    <span class="status-chip status-yellow">
                        DEMO OUTPUT
                    </span>

                </div>

                <div style="font-size:52px;
                            font-weight:900;
                            color:#b54708;
                            margin-top:20px;">
                    MODERATE
                </div>

                <p>
                    Prototype multimodal analysis indicates
                    a moderate level of OA-associated markers.
                </p>

            </div>
            """,
            unsafe_allow_html=True
        )

        render_markdown("<br>", unsafe_allow_html=True)

        fig = acoustic_waveform(270)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with right:

        render_markdown(
            """
            <div class="twin-box">

                <div style="text-align:center;">

                    <div style="font-size:12px;
                                font-weight:800;
                                letter-spacing:1px;
                                color:#667085;">
                        OA HUMAN DIGITAL TWIN
                    </div>

                    <div style="font-size:80px;
                                margin-top:25px;">
                        🧍
                    </div>

                    <div style="font-size:45px;
                                margin-top:-25px;">
                        🦿
                    </div>

                    <h2>Patient Movement State</h2>

                    <p>
                        Longitudinal representation of
                        movement, sound-pattern and symptom
                        characteristics.
                    </p>

                </div>

                <hr>

                <div style="display:flex;
                            justify-content:space-around;
                            text-align:center;">

                    <div>
                        <b>108°</b><br>
                        <small>Knee ROM</small>
                    </div>

                    <div>
                        <b>81%</b><br>
                        <small>Symmetry</small>
                    </div>

                    <div>
                        <b>0.84</b><br>
                        <small>Gait m/s</small>
                    </div>

                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    # Workflow

    render_markdown(
        "<div class='section-title'>Screening Workflow</div>",
        unsafe_allow_html=True
    )

    w1, w2, w3, w4 = st.columns(4)

    workflow = [
        ("01", "Patient Profile", "Symptoms + history"),
        ("02", "Sensor Capture", "Joint sound + movement"),
        ("03", "AI Fusion", "Feature extraction"),
        ("04", "Risk Report", "Personalized output")
    ]

    for col, (num, title, desc) in zip(
        [w1, w2, w3, w4],
        workflow
    ):

        with col:

            render_markdown(
                f"""
                <div class="metric-card">

                    <div style="font-size:12px;
                                color:#2563eb;
                                font-weight:900;">
                        STEP {num}
                    </div>

                    <h3 style="margin:8px 0;">
                        {title}
                    </h3>

                    <div class="metric-small">
                        {desc}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )


    next_button("👤 Patient Profile", "START PATIENT PROFILE →")

# ============================================================
# PAGE 2 — PATIENT PROFILE
# ============================================================

elif page == "👤 Patient Profile":

    page_header(
        "Patient Profile",
        "Create or reconnect a patient record before assessment"
    )

    render_markdown("<div class='section-title'>1. Patient Information</div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        name = st.text_input(t("Full Name"), st.session_state.patient_name)
    with c2:
        age = st.number_input(t("Age"), 18, 100, int(st.session_state.patient_age))
    with c3:
        sex = st.selectbox(t("Sex"), [t("Female"), t("Male"), t("Other")])

    c1, c2, c3 = st.columns(3)
    with c1:
        location = st.text_input(t("Location"), st.session_state.patient_location)
    with c2:
        occupation = st.text_input(t("Occupation"), st.session_state.patient_occupation)
    with c3:
        activity = st.selectbox(t("Physical Activity"), [t("Low"), t("Moderate"), t("High")], index=1)

    c1, c2 = st.columns(2)
    with c1:
        phone = st.text_input(t("Phone Number"), st.session_state.patient_phone, placeholder=t("e.g. +91 98765 43210"))
    with c2:
        address = st.text_area(t("Address"), st.session_state.patient_address, height=90, placeholder=t("House / village / town / district / state"))

    render_markdown("<div class='section-title'>2. Connect Patient Record</div>", unsafe_allow_html=True)
    st.info(t("Confirm the identity first. ArthroSonic can then reconnect the current assessment with previous screening records available in the prototype session."))
    connect_col, save_col = st.columns([2, 1])
    with connect_col:
        connect_previous = st.checkbox(t("Connect to previous patient data"), value=st.session_state.previous_data_connected)
    with save_col:
        if st.button("✓ " + t("CONFIRM PATIENT"), type="primary", use_container_width=True):
            st.session_state.patient_name = name
            st.session_state.patient_age = age
            st.session_state.patient_sex = sex
            st.session_state.patient_location = location
            st.session_state.patient_occupation = occupation
            st.session_state.patient_activity = activity
            st.session_state.patient_phone = phone
            st.session_state.patient_address = address
            st.session_state.profile_confirmed = True
            st.session_state.previous_data_connected = connect_previous
            st.success(f"{t('Patient Profile')}: {name} ✓")

    if st.session_state.profile_confirmed:
        render_markdown("<div class='card'><b>✓ Patient record confirmed</b><br>Current screening can now be linked with the patient's longitudinal record.</div>", unsafe_allow_html=True)

        render_markdown("<div class='section-title'>3. Latest Reports & Medical Documents</div>", unsafe_allow_html=True)
        st.write(t("Upload any recent reports that may help the healthcare worker review the patient's history. These can include X-rays, MRI scans, CT scans, ultrasound reports, blood work, prescriptions, or other relevant documents."))
        uploads = st.file_uploader(
            t("Upload latest reports"),
            type=["pdf", "png", "jpg", "jpeg", "webp", "doc", "docx", "xls", "xlsx", "csv"],
            accept_multiple_files=True,
            help=t("Prototype only: files are available during the current app session.")
        )
        if uploads:
            st.session_state.uploaded_reports = [f.name for f in uploads]
        if st.session_state.uploaded_reports:
            st.markdown("**" + t("Attached for this assessment:") + "**")
            for filename in st.session_state.uploaded_reports:
                st.markdown(f"- 📎 {filename}")

        render_markdown("<div class='section-title'>4. OA Risk Factors & Symptoms</div>", unsafe_allow_html=True)
        r1, r2, r3 = st.columns(3)
        with r1:
            injury = st.selectbox(t("Previous Knee Injury"), [t("No"), t("Yes")])
        with r2:
            family = st.selectbox(t("Family History of OA"), [t("No"), t("Yes")])
        with r3:
            terrain = st.selectbox(t("Terrain Exposure"), [t("Low"), t("Moderate"), t("High")])

        s1, s2, s3 = st.columns(3)
        with s1:
            pain = st.slider(t("Pain Level"), 0, 10, 5)
        with s2:
            stiffness = st.slider(t("Stiffness"), 0, 10, 4)
        with s3:
            mobility = st.slider(t("Mobility Difficulty"), 0, 10, 4)

        # ArthroSonic is specifically a knee-screening system; there is no joint selector.
        render_markdown("<div class='card'><b>🦵 KNEE-ONLY SCREENING</b><br>The ArthroSonic prototype measures the <b>knee joint only</b>. The screening site is fixed and cannot be changed.</div>", unsafe_allow_html=True)
        st.session_state.joint_screened = "Knee"
        next_button("📡 Assessment", "SAVE & CONTINUE TO ASSESSMENT →")
    else:
        st.warning(t("Confirm the patient record to unlock document upload and the next step."))


# ============================================================
# PAGE 3 — SENSOR ASSESSMENT
# ============================================================

elif page == "📡 Assessment":

    page_header(
        "Sensor Assessment",
        "Guided acquisition of joint sound and movement signals"
    )

    render_markdown("<div class='card'><b>🦵 SCREENING SITE: KNEE ONLY</b><br>ArthroSonic is configured specifically for knee assessment. The screening joint is fixed and cannot be changed.</div>", unsafe_allow_html=True)

    render_markdown(
        f"""
        <div class="card">

            <b>ACTIVE PATIENT</b>

            <span style="margin-left:15px;
                         font-size:20px;
                         font-weight:800;">
                {st.session_state.patient_id}
            </span>

            <span class="status-chip status-green"
                  style="float:right;">
                READY
            </span>

        </div>
        """,
        unsafe_allow_html=True
    )

    render_markdown(
        "<div class='section-title'>Sensor Network</div>",
        unsafe_allow_html=True
    )

    a, b, c, d = st.columns(4)

    with a:
        metric_card(
            "PZT + MICROPHONE",
            "● ONLINE",
            "Knee vibration + joint sound"
        )

    with b:
        metric_card(
            "IMU / GAIT",
            "● ONLINE",
            "Movement + posture + gait"
        )

    with c:
        metric_card(
            "CAMERA",
            "● READY",
            "Gait assessment"
        )

    with d:
        metric_card(
            "SIGNAL QUALITY",
            "94%",
            "Excellent acquisition"
        )

    # Assessment steps

    render_markdown(
        "<div class='section-title'>Guided Assessment Protocol</div>",
        unsafe_allow_html=True
    )

    p1, p2, p3 = st.columns(3)

    with p1:

        render_markdown(
            """
            <div class="card">

                <div style="font-size:35px;">🎧</div>

                <h3>01 · Joint Signal</h3>

                <p>
                    Place the PZT and microphone module over the
                    knee joint and perform controlled
                    flexion-extension movements.
                </p>

                <span class="status-chip status-green">
                    READY
                </span>

            </div>
            """,
            unsafe_allow_html=True
        )

    with p2:

        render_markdown(
            """
            <div class="card">

                <div style="font-size:35px;">🚶</div>

                <h3>02 · Movement</h3>

                <p>
                    Capture knee movement, gait,
                    range of motion and left-right
                    movement symmetry.
                </p>

                <span class="status-chip status-blue">
                    READY
                </span>

            </div>
            """,
            unsafe_allow_html=True
        )

    with p3:

        render_markdown(
            """
            <div class="card">

                <div style="font-size:35px;">📝</div>

                <h3>03 · Symptoms</h3>

                <p>
                    Combine patient-reported pain,
                    stiffness, mobility and relevant
                    risk factors.
                </p>

                <span class="status-chip status-blue">
                    READY
                </span>

            </div>
            """,
            unsafe_allow_html=True
        )

    render_markdown(
        "<div class='section-title'>Joint Signal Acquisition</div>",
        unsafe_allow_html=True
    )

    if st.button(
        "🔴 " + t("START SENSOR RECORDING"),
        type="primary",
        use_container_width=True
    ):

        progress = st.progress(0)

        import time as tm

        for i in range(101):

            progress.progress(i)

            tm.sleep(0.008)

        st.session_state.recording_complete = True

        st.success(
            t("Joint-signal and movement sequence captured successfully.")
        )

    if st.session_state.recording_complete:

        render_markdown(
            """
            <div class="card">

                <div style="display:flex;
                            justify-content:space-between;">

                    <div>
                        <h3>✓ Acquisition Complete</h3>

                        <p>
                            Signal quality is suitable for
                            feature extraction and prototype
                            AI analysis.
                        </p>
                    </div>

                    <div style="font-size:42px;">
                        📡
                    </div>

                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        render_markdown(
            "<div class='section-title'>Live Joint Signal</div>",
            unsafe_allow_html=True
        )

        st.plotly_chart(
            acoustic_waveform(350),
            use_container_width=True
        )

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            metric_card(
                "DURATION",
                "10.4 s",
                "Recording"
            )

        with c2:
            metric_card(
                "EVENTS",
                "17",
                "Detected sound events"
            )

        with c3:
            metric_card(
                "SAMPLING",
                "16 kHz",
                "Acquisition rate"
            )

        with c4:
            metric_card(
                "QUALITY",
                "94%",
                "Signal quality index"
            )

        render_markdown(
            "<div class='section-title'>Time-Frequency Analysis</div>",
            unsafe_allow_html=True
        )

        st.plotly_chart(
            create_spectrogram(),
            use_container_width=True
        )

        if st.button(
            "🧠 " + t("RUN MULTIMODAL AI ANALYSIS"),
            type="primary",
            use_container_width=True
        ):

            st.session_state.analysis_generated = True

            st.success(
                t("Prototype multimodal analysis completed.")
            )


    if st.session_state.recording_complete:
        next_button("🧠 AI Analysis", "CONTINUE TO AI ANALYSIS →")

# ============================================================
# PAGE 4 — AI ANALYSIS
# ============================================================

elif page == "🧠 AI Analysis":

    page_header(
        "AI Risk Analysis",
        "Screening grade, risk markers and supporting assessment findings"
    )

    score = int(st.session_state.risk_score)
    grade, level, simple_words = risk_grade(score)

    render_markdown(
        """
        <div class="card">
            <span class="status-chip status-yellow">PROTOTYPE / SIMULATED AI OUTPUT</span>
            <p style="margin-top:12px;">This page presents a preliminary screening interpretation for demonstration. It does not establish a medical diagnosis.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    render_markdown("<div class='section-title'>Screening Grade</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1.2, 1, 1])
    with c1:
        risk_class = "risk-moderate" if grade == 2 else "card"
        render_markdown(f"""
        <div class="{risk_class}">
            <div style="font-size:12px;font-weight:800;letter-spacing:1px;">OA-ASSOCIATED RISK MARKERS</div>
            <div class="risk-score">GRADE {grade}</div>
            <div style="font-size:20px;font-weight:800;margin-top:8px;">{level} RISK</div>
            <div style="margin-top:10px;">{simple_words}</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        metric_card("OA-ASSOCIATED RISK SCORE", f"{score} / 100", "Prototype screening index")
    with c3:
        metric_card("DATA QUALITY", "94%", "Good input quality; not OA probability")

    render_markdown("<div class='section-title'>What Do the Grades Mean?</div>", unsafe_allow_html=True)
    grade_df = pd.DataFrame({
        "GRADE": ["Grade 1", "Grade 2", "Grade 3"],
        "RISK LEVEL": ["LOW", "MEDIUM", "HIGH"],
        "IN SIMPLE WORDS": [
            "Few OA-related risk markers detected.",
            "Some OA-related risk markers detected.",
            "More OA-related risk markers detected."
        ]
    })
    st.dataframe(localize_df(grade_df), use_container_width=True, hide_index=True)
    st.caption(t("Grades describe screening risk only. They do not confirm OA or show the amount of joint damage. Grade boundaries must be defined and validated for the AI model."))

    render_markdown("<div class='section-title'>What Did the System Find?</div>", unsafe_allow_html=True)
    detail = pd.DataFrame({
        "SCREENING DETAIL": ["OA-related risk markers", "Data quality", "Sound patterns detected"],
        "RESULT": [level.title(), "94% — Good", "17"],
        "WHAT IT MEANS": [simple_words, "The system captured the input clearly; this is not the chance of having OA.", "Patterns picked up during screening."]
    })
    st.dataframe(localize_df(detail), use_container_width=True, hide_index=True)

    render_markdown("<div class='section-title'>Movement & Patient-Reported Findings</div>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    for col, label, value, small in [
        (m1, "KNEE ROM", "108°", "Movement range"),
        (m2, "GAIT SYMMETRY", "81%", "Left-right symmetry"),
        (m3, "PAIN", "6 / 10", "Patient reported"),
        (m4, "STIFFNESS", "4 / 10", "Patient reported"),
    ]:
        with col:
            metric_card(label, value, small)

    render_markdown("<div class='section-title'>Joint Signal Analysis</div>", unsafe_allow_html=True)
    left, right = st.columns(2)
    with left:
        st.plotly_chart(acoustic_waveform(340), use_container_width=True)
    with right:
        st.plotly_chart(create_spectrogram(), use_container_width=True)

    render_markdown("<div class='section-title'>Explainable Screening Factors</div>", unsafe_allow_html=True)
    factors = [
        ("🔊", "Sound + vibration events", "17 patterns detected during the prototype movement sequence."),
        ("🚶", "Movement symmetry", "Mild left-right movement asymmetry is present in the demonstration profile."),
        ("🦿", "Range of motion", "The recorded knee range of motion is 108° in the demonstration profile."),
        ("📝", "Reported symptoms", "Pain and stiffness inputs contribute to the multimodal screening profile."),
    ]
    cols = st.columns(4)
    for col, (icon, title_txt, desc) in zip(cols, factors):
        with col:
            render_markdown(f"<div class='card'><div style='font-size:30px'>{icon}</div><h3>{title_txt}</h3><p>{desc}</p></div>", unsafe_allow_html=True)

    render_markdown("<div class='section-title'>Longitudinal Risk Monitoring</div>", unsafe_allow_html=True)
    _trend_months = {
        "en": ["Jan 2026", "Apr 2026", "Jul 2026", "Sep 2026"],
        "hi": ["जन 2026", "अप्रै 2026", "जुल 2026", "सितं 2026"],
        "as": ["জানু 2026", "এপ্ৰিল 2026", "জুলাই 2026", "ছেপ্টে 2026"],
        "bn": ["জানু 2026", "এপ্রিল 2026", "জুলাই 2026", "সেপ্টে 2026"],
        "ne": ["जन 2026", "अप्रिल 2026", "जुल 2026", "सेप्टे 2026"],
    }
    dates = _trend_months.get(current_language(), _trend_months["en"])
    risk = [38, 44, 56, score]
    trend = go.Figure(go.Scatter(x=dates, y=risk, mode="lines+markers", line=dict(width=4), name=t("Risk Index")))
    trend.update_layout(height=330, template="plotly_white", yaxis=dict(range=[0,100], title=t("Risk Index")), xaxis_title=t("Assessment Date"))
    st.plotly_chart(trend, use_container_width=True)

    render_markdown("<div class='section-title'>What Does This Mean for You?</div>", unsafe_allow_html=True)
    meaning = {
        1: "Your result is Grade 1 (Low Risk). This does not mean you definitely do not have osteoarthritis. It means the system found few OA-related risk markers. If you have joint pain, stiffness, swelling, or trouble moving, share this with a doctor.",
        2: "Your result is Grade 2 (Medium Risk). This does not mean you definitely have osteoarthritis. It means the system found some signs that may need further checking. If you have joint pain, stiffness, swelling, or trouble moving, share this with a doctor.",
        3: "Your result is Grade 3 (High Risk). This does not mean you definitely have osteoarthritis. It means the system found more OA-related risk markers that may need further checking. If you have joint pain, stiffness, swelling, or trouble moving, share this with a doctor."
    }[grade]
    render_markdown(f"<div class='card'>{meaning}</div>", unsafe_allow_html=True)

    st.info(t("Predictive screening only. This system does not diagnose OA or prescribe treatment."))

    pdf = generate_pdf()
    st.download_button("📄 " + t("DOWNLOAD SCREENING REPORT"), data=pdf, file_name=f"ArthroSonic_Report_{st.session_state.patient_id}.pdf", mime="application/pdf", type="primary", use_container_width=True)
    next_button("🧬 Digital Twin", "CONTINUE TO OA HUMAN DIGITAL TWIN →")


# ============================================================
# PAGE 5 — DIGITAL TWIN
# ============================================================

elif page == "🧬 Digital Twin":

    page_header(
        "OA Human Digital Twin",
        "Longitudinal digital representation of patient-specific OA-related characteristics"
    )

    render_markdown(
        """
        <div class="hero-box">

            <div style="font-size:12px;
                        font-weight:800;
                        letter-spacing:1px;
                        color:#2563eb;">
                PATIENT DIGITAL REPRESENTATION
            </div>

            <h1>
                From one-time screening
                to longitudinal monitoring.
            </h1>

            <p style="max-width:850px;
                      font-size:17px;
                      line-height:1.7;">
                The ArthroSonic Digital Twin organizes sound,
                movement, symptom and contextual measurements
                into a patient-specific longitudinal profile.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    render_markdown(
        "<div class='section-title'>Patient Twin State</div>",
        unsafe_allow_html=True
    )

    left, right = st.columns([1, 1.5])

    with left:

        render_markdown(
            """
            <div class="twin-box">

                <div style="text-align:center;">

                    <div style="font-size:12px;
                                font-weight:800;
                                color:#667085;">
                        DIGITAL PATIENT MODEL
                    </div>

                    <div style="font-size:115px;
                                margin-top:25px;">
                        🧍
                    </div>

                    <div style="font-size:65px;
                                margin-top:-45px;">
                        🦿
                    </div>

                    <h2>Right Knee Profile</h2>

                    <span class="status-chip status-yellow">
                        MODERATE MARKER STATE
                    </span>

                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with right:

        render_markdown(
            """
            <div class="card">

                <h3>Patient-Specific State Variables</h3>

                <p>
                    These variables form the current
                    demonstration state of the digital twin.
                </p>

            </div>
            """,
            unsafe_allow_html=True
        )

        metrics = [
            ("Knee Sound + Vibration Signature", "17 events"),
            ("Knee Range of Motion", "108°"),
            ("Gait Symmetry", "81%"),
            ("Reported Pain", "6 / 10"),
            ("Gait Speed", "0.84 m/s"),
            ("Signal Quality", "94%")
        ]

        for label, value in metrics:

            c1, c2 = st.columns([2, 1])

            with c1:
                st.write(f"**{t(label)}**")

            with c2:
                st.write(f"**{value}**")

    render_markdown(
        "<div class='section-title'>Digital Twin Timeline</div>",
        unsafe_allow_html=True
    )

    timeline = [
        (
            "12 JAN 2026",
            "Baseline Assessment",
            "Initial patient movement and joint-signal profile recorded."
        ),
        (
            "18 APR 2026",
            "Follow-up Assessment",
            "Longitudinal measurements added to patient profile."
        ),
        (
            "20 JUL 2026",
            "Movement Assessment",
            "Updated gait and knee movement characteristics."
        ),
        (
            "18 SEP 2026",
            "Current Assessment",
            "Latest multimodal screening profile generated."
        )
    ]

    for date, title, desc in timeline:

        render_markdown(
            f"""
            <div class="timeline-item">

                <div class="timeline-date">
                    {date}
                </div>

                <div class="timeline-title">
                    {title}
                </div>

                <div>
                    {desc}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    render_markdown(
        "<div class='section-title'>Why a Digital Twin?</div>",
        unsafe_allow_html=True
    )

    d1, d2, d3 = st.columns(3)

    twin_features = [
        (
            "📈",
            "Longitudinal",
            "Compare future measurements against the patient's own baseline."
        ),
        (
            "🔄",
            "Multimodal",
            "Combine sound, movement and symptom information."
        ),
        (
            "🧠",
            "Personalized",
            "Represent patient-specific characteristics rather than relying only on population averages."
        )
    ]

    for col, (icon, title, desc) in zip(
        [d1, d2, d3],
        twin_features
    ):

        with col:

            render_markdown(
                f"""
                <div class="card">

                    <div style="font-size:35px;">
                        {icon}
                    </div>

                    <h3>{title}</h3>

                    <p>{desc}</p>

                </div>
                """,
                unsafe_allow_html=True
            )


    next_button("📋 Patient History", "VIEW PATIENT HISTORY →")

# ============================================================
# PAGE 6 — HISTORY
# ============================================================

elif page == "📋 Patient History":

    page_header(
        "Patient History",
        "Longitudinal screening records and personalized baseline tracking"
    )

    render_markdown(
        f"""
        <div class="card">

            <div style="font-size:12px;
                        font-weight:800;
                        color:#667085;">
                PATIENT RECORD
            </div>

            <h2>
                {st.session_state.patient_id}
            </h2>

            <p>
                Ananya Sharma • Assam, North Eastern Region
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    render_markdown(
        "<div class='section-title'>Previous Assessments</div>",
        unsafe_allow_html=True
    )

    history = pd.DataFrame({
        "Date": [
            "12 Jan 2026",
            "18 Apr 2026",
            "20 Jul 2026",
            "18 Sep 2026"
        ],
        "Risk Markers": [
            "Low",
            "Low",
            "Moderate",
            "Moderate"
        ],
        "Risk Index": [
            38,
            44,
            56,
            67
        ],
        "Pain": [
            2,
            3,
            5,
            6
        ],
        "Sound Events": [
            9,
            11,
            15,
            17
        ],
        "Knee ROM": [
            "121°",
            "118°",
            "112°",
            "108°"
        ]
    })

    st.dataframe(
        localize_df(history),
        use_container_width=True,
        hide_index=True
    )

    render_markdown(
        "<div class='section-title'>Longitudinal Trends</div>",
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(2)

    with c1:

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=history["Date"],
                y=history["Risk Index"],
                mode="lines+markers",
                line=dict(width=4),
                name="Risk"
            )
        )

        fig.update_layout(
            title=t("Prototype Risk Index"),
            yaxis=dict(range=[0, 100]),
            height=350,
            template="plotly_white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with c2:

        fig2 = go.Figure()

        fig2.add_trace(
            go.Scatter(
                x=history["Date"],
                y=history["Sound Events"],
                mode="lines+markers",
                line=dict(width=4),
                name=t("Sound Events")
            )
        )

        fig2.update_layout(
            title=t("Sound Event Trend"),
            height=350,
            template="plotly_white"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

    render_markdown(
        "<div class='section-title'>Personalized Baseline</div>",
        unsafe_allow_html=True
    )

    b1, b2, b3, b4 = st.columns(4)

    with b1:
        metric_card(
            "BASELINE ROM",
            "121°",
            "Jan 2026"
        )

    with b2:
        metric_card(
            "CURRENT ROM",
            "108°",
            "Sep 2026"
        )

    with b3:
        metric_card(
            "BASELINE EVENTS",
            "9",
            "Jan 2026"
        )

    with b4:
        metric_card(
            "CURRENT EVENTS",
            "17",
            "Sep 2026"
        )

    render_markdown(
        "<div class='section-title'>Screening Interpretation</div>",
        unsafe_allow_html=True
    )

    render_markdown(
        """
        <div class="card">

            <h3>Longitudinal monitoring</h3>

            <p>
                ArthroSonic stores repeated screening measurements
                so that future assessments can be compared with
                the patient's own historical baseline.
            </p>

            <p>
                Changes in sound-pattern features, movement characteristics,
                symptoms and other recorded variables can therefore
                be visualized over time.
            </p>

            <span class="status-chip status-blue">
                PERSONALIZED MONITORING
            </span>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# FOOTER
# ============================================================

render_markdown(
    """
    <div class="footer">

        <b>ARTHROSONIC</b> • AI-Assisted OA Risk Screening • SIH 2026

        <br><br>

        Prototype for screening research and demonstration.
        Not a medical diagnostic system.

    </div>
    """,
    unsafe_allow_html=True
)

if st.session_state.pop("_scroll_to_top", False):
    scroll_to_top()
